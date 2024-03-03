from aiogram.filters.callback_data import CallbackData

class WeekDaysCallbackFactory(CallbackData, prefix="day"):
    number: int