import logging
import os
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

CHANNEL_ID = os.getenv('CHANNEL_ID')
TOKEN = os.getenv('BOT_TOKEN')
TIMEZONE = os.getenv('TIMEZONE')


async def send_message(message: str):
    """Sends message to telegram bot"""
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text=message)


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
