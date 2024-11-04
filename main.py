import os
import threading
import time
import pandas as pd
from pyfiglet import Figlet

import config
from dialog_user import select_folder
from preprocessing_openpyxl import preprocessing_file_excel
from resaving_files import save_as_xlsx_not_alert
from analysis_deviations import revolutions_before_processing, revolutions_after_processing

from processing.A_table_header import table_header
from processing.B_handle_missing_values_in_account import handle_missing_values_in_account
from processing.C_horizontal_structure import horizontal_structure
from processing.F_lines_delete import lines_delete
from processing.G_shiftable_level import shiftable_level
from utility_functions import logger_with_spinner, print_with_spinner, spinner, terminate_script, delete_folders
from winreg_count import increment_run_count


# текст заставки
f1 = Figlet(font='ansi_shadow', justify="center")
f2 = Figlet(font='ansi_shadow', justify="center")

if increment_run_count():
    # вывод заставки и описания программы
    print_with_spinner('\n', f1.renderText("Flat table from"), f2.renderText("OSV 1C"))
    time.sleep(2)
    print_with_spinner(config.start_message)

    input('Для продолжения нажмите Enter')

    # индикатор выполнения программы
    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.daemon = True  # чтобы поток остановился, когда основной поток завершится
    spinner_thread.start()

    # выбор пользователем папки с обрабатываемыми файлами
    logger_with_spinner(f"Сейчас будет предложено выбрать папку с файлами Excel - анализами счетов.")
    time.sleep(2)
    select_folder()

    logger_with_spinner(f"Выбрана папка {config.folder_path}, проверим наличие файлов Excel...")

    # выгрузки из 1С УПП не загружаются в openpyxl без пересохранения Excel-ем
    # пересохраняем файлы
    save_as_xlsx_not_alert()
    files = os.listdir(config.folder_path_converted)
    excel_files = [file for file in files if (file.endswith('.xlsx') or file.endswith('.xls'))
                   and file != '_СВОД_ОСВ_счетов.xlsx']
    if not excel_files:
        terminate_script(f'Не найдены файлы Excel в папке {config.folder_path_converted}. Скрипт завершен неудачно')

    # Инициализируем пустой словарь, куда мы добавим обработанные таблицы каждой компании, затем объединим эти файлы в один.
    dict_df = {}  # для обрабатываемых таблиц
    dict_df_check = {}  # для таблиц сверки оборотов до и после обработки

    def main_process():
        empty_files = []

        for file_excel in excel_files:
            # предварительная обработка с помощью openpyxl (снятие объединения, уровни)
            folder_path_converted_file = os.path.normpath(os.path.join(config.folder_path_converted, file_excel))
            file_excel_treatment = preprocessing_file_excel(folder_path_converted_file)

            # загрузка в pandas
            df = pd.read_excel(file_excel_treatment)
            logger_with_spinner(f'{file_excel}: успешно загрузили в DataFrame')

            # устанавливаем шапку таблицы
            sign_1c, df = table_header(df, file_excel)
            logger_with_spinner(f'{file_excel}: успешно создали шапку таблицы')

            # если есть незаполненные поля группировки (вид номенклатуры например), ставим "не_заполнено"
            handle_missing_values_in_account(df, sign_1c)
            logger_with_spinner(f'{file_excel}: проверили незаполненные поля, при необходимости проставили "не заполнено"')


            # разносим иерархию в горизонтальную плоскость
            # если иерархии нет, то файл пустой, пропускаем его
            if horizontal_structure(df, file_excel, sign_1c):
                logger_with_spinner(f'{file_excel}: пустой, пропускаем его')
                empty_files.append(f'{file_excel}')
                continue
            else:
                logger_with_spinner(f'{file_excel}: разнесли иерархию в горизонтальную плоскость')

            # формируем вспомогательную таблицу с оборотами до обработки
            # потом сравним данные с итоговой таблицей, чтобы убедиться в правильности результата
            df_for_check = revolutions_before_processing(df, file_excel, sign_1c)

            logger_with_spinner(f'{file_excel}: сформировали вспомогательную таблицу с оборотами до обработки')
            if df_for_check.empty:
                  logger_with_spinner(f'{file_excel}: пустой, пропускаем его')
                  empty_files.append(f'{file_excel}')
                  continue

            # удаляем дублирующие строки (родительские счета, счета по которым есть аналитика, обороты, сальдо и т.д.)
            df = lines_delete(df, sign_1c)
            logger_with_spinner(f'{file_excel}: удалили дублирующие строки')

            # Сдвиг столбцов, чтобы субсчета располагались в одном столбце
            df = shiftable_level(df, file_excel, True)
            logger_with_spinner(f'{file_excel}: сдвинули столбцы, чтобы субсчета располагались в одном столбце')

            # формируем вспомогательную таблицу с оборотами после обработки
            # записываем данные по отклонениям до/после обработки
            df_check = revolutions_after_processing(df, df_for_check, file_excel)
            dict_df_check[file_excel] = df_check
            logger_with_spinner(f'{file_excel}: сформировали вспомогательную таблицу с оборотами после обработки')

            # запишем таблицу в словарь
            dict_df[file_excel] = df
            logger_with_spinner(f'{file_excel}: успешно записали таблицу в словарь для дальнейшего объединения с другими таблицами')

        # объединяем все таблицы в одну
        result, result_check = None, None
        try:
            result = pd.concat(list(dict_df.values()))
            logger_with_spinner('объединили все таблицы в одну')

            # Повторно сдвиг столбцов, чтобы субсчета располагались в одном столбце
            shiftable_level(result)
            logger_with_spinner('повторно сдвинули столбцы уже в сводной таблице, чтобы субсчета располагались в одном столбце')

            result_check = pd.concat(list(dict_df_check.values()))
            logger_with_spinner('объединили все таблицы с проверкой оборотов в одну')

            deviation_rpm = (result_check['Разница_сальдо_нач'] + result_check['Разница_оборот'] + result_check['Разница_сальдо_кон']).sum()
            if deviation_rpm < 1:
                logger_with_spinner('отклонения до и после обработки менее 1')
            else:
                logger_with_spinner('обнаружены существенные отклонения до и после обработки. См лист Сверка файла "_СВОД_ОСВ_счетов.xlsx"', warning_log=True)

            logger_with_spinner('Объединение завершено, пытаемся выгрузить файл в excel...')
        except Exception as e:
            terminate_script(f'Ошибка при объединении файлов {e}')
        # выгружаем в excel
        try:
            folder_path_summary_files = os.path.join(config.folder_path, "_СВОД_ОСВ_счетов.xlsx")
            with pd.ExcelWriter(folder_path_summary_files) as writer:
                result.to_excel(writer, sheet_name='Свод', index=False)
                result_check.to_excel(writer, sheet_name='Сверка', index=False)
            logger_with_spinner('Файл успешно выгружен в excel')
        except Exception as e:
            terminate_script(f'Ошибка при сохранении файла в excel: {e}')

        # удаляем папки с временными файлами
        delete_folders()

        if empty_files:
            logger_with_spinner(f'ОСВ счетов без оборотов ({len(empty_files)}): {empty_files}')

        logger_with_spinner('Скрипт завершен успешно. Можно закрыть программу.')

    if __name__ == "__main__":
        main_process()
        input()

else:
    logger_with_spinner('Попытки запуска исчерпаны. Можно закрыть программу.')
    input()