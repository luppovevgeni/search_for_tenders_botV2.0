from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Читать 📖", url="https://telegra.ph/Informaciya-o-bote-01-06")
    kb.button(text="Я прочел ✅", callback_data="get_start")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)