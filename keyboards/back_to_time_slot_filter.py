from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def back_to_time_slot_filter_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅", callback_data="time_slot_filter")
    return kb.as_markup(resize_keyboard=True)