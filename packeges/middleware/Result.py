import pandas as pd
from packeges.middleware import Ai_block

def create_lead_title(entry):
    if 'ФИО' in entry:
        return entry['ФИО'].strip()
    else:
        parts = [entry.get(part, '').strip() for part in ['Фамилия', 'Имя', 'Отчество']]
        return ' '.join(part for part in parts if part)

def get_phone_number(entry):
    if 'Мобильный телефон' in entry and entry['Мобильный телефон'].strip():
        return entry['Мобильный телефон'].strip()
    elif 'Телефон' in entry and entry['Телефон'].strip():
        return entry['Телефон'].strip()
    else:
        return ''
    
def output_res(res_list, interest_list, file_id):
    df = pd.DataFrame(res_list)
    df_res = pd.DataFrame()
    #df = df.map(lambda x: x.replace(' ', '') if isinstance(x, str) else x)
    interest_strings = [', '.join(item) if item else '' for item in interest_list] 
    df_res['Название лида'] = [create_lead_title(item) for item in res_list]
    df_res['Пол'] = Ai_block.chat_gender(df_res, 'Название лида')
    df_res['Дата рождения'] = df['Дата Рождения']
    df_res['Мобильный телефон'] = [get_phone_number(item) for item in res_list]
    df_res['Рабочий телефон'] = df['Телефон родителя']
    df_res['Частный e-mail'] = df['E-mail']
    try:
        df_res['ФИО отца'] = df['ФИО родителя']
    except KeyError:
        pass
    df_res['Телефон отца'] = df['Телефон родителя']
    df_res['Комментарий'] = interest_strings
    df_res['Источник'] = '8'
    df_res['Дополнительно об источнике'] = 'Университет'
    df_res['Тип анкетирования'] = 'Анкета / Questionnaire'
    df_res['Категория Анкеты'] = 'A1'

    df_res.dropna(how='all', inplace=True)
    output = df_res.to_excel(f'tmp/{file_id}/output.xlsx', index=False)
    return output