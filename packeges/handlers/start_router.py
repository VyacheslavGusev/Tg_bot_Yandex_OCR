from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message, state:FSMContext):
    await state.clear()

    await message.answer(
        "Привет!  Я бот распознования анкет. Давай заполним обязательные поля"
    )