from logger import logger
import pandas as pd

def revolutions_before_processing(df, file_excel, sign_1c):
    
    if df[df[sign_1c] == 'Итого'][['Дебет_начало', 'Кредит_начало', 'Дебет_оборот', 'Кредит_оборот', 'Дебет_конец', 'Кредит_конец']].empty:
        print('Нет строки ИТОГО в таблице, чтобы свериться!!!!!')
        return None
    else:
        df_for_check = df[df[sign_1c] == 'Итого'][[sign_1c,
                                                   'Дебет_начало', 
                                                   'Кредит_начало', 
                                                   'Дебет_оборот', 
                                                   'Кредит_оборот', 
                                                   'Дебет_конец', 
                                                   'Кредит_конец']].copy()
        
        df_for_check.fillna(0, inplace = True)
        df_for_check['Сальдо_начало_до_обработки'] = df_for_check['Дебет_начало'] - df_for_check['Кредит_начало']
        df_for_check['Сальдо_конец_до_обработки'] = df_for_check['Дебет_конец'] - df_for_check['Кредит_конец']
        df_for_check['Оборот_до_обработки'] = df_for_check['Дебет_оборот'] - df_for_check['Кредит_оборот']
        
        df_for_check = df_for_check[[
                                     'Сальдо_начало_до_обработки',
                                     'Оборот_до_обработки',
                                     'Сальдо_конец_до_обработки']].copy()
        df_for_check = df_for_check.reset_index(drop=True)

        logger.info(f'{file_excel}: сформировали таблицу с оборотами в разрезе счетов до обработки')

        return df_for_check

def revolutions_after_processing(df, df_for_check, file_excel):
    
    df_for_check_2 = pd.DataFrame()
    df_for_check_2['Сальдо_начало_после_обработки'] = [df['Дебет_начало'].sum() - df['Кредит_начало'].sum()]
    df_for_check_2['Оборот_после_обработки'] = [df['Дебет_оборот'].sum() - df['Кредит_оборот'].sum()]
    df_for_check_2['Сальдо_конец_после_обработки'] = [df['Дебет_конец'].sum() - df['Кредит_конец'].sum()]
    df_for_check_2 = df_for_check_2.reset_index(drop=True)

    # Объединение DataFrame с использованием внешнего соединения
    merged_df = pd.concat([df_for_check, df_for_check_2], axis=1)

    # Заполнение отсутствующих значений нулями
    merged_df = merged_df.infer_objects().fillna(0)

    # Вычисление разницы
    merged_df['Разница_сальдо_нач'] = merged_df['Сальдо_начало_до_обработки'] - merged_df['Сальдо_начало_после_обработки']
    merged_df['Разница_оборот'] = merged_df['Оборот_до_обработки'] - merged_df['Оборот_после_обработки']
    merged_df['Разница_сальдо_кон'] = merged_df['Сальдо_конец_до_обработки'] - merged_df['Сальдо_конец_после_обработки']
    
    merged_df['Разница_сальдо_нач'] = merged_df['Разница_сальдо_нач'].apply(lambda x: round(x))
    merged_df['Разница_оборот'] = merged_df['Разница_оборот'].apply(lambda x: round(x))
    merged_df['Разница_сальдо_кон'] = merged_df['Разница_сальдо_кон'].apply(lambda x: round(x))

    merged_df['Исх.файл'] = file_excel
    logger.info(f'{file_excel}: сформировали дополнительную таблицу с отклонениями до и после обработки')
    return merged_df
