from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import link
from aiogram.enums.parse_mode import ParseMode
from keyboards.available_sites import available_sites_kb
from keyboards.settings import settings_kb
from keyboards.key_words import key_words_kb
from keyboards.sending import sending_kb
from keyboards.abort_key_words import abort_key_words_kb
from keyboards.abort_sending import abort_sending_kb
from keyboards.week_days import week_days_kb
from keyboards.filters import filters_kb
from keyboards.change_time_slot_filter import change_time_slot_filter_kb
from keyboards.abort_change_time_slot_filter import abort_change_time_slot_filter_kb
from keyboards.back_to_premium import back_to_premium_kb
from keyboards.premium import premium_kb
from keyboards.default import default_kb
from callbacks.site_callback import SiteCallbackFactory
from callbacks.week_days_callback import WeekDaysCallbackFactory
from states import ChangeKeyWords, SendingTime, TimeSlot
from datetime import datetime, timedelta
import db, scheduler, config as config, main


router = Router()


@router.callback_query(SiteCallbackFactory.filter())
async def sites_func(callback: types.CallbackQuery, callback_data: SiteCallbackFactory):
    user_id = callback.from_user.id
    user_data = db.users.find_one({"user_id": user_id})
    user_sites = user_data["sites"]
    if config.SITES[callback_data.number] in user_sites:
        if len(user_sites) == 1:
            await callback.answer(text="Вы не можете отключить все сайты, у вас подключена рассылка", show_alert=True)
        else: 
            user_sites.remove(config.SITES[callback_data.number])
            db.users.find_one_and_update({"user_id": user_id}, {"$set": {"sites": user_sites}})
            await callback.message.edit_reply_markup(reply_markup=available_sites_kb(user_id))
    else:
        if len(user_sites) == 2 and user_data["premium"] == False:
            await callback.answer(text="Для парсинга более 2 сайтов купите подписку", show_alert=True)
        else:
            db.users.find_one_and_update({"user_id": user_id}, {"$set": {"sites": user_sites + [config.SITES[callback_data.number]]}})
            await callback.message.edit_reply_markup(reply_markup=available_sites_kb(user_id))
    await callback.answer()


@router.callback_query(WeekDaysCallbackFactory.filter())
async def week_days_func(callback: types.CallbackQuery, callback_data: WeekDaysCallbackFactory):
    user_id = callback.from_user.id
    user_days = db.users.find_one({"user_id": user_id})["days"]
    if callback_data.number in user_days:
        user_days.remove(callback_data.number)
        db.users.find_one_and_update({"user_id": user_id}, {"$set": {"days": user_days}})
        await callback.message.edit_reply_markup(reply_markup=week_days_kb(user_id))
    else:
        db.users.find_one_and_update({"user_id": user_id}, {"$set": {"days": user_days + [callback_data.number]}})
        await callback.message.edit_reply_markup(reply_markup=week_days_kb(user_id))
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings_func(callback: types.CallbackQuery):
    await callback.message.edit_text("Настройки ⚙️", reply_markup=settings_kb())
    await callback.answer()


