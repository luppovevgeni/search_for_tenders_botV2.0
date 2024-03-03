from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def change_time_slot_filter_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Изменить ✏️", callback_data="change_time_slot_filter")
    kb.button(text="Назад ⬅️", callback_data="filters")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)