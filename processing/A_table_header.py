"""
Обновляем наименования столбцов на корректные
"""

from settings import target_value
from logger import logger

sign_1c_upp = 'Субконто'
sign_1c_not_upp = 'Счет'
# Функция для обновления элементов списка


def table_header(df, file_excel):
    

    # получаем индекс строки, содержащей target_value (значение)
    index_for_columns = df.index[df.apply(lambda row: target_value in row.values, axis=1)][0]

    # устанавливаем заголовки
    df.columns = df.iloc[index_for_columns]
    
    number_debet = df.columns.to_list().index('Дебет')
    end_list = df.columns.to_list()[number_debet:]
    new_columns = df.loc[index_for_columns-1].to_list()[:number_debet] + end_list
    df.columns = new_columns[:]

    # имена столбцов (в т.ч. np.nan) преобразуем в строки
    df.columns = df.columns.map(str)

    # удаляем данные выше строки с именами столбцов таблицы (наименование отчета, период и т.д.)
    df.drop(df.index[0:(index_for_columns + 1)], inplace=True)
    
    

    # переименуем первые два столбца
    df.columns.values[0] = 'Уровень'
    logger.info(f'{file_excel}: успешно обновили шапку таблицы, удалили строки выше шапки')

    # удаляем пустые строки и столбцы
    df.dropna(axis=0, how='all', inplace=True)
    if 'nan' in df.columns.to_list():
        df.drop(columns=['nan'], inplace=True)
    logger.info(f'{file_excel}: удалили пустые строки и столбцы')
    
    col_0 = df.columns.to_list()
    
    counters = {'Дебет': 0, 'Кредит': 0}
    def update_account_list(item):
        if item in counters:
            # Увеличиваем счетчик для 'Дебет' или 'Кредит'
            counters[item] += 1
            # Возвращаем обновленное значение элемента
            return f"{item}_{['начало', 'оборот', 'конец'][counters[item] - 1]}"
        return item
    
    updated_list = [update_account_list(item) for item in col_0]
    df.columns = updated_list
    sign_1c = sign_1c_upp
    list_columns_necessary = ['Уровень', sign_1c, 'Вид связи КА за период', 'Дебет_начало', 'Кредит_начало', 'Дебет_оборот', 'Кредит_оборот', 'Дебет_конец', 'Кредит_конец'] # список необходимых столбцов
    list_columns_necessary_error = ['Уровень', sign_1c, 'Дебет_начало', 'Кредит_начало', 'Дебет_оборот', 'Кредит_оборот', 'Дебет_конец', 'Кредит_конец'] # список необходимых столбцов
    try:
        df = df[list_columns_necessary].copy()
    except KeyError as e:
        print('----------')
        print(e)
        print('----------')
        if 'Субконто' in e.args[0]:
            sign_1c = sign_1c_not_upp
            list_columns_necessary_error = ['Уровень', sign_1c, 'Дебет_начало', 'Кредит_начало', 'Дебет_оборот', 'Кредит_оборот', 'Дебет_конец', 'Кредит_конец'] # список необходимых столбцов
        df = df[list_columns_necessary_error].copy()
        print(f'\n{file_excel}: ОТСУТСТВУЕТ СТОЛБЕЦ Вид связи КА за период\n')
    
    return sign_1c
    
