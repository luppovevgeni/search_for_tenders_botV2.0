from aiogram.filters.callback_data import CallbackData

class SiteCallbackFactory(CallbackData, prefix="site"):
    number: int