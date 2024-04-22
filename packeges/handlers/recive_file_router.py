import os
import shutil
from aiogram import Router, Bot, F
from aiogram.types import Message, FSInputFile
from packeges.middleware import Validation, YandexAPI, Proc_image



if not os.path.exists('tmp'):
    os.makedirs('tmp')

router = Router()
@router.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    await bot.download(
        message.photo[-1],
        destination=f"tmp/{message.photo[-1].file_id}.jpg")
    
    await message.answer("Файл получен, отправлен на распознание, подождите немного")

    file_path = f"tmp/{message.photo[-1].file_id}.jpg"
    output_images = f'tmp/{message.photo[-1].file_id}'
    Proc_image.file_to_png(file_path, output_images)
        
    rotate_folder = f'tmp/{message.photo[-1].file_id}/rotated'
    for img in os.listdir(output_images):
        image_path = os.path.join(output_images, img)
        Proc_image.rotate_image(image_path,rotate_folder)

    result = YandexAPI.recognition_text( message.photo[-1].file_id)
    proc_data = Validation.read_json(result)
    Validation.output_res(proc_data, message.photo[-1].file_id)

    doc_output = FSInputFile(f"tmp/{message.photo[-1].file_id}/output.xlsx")
    await message.answer_document(doc_output, 
                                  caption="Результат распознания")
    os.remove(f"tmp/{message.photo[-1].file_id}.jpg")
    shutil.rmtree(f'tmp/{message.photo[-1].file_id}')

@router.message(F.document)
async def download_document(message: Message, bot: Bot):
    await bot.download(message.document,
        destination=f"tmp/{message.document.file_id}.pdf")
    
    await message.answer("Файл получен, отправлен на распознание, подождите немного")

    file_path = f"tmp/{message.document.file_id}.pdf"
    output_images = f'tmp/{message.document.file_id}'
    Proc_image.file_to_png(file_path, output_images)
    
    rotate_folder = f'tmp/{message.document.file_id}/rotated'
    for img in os.listdir(output_images):
        image_path = os.path.join(output_images, img)
        Proc_image.rotate_image(image_path,rotate_folder)

    result = YandexAPI.recognition_text(message.document.file_id)
    proc_data = Validation.read_json(result)
    Validation.output_res(proc_data, message.document.file_id )
    
    doc_output = FSInputFile(f"tmp/{message.document.file_id}/output.xlsx")
    await message.answer_document(doc_output, 
                                  caption="Результат распознания")
    
    os.remove(f"tmp/{message.document.file_id}.pdf")
    shutil.rmtree(f"tmp/{message.document.file_id}")                                

    
  