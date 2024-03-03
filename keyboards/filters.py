from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def filters_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Цена 💰", callback_data="price_filter")
    kb.button(text="Период поиска ⏳", callback_data="time_slot_filter")
    kb.button(text="Регион 🗺", callback_data="region_filter")
    kb.button(text="Назад ⬅️", callback_data="back_to_settings")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)