from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR
import os
import asyncio
import pytz
import logging #in py it's a singleton, so it has the same configuration in every .py file
from config import load_config
load_config()

from constants import URL_EU
from istat import retrieve_inflation
from euroSTR import retrieve_euro_str
from utils import logScheduledJobs, send_message
ENV = os.environ.get('ENV')
TIMEZONE = os.environ.get('TIMEZONE')



### INFLATION ###

async def task_monthly():
    logging.info("## [INFLATION] ## Running the monthly task (20th of the month)")
    #TODO: fare la funzione parametrizzata in base al mese..
    value = await retrieve_inflation()
    logging.info(f"## [INFLATION] ## Valore recuperato dalle API ISTAT: {value}")
    last_month_date = "bho"
    last_month_name = "gennaio"
    message = f"""Secondo [dati ISTAT]({"www.google.com"}) in Italia a {last_month_date}:
Inflazione nel mese di *{last_month_name}*: {value}
Inflazione nell'*ultimo anno*: {value}
"""
    await send_message(message)
    logging.info(f"## [INFLATION] ## Message sent to Telegram: {message}")

#################



### EURO STR ###

async def task_weekly():
    logging.info("### [EURO STR] ### Running the weekly task (every Monday)")
    euro_str_value = retrieve_euro_str()
    message = f"[Euro short-term rate]({URL_EU}) (`€STR`) odierno: `{euro_str_value}`"
    await send_message(message)
    logging.info(f"### [EURO STR] ### Message sent to Telegram: {message}")

################



def error_listener(event):
    if event.exception:
        logging.error(f"Job {event.job_id} failed with exception: {event.exception}")


def main():
    #asyncio.run(task_monthly())
    #asyncio.run(task_weekly())
    scheduler = AsyncIOScheduler()
    timezone = pytz.timezone(TIMEZONE)

    #triggerMonthly = CronTrigger(day=20, hour=8, minute=31, timezone=timezone)
    #triggerWeakly = CronTrigger(day_of_week="mon", hour=8, minute=30, timezone=timezone)
    triggerMonthly = CronTrigger(day=20, hour=21, minute=30, timezone=timezone)
    triggerWeakly = CronTrigger(day_of_week=2, hour=21, minute=29, timezone=timezone)
    scheduler.add_job(task_monthly, triggerMonthly, id="monthly_task")
    scheduler.add_job(task_weekly, triggerWeakly, id="weekly_task")

    scheduler.add_listener(error_listener, EVENT_JOB_ERROR)
    scheduler.start()
    logging.info("Scheduler started. Tasks are scheduled.")

    logScheduledJobs(scheduler)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
