from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def abort_change_time_slot_filter_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена 🚫", callback_data="time_slot_filter")
    return kb.as_markup(resize_keyboard=True)