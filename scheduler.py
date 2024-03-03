from apscheduler.schedulers.asyncio import AsyncIOScheduler
import db, parse, main
from datetime import datetime, timedelta
from keyboards.premium import premium_kb


def initialization():
    global scheduler
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()
    for user in db.users.find({}):
        if user["time"] != False:
            scheduler.add_job(parse.parser, id=str(user["user_id"]), trigger="cron", hour=user["time"], minute="00", args=[user["user_id"]])
        if user["premium"] != True and user["premium"] != False:
            if (user["premium"] - datetime.now()).days > 1:
                scheduler.add_job(pre_premium_end, id=f'pre_premium_end_{str(user["user_id"])}', trigger="date", run_date=(user["premium"] - timedelta(days=1)), args=[user["user_id"]])
            else:
                scheduler.add_job(premium_end, id=f'premium_end_{str(user["user_id"])}', trigger="date", run_date=user["premium"], args=[user["user_id"]])


async def pre_premium_end(user_id):
    end_date = datetime.now() + timedelta(days=1)
    scheduler.add_job(premium_end, id=f'premium_end_{str(user_id)}', trigger="date", run_date=end_date, args=[user_id])
    await main.bot.send_message(user_id, "Ваша подписка закончится через сутки! Не забудьте её продлить", reply_markup=premium_kb(True))


async def premium_end(user_id):
    user_data = db.users.find_one({"user_id": user_id})
    sites = user_data["sites"]
    key_words = user_data["keywords"]
    db.users.find_one_and_update({"user_id": user_id}, {"$set": {"premium": False, "time": False, "sites": sites[:2], "keywords": key_words[5:]}})
    scheduler.remove_job(str(user_id))
    await main.bot.send_message(user_id, "Ваша падписка кончилась", reply_markup=premium_kb(True))