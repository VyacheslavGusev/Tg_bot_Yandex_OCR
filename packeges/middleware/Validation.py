import re
import os
import cv2
import json
import numpy as np
from Levenshtein import distance as levenshtein_distance
from boxdetect import config
from boxdetect.pipelines import get_checkboxes

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
                levenshtein_distance(normalize_string(merged_text), normalize_string(el)) <=1:
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

# Функция поиска чек боксов и разделения их на заполненные и незаполненные
def checkbox_detect(image_path):
    image = cv2.imread(image_path)
    height, width = image.shape[:2]

    cfg = config.PipelinesConfig()

    cfg.width_range = (25,87)
    cfg.height_range = (25,87)

    cfg.scaling_factors = [1.3]

    cfg.wh_ratio_range = (0.8, 1.2)


    cfg.group_size_range = (1, 1)

    cfg.dilation_iterations = 0

    checkboxes = get_checkboxes(
        image_path, cfg=cfg, px_threshold=0.2, plot=False, verbose=False)
    
    # определение конца сегмента для распознанного текста путем сравнения координат
    # чек боксов, стоящих на одной линии
    checkbox_coord = []

    for el in checkboxes:
        found = False
        for i in checkboxes:
            if el[0] != i[0]:
                if abs(int(el[0][1])/int(height)*100-int(i[0][1])/int(height)*100)<=1 and\
                int(el[0][0]) < int(i[0][0]):
                    coord = el[0] +(int(i[0][0]), int(height))
                    el = np.array([coord, el[1], el[2]], dtype=object)
                    checkbox_coord.append(el)
                    found = True
                    break
        if not found:
            coord = el[0] +(int(width), int(height))
            el = np.array([coord, el[1], el[2]], dtype=object)
            checkbox_coord.append(el)
                    
    # Разделение списков чек боксов на заполненные и незаполненные
    boxes = []
    checked_box = []

    for checkbox in checkbox_coord:
        boxes.append(checkbox[0])
        
    found = False
    for checkbox in checkbox_coord:
        if checkbox[1]:
            checked_box.append(checkbox[0])
            found = True
    if not found:
       checked_box.append((1,1,1,1,1,1))
        
    return boxes, checked_box

# Функция разделения списков заполненных чекбоксов на несколько
# в случае если на листе несколько анкет
def split_checkbox_list(data, checkbox_list, keyword):
    # Создаем список ключевых слов с координатами
    keywords = []

    for item in data:
        if item['text'].lower().strip() == keyword.lower().strip():
            keywords.append(item)

    # Проверяем, есть ли ключевые слова
    if not keywords:
        return []

    # Сортируем ключевые слова по координате Y начала
    sorted_keywords = sorted(keywords, key=lambda k: int(k['y_coord'][0]))

    # Если ключевое слово одно, создаем один диапазон до конца страницы
    if len(sorted_keywords) == 1:
        ranges = [(int(sorted_keywords[0]['y_coord'][1]), None)]
    else:
        # Получаем диапазоны между ключевыми словами
        ranges = [(int(sorted_keywords[i]['y_coord'][1]), int(sorted_keywords[i+1]['y_coord'][0]))
                  for i in range(len(sorted_keywords) - 1)]
        # Добавляем диапазон для последнего ключевого слова
        last_keyword = sorted_keywords[-1]
        ranges.append((int(last_keyword['y_coord'][1]), None))

    # Разделяем чекбоксы по диапазонам
    split_chbox_lists = [[] for _ in range(len(ranges))]
    
    for checkbox in checkbox_list:
        y_coord = checkbox[1]  # Y координата верхнего левого угла чекбокса
        
        for i, (start, end) in enumerate(ranges):
            if end is None:
                # Если это последний диапазон
                if y_coord > start:
                    split_chbox_lists[i].append(checkbox)
            else:
                if start < y_coord <= end:
                    split_chbox_lists[i].append(checkbox)
                    found = True
                    break
            

    return split_chbox_lists

# Функция заполнения слов по отмеченным чек-боксам
def check_box_extract_text(text_fields, checked_box):
    interest = []
    for el in checked_box:
        proc_string = ''
        for item in text_fields:
            # Прямое сравнение координат без индексации строки
            if abs(el[1]/el[5]*100 - int(item['y_coord'][0])/int(item['height'])*100) <= 1.2 and\
               el[0] < int(item['x_coord'][1]) < el[4]:
                proc_string += item['text'] + ' '
        # Добавляем proc_string в interest, если он не пустой
        if proc_string:
            interest.append(proc_string.rstrip(' '))
    return interest

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

    boxes_list = []
    checkbox_list = []
    for img in os.listdir(f'tmp/{file_id}/rotated'):
        image_path = os.path.join(f'tmp/{file_id}/rotated', img)  
        boxes, checked_box = checkbox_detect(image_path)
        boxes_list.append(boxes)
        checkbox_list.append(checked_box)

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

    splited_checkboxes = []
    for el, i in zip(proc_list, checkbox_list):
        split_cb = split_checkbox_list(el, i, 'анкета')
        for item in split_cb:
            splited_checkboxes.append(item)

    interest_list =[]
    for res, cb in zip(sublist, splited_checkboxes):
        interest_list.append(check_box_extract_text(res, cb))

    return res_list, interest_list
