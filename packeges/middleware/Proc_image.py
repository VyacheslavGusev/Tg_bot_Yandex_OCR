import os
import cv2
import fitz
import base64
import numpy as np

# Разбираем PDF файл на страницы и переводим его в png, работает также и с изображениями
def file_to_png(file_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Открываем PDF файл
    pdf_document = fitz.open(file_path)

    # Проходим по всем страницам PDF и сохраняем их в формате PNG
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        image = page.get_pixmap()

        
        image.save(os.path.join(output_folder, f'img{page_number+1}.png'))
    # Закрываем PDF файл
    pdf_document.close()

# Кодировка файла в base 64
def encode_file(file):
  with open(file, 'rb') as file:
    file_content = file.read()
    return base64.b64encode(file_content).decode('UTF-8')

# Функции поворота изображения
def average_slope(lines):
    slopes = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            slope = np.arctan2(y2 - y1, x2 - x1) * (180 / np.pi)
            slopes.append(slope)
    # Фильтруем вертикальные линии, которые имеют угол ~90 или ~-90 градусов
    slopes = [slope for slope in slopes if not np.isclose(abs(slope), 90, atol=10)]
    return np.mean(slopes) if len(slopes) > 0 else 0

def rotate_image(image_path, rotate_folder):

    # Создание папки, если она не существует
    if not os.path.exists(rotate_folder):
        os.makedirs(rotate_folder)
    # Загрузка изображения
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Обнаружение краев на изображении
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Обнаружение линий на изображении
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)

    # Вычисление среднего угла наклона линий
    angle = average_slope(lines)

    # Получение размеров изображения
    (h, w) = img.shape[:2]

    # Вычисление центра изображения
    center = (w // 2, h // 2)

    # Применение поворота
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Формирование уникального имени файла для каждого фрагмента
    output_path = os.path.join(rotate_folder, f'rotated_{os.path.splitext(os.path.basename(image_path))[0]}.jpg')

    # Сохранение результата
    cv2.imwrite(output_path, rotated)