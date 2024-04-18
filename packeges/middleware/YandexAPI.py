import os
import requests
import json
from packeges.middleware import Proc_image

from config import (
    folder_id,
    oauth_token
)

VISION_URL = 'https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText'
folder_id = folder_id

# Создаем ключ API, обращаемся к папке
def create_token(oauth_token):
    params = {'yandexPassportOauthToken': oauth_token}
    response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', params=params)
    decode_response = response.content.decode('UTF-8')
    text = json.loads(decode_response)
    iam_token = text.get('iamToken')

    return iam_token
  
def recognition_text(file_id):
    result = []
    for img in os.listdir(f'tmp/{file_id}/rotated'):
        image_path = os.path.join(f'tmp/{file_id}/rotated', img)
    
        # Заголовки запроса
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {create_token(oauth_token)}',
            'x-folder-id': folder_id,
            'x-data-logging-enabled': 'true'
        }

        body = {
            "mimeType": "image",
            "languageCodes": ["ru", "en"],  
            "model": "handwritten",
            "content": Proc_image.encode_file(image_path)
        }
   
        # Отправка POST-запроса
        response = requests.post(VISION_URL, headers=headers, json=body)
        result.append(response)
    return result
