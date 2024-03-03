from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import WEEK_DAYS
import db
from callbacks.week_days_callback import WeekDaysCallbackFactory


def week_days_kb(user_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    user_days = db.users.find_one({"user_id": user_id})["days"]
    for elem in WEEK_DAYS:
        if WEEK_DAYS.index(elem) in user_days:
            kb.button(text=f'{elem} ✅', callback_data=WeekDaysCallbackFactory(number=WEEK_DAYS.index(elem)))
        else:
            kb.button(text=f'{elem} ❌', callback_data=WeekDaysCallbackFactory(number=WEEK_DAYS.index(elem)))
    kb.adjust(2)
    kb.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="sending"))
    return kb.as_markup(resize_keyboard=True)