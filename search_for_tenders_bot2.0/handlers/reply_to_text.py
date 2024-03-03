from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.settings import settings_kb
from keyboards.see_key_words import see_key_words_kb
from keyboards.key_words import key_words_kb
from keyboards.sending import sending_kb
from keyboards.abort_sending import abort_sending_kb
from keyboards.abort_change_time_slot_filter import abort_change_time_slot_filter_kb
from keyboards.back_to_sending import back_to_sending_kb
from keyboards.back_to_time_slot_filter import back_to_time_slot_filter_kb
from keyboards.premium import premium_kb
from states import ChangeKeyWords, SendingTime, TimeSlot, Searching
from datetime import datetime
import db, scheduler, parse, logging


router = Router()
router.message.filter(F.text != None)


@router.message(F.text == "Настройки⚙️")
async def settings(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Настройки ⚙️", reply_markup=settings_kb())


@router.message(F.text == "Рассылка📫")
async def sending(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    time = db.users.find_one({"user_id": user_id})["time"]
    if time:
        await message.answer(f'Рассылка 📫\n\nСейчас она подключна на {time}', reply_markup=sending_kb(user_id))
    else:
        await message.answer("Рассылка 📫", reply_markup=sending_kb(user_id))


@router.message(F.text == "Поиск🔎")
async def search(message: Message, state: FSMContext):
    if await state.get_state() == "Searching:searching":
        await message.delete()
    else:
        await state.set_state(Searching.searching)
        user_id = message.from_user.id
        user_data = db.users.find_one({"user_id": user_id})
        user_words = user_data["keywords"]
        user_sites = user_data["sites"]
        if user_words == []:
            await message.answer("Сначала перейдите в настройки и заполните ключевые слова")
        elif user_sites == []:
            await message.answer("Сначала перейдите в настройки и выберете хотя бы один сайт")
        else:
            await parse.parser(user_id, True, state)


@router.message(F.text == "Подписка👤")
async def premium(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user_data = db.users.find_one({"user_id": user_id})
    user_premium = user_data["premium"]
    if user_premium == False:
        await message.answer("Управление вашей подпиской", reply_markup=premium_kb(user_data["trial_period"]))
    elif user_premium == True:
        await message.answer("У вас подключена подписка на всегда, приятного пользования")
    else:
        end_date = user_premium
        delta = user_premium - datetime.now()
        await message.answer(f'Ваша подписка активна до {end_date.strftime("%d.%m %H:%M")} (еще {delta.days} дней)\n\nЕсли вы оплатите подписку, то она продлиться относительно текущей', reply_markup=premium_kb(True))


@router.message(ChangeKeyWords.input_words)
async def input_key_words(message: Message, state: FSMContext):
    words = list(map(lambda x: x.rstrip().lstrip(), message.text.split(",")))
    user_id = message.from_user.id
    user_premium = db.users.find_one({"user_id": user_id})["premium"]
    if len(words) > 5 and user_premium == False:
        await state.clear()
        await message.answer("Для того что бы иметь больше 5 ключевых слов, купите подписку")
        user_key_words = db.users.find_one({"user_id": user_id})["keywords"]
        n = "\n"
        await message.answer("У вас еще нет клюевых слов" if user_key_words == [] else f'Ваши ключевыевые слова:\n{n.join(user_key_words)}', reply_markup=key_words_kb())
    elif len(words) > 40:
        await message.answer("У Вас не может быть больше 40 слов")
        user_key_words = db.users.find_one({"user_id": user_id})["keywords"]
        n = "\n"
        await message.answer("У вас еще нет клюевых слов" if user_key_words == [] else f'Ваши ключевыевые слова:\n{n.join(user_key_words)}', reply_markup=key_words_kb())
    else:
        db.users.update_one({'user_id':user_id}, {'$set': {'keywords': words}})
        await message.answer("Ваши ключивые слова изменены", reply_markup=see_key_words_kb())
        await state.clear()


@router.message(SendingTime.input_time)
async def input_time(message: Message, state: FSMContext):
    try:
        time = int(message.text)
        if time > 23 or time < 1:
            await message.answer("Ошибка, проверьте время и напишите еще раз", reply_markup=abort_sending_kb())
        else:
            user_id = message.from_user.id
            db.users.update_one({"user_id": user_id}, {"$set": {"time": time}})
            try:
                scheduler.scheduler.remove_job(str(user_id))
            except:
                pass
            scheduler.scheduler.add_job(parse.parser, id=str(user_id), trigger="cron", hour=time, minute="00", args=[user_id])
            await message.answer(f'Время рассылки установлено на {time}', reply_markup=back_to_sending_kb())
            await state.clear()
    except:
        await message.answer("Ошибка, проверьте время и напишите еще раз", reply_markup=abort_sending_kb())


@router.message(TimeSlot.input_time_slot)
async def input_time_slot(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        time_slot = int(message.text)
        if time_slot > 7 or time_slot < 1:
            await message.answer("Ошибка, проверьте период и напишите еще раз", reply_markup=abort_change_time_slot_filter_kb())
        else:
            filters = db.users.find_one({"user_id": user_id})["filters"]
            filters["time_slot"] = time_slot
            db.users.update_one({"user_id": user_id}, {"$set": {"filters": filters}})
            if time_slot == 1:
                message_text = f'Сейчас поиск работает с периодом в {time_slot} день'
            elif time_slot < 5:
                message_text = f'Сейчас поиск работает с периодом в {time_slot} дня'
            else:
                message_text = f'Сейчас поиск работает с периодом в {time_slot} дней'
            await message.answer(f'Период поиска установлен на {time_slot}', reply_markup=back_to_time_slot_filter_kb())
            await state.clear()
    except:
        await message.answer('Ошибка, проверьте период и напишите еще раз', reply_markup=abort_change_time_slot_filter_kb())