from aiogram import Router, F, types
from aiogram.types import ContentType
from datetime import datetime, timedelta
from keyboards.premium import premium_kb
import main, db, scheduler


router = Router()


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await main.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message()
async def process_successful_payment(message: types.Message):
    print(message)
    if message.content_type == ContentType.SUCCESSFUL_PAYMENT:
        await message.answer("Благодарим Вас за оплату подписки на месяц!")
        user_id = message.from_user.id
        user_premium = db.users.find_one({"user_id": user_id})["premium"]
        if user_premium == False:
            user_premium = datetime.now()
        end_date = user_premium + timedelta(days=30)
        db.users.update_one({"user_id": user_id}, {"$set": {"premium": end_date}})
        delta = end_date - datetime.now()
        await message.answer(f'Ваша подписка активна до {end_date.strftime("%d.%m %H:%M")} (еще {delta.days} дней)\n\nЕсли вы оплатите подписку, то она продлиться относительно текущей', reply_markup=premium_kb(True))
        try:
            scheduler.scheduler.remove_job(f'pre_premium_end_{str(user_id)}')
        except:
            pass
        try:
            scheduler.scheduler.remove_job(f'free_access_{str(user_id)}')
        except:
            pass
        try:
            scheduler.scheduler.remove_job(f'premium_end_{str(user_id)}')
        except:
            pass
        scheduler.scheduler.add_job(scheduler.pre_premium_end, id=f'pre_premium_end_{str(user_id)}', trigger="date", run_date=(end_date - timedelta(days=1)), args=[user_id])