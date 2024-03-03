from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import SITES
import db
from callbacks.site_callback import SiteCallbackFactory


def available_sites_kb(user_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    user_sites = db.users.find_one({"user_id": user_id})["sites"]
    for i in range(len(SITES)):
        if SITES[i] in user_sites:
            kb.button(text=f'{SITES[i]} ✅', callback_data=SiteCallbackFactory(number=i))
        else:
            kb.button(text=f'{SITES[i]} ❌', callback_data=SiteCallbackFactory(number=i))
    kb.adjust(2)
    kb.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_settings"))
    return kb.as_markup(resize_keyboard=True)