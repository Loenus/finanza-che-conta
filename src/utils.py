import logging
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from telegram import Bot
from telegram.constants import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from constants import MONTH_NAMES

CHANNEL_ID = os.getenv('CHANNEL_ID')
TOKEN = os.getenv('BOT_TOKEN')
TIMEZONE = os.getenv('TIMEZONE')


async def send_message(message: str):
    """Sends message to telegram bot"""
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text=message, disable_web_page_preview=True, parse_mode = ParseMode.MARKDOWN)


def logScheduledJobs(scheduler: AsyncIOScheduler):
    """View all scheduled jobs

    Parameters
    ----------
    scheduler : AsyncIOScheduler
        It must have at least one scheduled job
    """
    msg = f"Scheduled jobs (with timezone= {TIMEZONE}): "
    for job in scheduler.get_jobs():
        msg = msg + f"\nJob ID: {job.id}, Next Run: {job.next_run_time}"
    logging.info(msg)


def get_last_day_of_previous_month():
    today = datetime.today()
    last_day_previous_month = (today.replace(day=1) - relativedelta(days=1))
    return last_day_previous_month.strftime("%Y-%m-%d")


def get_previous_month_name():
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    
    #previous_month_name = last_day_of_previous_month.strftime("%B") #english
    previous_month_name = MONTH_NAMES[last_day_of_previous_month.month]
    return previous_month_name
