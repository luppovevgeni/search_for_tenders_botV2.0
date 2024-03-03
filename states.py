from aiogram.fsm.state import StatesGroup, State


class ChangeKeyWords(StatesGroup):
    input_words = State()


class SendingTime(StatesGroup):
    input_time = State()


class TimeSlot(StatesGroup):
    input_time_slot = State()


class Searching(StatesGroup):
    searching = State()