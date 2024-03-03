from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import db


def sending_kb(user_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    sending = db.users.find_one({"user_id": user_id})["time"]
    if sending:
        kb.button(text="Время 🕔", callback_data="activate_sending")
        kb.button(text="Дни недели 🗓", callback_data="week_days")
        kb.button(text="Отключить 🔕", callback_data="deactivate_sending")
    else:
        kb.button(text="Подключить 🔔", callback_data="activate_sending")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)