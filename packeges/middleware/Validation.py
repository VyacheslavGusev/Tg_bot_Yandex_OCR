import re
import json
import pandas as pd
from Levenshtein import distance as levenshtein_distance

def read_json(result):
    proc_list = []

    for res in result:
        data = json.loads(res.content.decode('UTF-8'))
        elenco= []
        for block in data["result"]["textAnnotation"]["blocks"]:
            width = data["result"]["textAnnotation"]["width"]  # Получаем ширину
            height = data["result"]["textAnnotation"]["height"]  # Получаем высоту
            for line in block['lines']:
                for word in line['words']:
                    text = word['text']
                    x_coord = [(vertex['x']) for vertex in word['boundingBox']['vertices']]
                    y_coord = [(vertex['y']) for vertex in word['boundingBox']['vertices']]
                    elenco.append({"text": text, "x_coord": x_coord, "y_coord": y_coord, "width": width, "height": height})
        proc_list.append(elenco)
    return proc_list

# Функция для разделения списка словарей на отдельные словари анкет по ключевому слову
def split_on_keyword(data, keyword):
    result = []
    current_list = []

    for item in data:
        if item['text'].lower().strip() == keyword:
            if current_list:
                result.append(current_list)
            current_list = [item]
        else:
            current_list.append(item)
    
    # Добавляем последний список, если он не пустой
    if current_list:
        result.append(current_list)

    return result

# Функция нормализации строки для поиска ключей в анкете
def normalize_string(string):
    # Удаляем все неалфавитные символы и приводим строку к нижнему регистру
    return re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', string).lower()


# Функция объединения текстовых полей и поиска уникальных ключей, содержащихся в распозноваемой анкете
def merge_texts(sublist, field_list):
    new_list = []
    miss_next = False
    found_next = False
    for i in range(0, len(sublist) - 1):
        if miss_next:
            miss_next = False
            continue
        found = False
        merged_text = sublist[i]['text'] + ' ' + sublist[i + 1]['text']
        for el in field_list:
            if normalize_string(merged_text) in normalize_string(el) or\
                levenshtein_distance(normalize_string(merged_text),normalize_string(el))<=1:
                new_dict = {
                    'text': merged_text,
                    'x_coord': sublist[i + 1]['x_coord'],
                    'y_coord': sublist[i + 1]['y_coord'],
                    'width': sublist[i + 1]['width'],
                    'height': sublist[i + 1]['height']
                }
                new_list.append(new_dict)
                found = True
                found_next = True
                miss_next = True
                break
            
        if not found:
            new_list.append(sublist[i])
    
    # Добавляем последний элемент, если он не был объединен
    if not miss_next and len(sublist) > 0:
        new_list.append(sublist[-1])
    
    # Если были найдены объединения, рекурсивно вызываем функцию с новым списком
    if found_next:
        return merge_texts(new_list, field_list)
    else:
        return new_list

# извлечение ключей и записи конца сегмента
# Функция получения ключей с координатами для дальнейшего разбора и поиска распознанного рукописного текста
def process_text_fields(spisok, field_list):
    ext_list = {}
    for item in spisok:
        for field in field_list:
            if levenshtein_distance(normalize_string(item['text']),normalize_string(field))<=1 or\
                normalize_string(item['text']) == normalize_string(field) and len(item['text']) >= 3:
                if field in ext_list:
                    continue
                else:
                    ext_list[field] = {
                                    'x_coord': item['x_coord'],
                                    'y_coord': item['y_coord'],
                                    'width': item['width'],
                                    'height': item['height']}
                    break

    # Находим окончание поля для рукописного текста
    for key in ext_list: 
        found = False
        for other_key in ext_list:
            if key != other_key:
                if abs(int(ext_list[key]['y_coord'][1])/int(ext_list[key]['height'])*100 - int(ext_list[other_key]['y_coord'][1])/int(ext_list[other_key]['height'])*100) <= 1.2 and\
                int(ext_list[key]['x_coord'][1])< int(ext_list[other_key]['x_coord'][1]):
                    ext_list[key]['end_segment'] = ext_list[other_key]['x_coord'][1]
                    found = True
                    break
        if not found:
            ext_list[key]['end_segment'] = ext_list[key]['width']
    
    # после того, как все ключи найдены и записаны в ext_list, формируем очищенный список значений filtred_spisok для дальнейшего разбора
    filtered_spisok = []

    for i in spisok:
        # Устанавливаем флаг, указывающий на необходимость удаления элемента
        remove_item = False
        # Перебираем ключи в ext_list
        for key in ext_list:
            # Проверяем условие, если текст элемента i входит в ключ key
            if normalize_string(i['text']) in normalize_string(key) and len(i['text']) >= 3:
                # Устанавливаем флаг, указывающий на необходимость удаления элемента
                remove_item = True
                break  # Если условие выполнено, выходим из внутреннего цикла
        # Если флаг не установлен, добавляем элемент в новый список
        if not remove_item:
            filtered_spisok.append(i)
    return ext_list, filtered_spisok

# Функция обработки распознанного текста и запись его в строку
def process_extract_text(text_fields, extracted_data):
    for key in extracted_data:
        proc_string = ''
        for item in text_fields:
            if abs(int(item['y_coord'][1])/int(item['height'])*100 - int(extracted_data[key]['y_coord'][1])/int(extracted_data[key]['height'])*100) <=1.2 and\
            int(extracted_data[key]['x_coord'][2]) < int(item['x_coord'][1]) < int(extracted_data[key]['end_segment'])-5:
                proc_string += item['text']+' ' 
        extracted_data[key]= proc_string

def output_res(proc_list, file_id):
    res_list = []
    field_list = [
        'Фамилия',
        'ФИО',
        'ФИО родителя',
        'Имя',
        'Отчество',
        'Дата Рождения',
        'E-mail',
        'Телефон',
        'Телефон родителя',
        'Мобильный телефон',
        'Город',
        'Хобби',
        'Регион',
        'Населенный пункт',
        'Адрес',
        'Паспорт',
        'Дата выдачи',
        'Название учебного заведения',
        'Школа/Колледж',
        'Курс\класс'
    ]

    sublist = []
    for el in proc_list:
        split_lists = split_on_keyword(el, 'анкета')
        for item in split_lists:
            sublist.append(item)
        
    for spisok in sublist:
        new_sublist = merge_texts(spisok,field_list)
        extracted_data, filtered_spisok = process_text_fields(new_sublist, field_list)
        process_extract_text(filtered_spisok, extracted_data)
        res_list.append(extracted_data)
    
        df = pd.DataFrame(res_list)
        output = df.to_excel(f'tmp/{file_id}/output.xlsx', index=False)
    return output