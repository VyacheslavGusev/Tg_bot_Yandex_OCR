import re
import pandas as pd
from packeges.middleware import Ai_block



def create_lead_title(entry):
    if 'ФИО' in entry:  
        return entry['ФИО'].strip()
    # Иначе обрабатываем составные части
    else:
        parts = [entry.get(part, '').strip() for part in ['Фамилия', 'Имя', 'Отчество']]
        # Объединяем части, исключая пустые строки
        result = ' '.join(part for part in parts if part)
        return result
    
def get_phone_number(entry):
    if 'Мобильный телефон' in entry and entry['Мобильный телефон'].strip():
        return entry['Мобильный телефон'].strip()
    elif 'Телефон' in entry and entry['Телефон'].strip():
        return entry['Телефон'].strip()
    else:
        return ''
    
def validate_phone(phone_str):
    if pd.isna(phone_str):
        return None  # Если значение NaN, возвращаем None
    # Сначала проверяем, начинается ли значение с буквы
    if re.match(r'^[А-Яа-яA-Za-z]', phone_str):
        return None  # Если начинается с буквы, возвращаем None
    # Далее идет уже существующая логика поиска и валидации номера телефона
    return re.sub(r'^(\+?\d+(?:[\d\s]*\d)?)(?:\s+[А-Яа-яA-Za-z].*)?$', r'\1', phone_str)
    
def output_res(res_list, interest_list, file_id, id_request, compaign, ed_inst,\
                      name_ed_inst, date, city, address, responsible):
    df = pd.DataFrame(res_list)
    df_res = pd.DataFrame()
    interest_strings = [', '.join(item) if item else '' for item in interest_list] 
    df_res['Название лида'] = [create_lead_title(item) for item in res_list]
    df_res['Пол'] = Ai_block.chat_gender(df_res, 'Название лида')
    df_res['Дата рождения'] = df['Дата Рождения'].map(lambda x: x.replace(' ', '') if isinstance(x, str) else x)
    df_res['Мобильный телефон'] = [get_phone_number(item) for item in res_list]
    df_res['Мобильный телефон'] = df_res['Мобильный телефон'].apply(validate_phone).map(lambda x: x.replace(' ', '') if isinstance(x, str) else x)
    df_res['Рабочий телефон'] = df['Телефон родителя']
    df_res['Рабочий телефон'] = df['Телефон родителя'].apply(validate_phone).map(lambda x: x.replace(' ', '') if isinstance(x, str) else x)
    df_res['Частный e-mail'] = df['E-mail'].map(lambda x: x.replace(' ', '') if isinstance(x, str) else x)
    
    try:
        df_res['Уровень образования (Класс/курс)'] = df['Курс\класс']
    except KeyError:
        pass
    try:
        df_res['ФИО отца'] = df['ФИО родителя']
    except KeyError:
        pass
    df_res['Телефон отца'] = df['Телефон родителя'].apply(validate_phone).map(lambda x: x.replace(' ', '') if isinstance(x, str) else x)
    df_res['Комментарий'] = interest_strings
    df_res['ID заявки в SD'] = id_request
    df_res['Кампания (utm_campaign)'] = compaign
    df_res['Тип учебного заведения'] = ed_inst
    df_res['учебное заведение'] = name_ed_inst
    df_res['Дата анкетирования'] = date
    df_res['Город'] = city
    df_res['Город (IP)'] = city
    df_res['Адрес'] = address
    df_res['Ответственный'] = responsible
    df_res['Визуал'] = responsible
    df_res['Источник'] = '8'
    df_res['Дополнительно об источнике'] = 'Университет'
    df_res['Тип анкетирования'] = 'Анкета / Questionnaire'
    df_res['Категория Анкеты'] = 'A1'

    df_res.dropna(how='all', inplace=True)
    result = df.to_excel(f'tmp/{file_id}/result.xlsx', index=False)
    output = df_res.to_excel(f'tmp/{file_id}/output.xlsx', index=False)
    return output, result