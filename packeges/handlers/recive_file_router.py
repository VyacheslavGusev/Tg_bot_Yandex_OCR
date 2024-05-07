import os
import shutil
from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from packeges.middleware import Validation, YandexAPI, Proc_image, Result



if not os.path.exists('tmp'):
    os.makedirs('tmp')

router = Router()
@router.message(F.photo)
async def download_photo(message: Message, state: FSMContext, bot: Bot):
    await bot.get_file(
        message.photo[-1],
        destination=f"tmp/{message.photo[-1].file_id}.jpg")
    
    await message.answer("Файл получен, отправлен на распознание, подождите немного")

    data = await state.get_data()
    id_request = data.get('id_request')
    compaign = data.get('compaign')
    ed_inst = data.get('ed_inst')
    name_ed_inst = data.get('name_ed_inst')
    date = data.get('date')
    city = data.get('city')
    address = data.get('address')
    responsible = data.get('responsible')

    file_path = f"tmp/{message.photo[-1].file_id}.jpg"
    output_images = f'tmp/{message.photo[-1].file_id}'
    Proc_image.file_to_png(file_path, output_images)
        
    rotate_folder = f'tmp/{message.photo[-1].file_id}/rotated'
    for img in os.listdir(output_images):
        image_path = os.path.join(output_images, img)
        Proc_image.rotate_image(image_path,rotate_folder)

    result = YandexAPI.recognition_text( message.photo[-1].file_id)
    proc_data = Validation.read_json(result)
    res_list, interest_list = Validation.output_res(proc_data, message.photo[-1].file_id)
    Result.output_res(res_list, interest_list, message.photo[-1].file_id, id_request, compaign, ed_inst,\
                      name_ed_inst, date, city, address, responsible)
    doc_output = FSInputFile(f"tmp/{message.photo[-1].file_id}/output.xlsx")
    await message.answer_document(doc_output, 
                                  caption="Результат распознания")
    os.remove(f"tmp/{message.photo[-1].file_id}.jpg")
    shutil.rmtree(f'tmp/{message.photo[-1].file_id}')

@router.message(F.document)
async def download_document(message: Message, state: FSMContext, bot: Bot): 
    file = await bot.get_file(message.document.file_id)
    
    await message.answer("Файл получен, отправлен на распознание, подождите немного")

    data = await state.get_data()
    id_request = data.get('id_request')
    compaign = data.get('compaign')
    ed_inst = data.get('ed_inst')
    name_ed_inst = data.get('name_ed_inst')
    date = data.get('date')
    city = data.get('city')
    address = data.get('address')
    responsible = data.get('responsible')

    
    

    file_name = os.path.splitext(os.path.basename(file.file_path))[0]
    file_extension = os.path.splitext(os.path.basename(file.file_path))[1]
    file_path = f'/home/vyacheslav/Documents/GitHub/Tg_bot_OCR/bot_files/7042345812:AAGDBQzNpghb5u5eFlmKvKGBtTcapCTzkg0/documents/{file_name}{file_extension}'
    output_images = f'tmp/{message.document.file_id}'
    Proc_image.file_to_png(file_path, output_images)
    
    rotate_folder = f'tmp/{message.document.file_id}/rotated'
    for img in os.listdir(output_images):
        image_path = os.path.join(output_images, img)
        Proc_image.rotate_image(image_path,rotate_folder)

    result = YandexAPI.recognition_text(message.document.file_id)
    proc_data = Validation.read_json(result)
    res_list, interest_list = Validation.output_res(proc_data, message.document.file_id )
    Result.output_res(res_list, interest_list, message.document.file_id, id_request, compaign, ed_inst,\
                      name_ed_inst, date, city, address, responsible)
    
    doc_output = FSInputFile(f"tmp/{message.document.file_id}/output.xlsx")
    await message.answer_document(doc_output, 
                                  caption="Результат распознания")
    
    result_output = FSInputFile(f"tmp/{message.document.file_id}/result.xlsx")
    await message.answer_document(result_output, caption='Результат обработки')
    
    os.remove(f"tmp/{message.document.file_id}.pdf")
    shutil.rmtree(f"tmp/{message.document.file_id}")                                

    
  