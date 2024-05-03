from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State

router = Router()

class CompilationModul(StatesGroup):
    choosing_id_request = State()
    choosing_compaign = State()
    choosing_ed_inst = State()
    choosing_name_ed_inst = State()
    choosing_date = State()
    choosing_city = State()
    choosing_address = State()
    choosing_responsible = State()




@router.message(StateFilter(None), Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Привет!  Я бот распознования анкет. Давай заполним необходимые обязательные поля.\n\
         Введите номер заявки: "
    )
    await state.set_state(CompilationModul.choosing_id_request)

@router.message(CompilationModul.choosing_id_request, F.text)
async def id_request_chosen(message: Message, state: FSMContext):
    await state.update_data(id_request = message.text)
    
    await message.answer(
        'Отлично, теперь выберем компанию'
    )
    await state.set_state(CompilationModul.choosing_compaign)

@router.message(CompilationModul.choosing_compaign, F.text)
async def compaign_chosen(message: Message, state: FSMContext):
    await state.update_data(compaign = message.text)
    
    await message.answer(
        'Теперь давай выберем тип учебного заведения.'
    )
    await state.set_state(CompilationModul.choosing_ed_inst)
@router.message(CompilationModul.choosing_ed_inst, F.text)
async def ed_inst_chosen(message: Message, state: FSMContext):
    await state.update_data(ed_inst = message.text)

    await message.answer(
        'Выберем название учебного заведения.'
    )
    await state.set_state(CompilationModul.choosing_name_ed_inst)
@router.message(CompilationModul.choosing_name_ed_inst, F.text)
async def name_ed_inst_chosen(message: Message, state: FSMContext):
    await state.update_data(name_ed_inst = message.text)

    await message.answer(
        'Заполни дату анкетирования в формате ДД.ММ.ГГГГ'
    )
    await state.set_state(CompilationModul.choosing_date)

@router.message(CompilationModul.choosing_date, F.text)
async def date_chosen(message: Message, state: FSMContext):
    await state.update_data(date = message.text)

    await message.answer(
        'Теперь выберем город'
    )
    await state.set_state(CompilationModul.choosing_city)

@router.message(CompilationModul.choosing_city, F.text)
async def city_chosen(message: Message, state: FSMContext):
    await state.update_data(city = message.text)

    await message.answer(
        'Введите адрес школы'
    )
    await state.set_state(CompilationModul.choosing_address)

@router.message(CompilationModul.choosing_address, F.text)
async def address_chosen(message: Message, state: FSMContext):
    await state.update_data(address = message.text)

    await message.answer(
        'Введите имя ответственного лица'
    )
    await state.set_state(CompilationModul.choosing_responsible)

@router.message(CompilationModul.choosing_responsible, F.text)
async def responsible_chosen(message: Message, state: FSMContext):
    await state.update_data(responsible = message.text)
    
    await message.answer(
        'Кидай мне теперь свою анкету, и я ее буду распозновать'
    )
   