@router.callback_query(F.data == "available_sites")
async def available_sites_func(callback: types.CallbackQuery):
    await callback.message.edit_text("Доступные сайты (для изменения нажмите на сайт)", reply_markup=available_sites_kb(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "key_words")
async def key_words_func(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_key_words = db.users.find_one({"user_id": callback.from_user.id})["keywords"]
    n = "\n"
    await callback.message.edit_text("У вас еще нет клюевых слов" if user_key_words == [] else f'Ваши ключевыевые слова:\n{n.join(user_key_words)}', reply_markup=key_words_kb())
    await callback.answer()


@router.callback_query(F.data == "change_key_words")
async def change_key_words_func(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Напишите ключевые слова через запятую, например:\n\nРемонт, вентиляция, аудит", reply_markup=abort_key_words_kb())
    await state.set_state(ChangeKeyWords.input_words)
    await callback.answer()


@router.callback_query(F.data == "activate_sending")
async def activate_sending_func(callback: types.CallbackQuery, state: FSMContext):
    user_data = db.users.find_one({"user_id": callback.from_user.id})
    user_premium = user_data["premium"]
    user_keywords = user_data["keywords"]
    user_sites = user_data["sites"]
    if not user_premium:
        await callback.answer("Для подключения рассылки у Вас должна быть подписка", show_alert=True)
    elif user_keywords == []:
        await callback.answer("Для подключения рассылки заполните ключевые слова", show_alert=True)
    elif user_sites == []:
        await callback.answer("Для подключения рассылки выберете хотя бы один сайт", show_alert=True)
    else:
        await callback.message.edit_text(text="Напишите время в которое бот будет посылать информацию (напрмер 11)", reply_markup=abort_sending_kb())
        await state.set_state(SendingTime.input_time)
    await callback.answer()


@router.callback_query(F.data == "deactivate_sending")
async def deactivate_sending_func(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    db.users.update_one({"user_id": user_id}, {"$set": {"time": False}})
    scheduler.scheduler.remove_job(str(user_id))
    await callback.answer("Вы отключили рассылку", show_alert=False)
    await callback.message.edit_text(text="Рассылка 📫", reply_markup=sending_kb(user_id))
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "week_days")
async def week_days_func(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text(text="Дни недели (нажми на день недели что бы изменить)", reply_markup=week_days_kb(user_id))
    await callback.answer()


@router.callback_query(F.data == "sending")
async def sending_func(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    time = db.users.find_one({"user_id": user_id})["time"]
    if time:
        await callback.message.edit_text(text=f'Рассылка 📫\n\nСейчас она подключна на {time}', reply_markup=sending_kb(user_id))
    else:
        await callback.message.edit_text(text="Рассылка 📫", reply_markup=sending_kb(user_id))
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "filters")
async def filters_func(callback: types.CallbackQuery):
    await callback.message.edit_text(text="Доступные фильтры", reply_markup=filters_kb())
    await callback.answer()


@router.callback_query(F.data == "time_slot_filter")
async def time_slot_filter_func(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    time_slot = db.users.find_one({"user_id": user_id})["filters"]["time_slot"]
    if time_slot == 1:
        message_text = f'Сейчас поиск работает с периодом в {time_slot} день'
    elif time_slot < 5:
        message_text = f'Сейчас поиск работает с периодом в {time_slot} дня'
    else:
        message_text = f'Сейчас поиск работает с периодом в {time_slot} дней'
    info_link = link("Как работает этот фильтр?", "https://telegra.ph/Informaciya-o-bote-01-06#Фильтры")
    await callback.message.edit_text(text=f'{message_text}\n\n{info_link}', reply_markup=change_time_slot_filter_kb(), parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "change_time_slot_filter")
async def change_time_slot_filter_func(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Напишите период времени в днях(от 1 до 7)", reply_markup=abort_change_time_slot_filter_kb())
    await state.set_state(TimeSlot.input_time_slot)
    await callback.answer()


@router.callback_query(F.data == "free_access")
async def free_access_func(callback: types.CallbackQuery, state: FSMContext):
    end_date = datetime.now() + timedelta(days=10)
    user_id = callback.from_user.id
    scheduler.scheduler.add_job(scheduler.pre_premium_end, id=f'free_access_{str(user_id)}', trigger="date", run_date=(end_date - timedelta(days=1)), args=[user_id])
    db.users.find_one_and_update({"user_id": user_id}, {"$set": {"premium": end_date}})
    await callback.message.edit_text(text="Вы получили пробную подписку на 10 дней, бот уведомит вас об истечении подписки", reply_markup=back_to_premium_kb())
    await callback.answer()


@router.callback_query(F.data == "premium")
async def premium_func(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = db.users.find_one({"user_id": user_id})
    user_premium = user_data["premium"]
    if user_premium == False:
        await callback.message.edit_text(text="Управление вашей подпиской", reply_markup=premium_kb(user_data["trial_period"]))
    elif user_premium == True:
        await callback.message.edit_text(text="У вас подключена подписка на всегда, приятного пользования")
    else:
        end_date = user_premium
        delta = user_premium - datetime.now()
        await callback.message.edit_text(text=f'Ваша подписка активна до {end_date.strftime("%d.%m %H:%M")} (еще {delta.days} дней)\n\nЕсли вы оплатите подписку, то она продлиться относительно текущей', reply_markup=premium_kb(True))
    await callback.answer()


@router.callback_query(F.data == "buy_subscription")
async def buy_subscription_func(callback: types.CallbackQuery):
    await main.bot.send_invoice(chat_id=callback.from_user.id,
                                payload='None',
                                title="Подписка на месяц",
                                description="Вы получите подписку на месяц (30 дней)",
                                provider_token=config.PAYMENTS_TOKEN,
                                currency="rub",
                                photo_url="https://neftegaz.ru/upload/iblock/dd8/dd8c5131d662e4572b074717d70fc784.jpg",
                                photo_width=900,
                                photo_height=450,
                                is_flexible=False,
                                prices = [types.LabeledPrice(label="Подписка на месяц", amount=19900)],
                                start_parameter="one-month-subscription",)
    await callback.message.delete()


@router.callback_query(F.data == "get_start")
async def get_start_func(callback: types.CallbackQuery):
    await callback.message.answer(text="Отлино! Приятного пользования", reply_markup=default_kb())
    await callback.message.delete()


@router.callback_query()
async def change_time_slot_filter_func(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(text="В разроботке", show_alert=True)