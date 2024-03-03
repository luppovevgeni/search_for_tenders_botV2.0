from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from datetime import datetime
import db
from keyboards.default import default_kb
from keyboards.start import start_kb


router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    if db.users.count_documents({"user_id": message.from_user.id}) == 0:
        db.users.insert_one({"user_id": message.from_user.id,
                             "time": False,
                             "keywords": [],
                             "filters": {"time_slot": 1},
                             "sites": [],
                             "days": [0, 1, 2, 3, 4],
                             "premium": False,
                             "trial_period": False,
                             "date_of_regestration": datetime.now()})
        await message.answer("Для начала пользования *настоятельно* рекомендуем прочитать краткую информацию о боте и его использовании", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=start_kb())
    else:
        await message.answer("Бот обновлён", reply_markup=default_kb())
        await state.clear()


@router.message(Command("help"))
async def clear(message: Message):
    telegraph_link = '<a href="https://telegra.ph/Informaciya-o-bote-01-06">этой</a>'
    await message.answer(f'Вся актуальная информация о боте находится в {telegraph_link} статье, если у вас остались вопросы или есть предложения, пишите @evgeni_luppov', parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.message(Command("clear"))
async def clear(message: Message):
    db.users.delete_many({})