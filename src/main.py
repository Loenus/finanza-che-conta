from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR
import os
import asyncio
import pytz
import logging #in py it's a singleton, so it has the same configuration in every .py file
from config import load_config
load_config()

from constants import URL_EU, URL_ISTAT
from istat import retrieve_inflation
from euroSTR import retrieve_euro_str
from utils import logScheduledJobs, send_message, get_previous_month_name
ENV = os.getenv('ENV')
TIMEZONE = os.getenv('TIMEZONE')



### INFLATION ###

async def task_monthly():
    logging.info("## [INFLATION] ## Running the monthly task (18th of the month)")
    var_congiunturale, var_tendenziale = await retrieve_inflation()
    logging.info(f"## [INFLATION] ## Valori recuperati dall'API ISTAT" +
                f" -> var_congiunturale: {var_congiunturale} | " +
                f"var_tendenziale: {var_tendenziale}")
    message = f"""Riguardo il NIC, secondo [dati ISTAT]({URL_ISTAT}), in Italia a *{get_previous_month_name()}*:
variazione congiunturale: {var_congiunturale}%
*inflazione*: {var_tendenziale}%

Metti una stella a [questo mini-progetto](https://github.com/Loenus/finanza-che-conta) disponibile a tutti e completamente gratuito. Grazie ❤️
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
    if (ENV == "local"):    
        asyncio.run(task_monthly())
        asyncio.run(task_weekly())
        return
    
    scheduler = AsyncIOScheduler()
    timezone = pytz.timezone(TIMEZONE)

    triggerMonthly = CronTrigger(day=18, hour=8, minute=31, timezone=timezone)
    triggerWeakly = CronTrigger(day_of_week="mon", hour=8, minute=30, timezone=timezone)
    scheduler.add_job(task_monthly, triggerMonthly, id="monthly_task")
    scheduler.add_job(task_weekly, triggerWeakly, id="weekly_task")

    scheduler.add_listener(error_listener, EVENT_JOB_ERROR)
    scheduler.start()
    logging.info("Scheduler started. Tasks are scheduled.")

    logScheduledJobs(scheduler)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
