from config import exclude_values
from utility_functions import catch_errors


@catch_errors()
def lines_delete(df, sign_1c):
    
    df[sign_1c] = df[sign_1c].apply(lambda x: str(x))
    max_level = df['Уровень'].max()
    
    for i in range(max_level):
        df = df[~((df['Уровень']==i) & (df[sign_1c] == df[f'Level_{i}']) & (i<df['Уровень'].shift(-1)))]

    df = df[~df[sign_1c].isin(exclude_values)].copy()
    
    df[sign_1c] = df[sign_1c].astype(str)
    df = df[~df[sign_1c].str.contains('Итого')]
    df = df[df[['Дебет_начало',
                'Кредит_начало',
                'Дебет_оборот',
                'Кредит_оборот',
                'Дебет_конец',
                'Кредит_конец']].notna().any(axis=1)]
    df.rename(columns={'Счет': 'Субконто'}, inplace=True)
    df.drop('Уровень', axis=1, inplace=True)
    return df
