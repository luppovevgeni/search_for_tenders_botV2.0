from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def default_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Настройки⚙️")
    kb.button(text="Рассылка📫")
    kb.button(text="Поиск🔎")
    kb.button(text="Подписка👤")
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="меню")