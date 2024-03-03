from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def premium_kb(trial_period) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if not trial_period:
        kb.button(text="Пробная подписка 🆓", callback_data="free_access")
    kb.button(text="Купить подписку 💳", callback_data="buy_subscription")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)