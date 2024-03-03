from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def settings_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Доступные сайты 🌐", callback_data="available_sites")
    kb.button(text="Ключевые слова 📝", callback_data="key_words")
    kb.button(text="Фильтры поиска 🗂", callback_data="filters")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)