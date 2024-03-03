from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def key_words_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Изменить ✏️", callback_data="change_key_words")
    kb.button(text="Назад ⬅️", callback_data="back_to_settings")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)