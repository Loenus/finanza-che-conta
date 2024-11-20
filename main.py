import os
import re
import requests
import datetime #from datetime
import schedule
import time
import asyncio
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from telegram.ext import ContextTypes, Application
from telegram.constants import ParseMode
from telegram.error import BadRequest, TimedOut
from dotenv import load_dotenv
from constants import URL_EU
from istat import retrieve_inflation
from euroSTR import retrieve_euro_str
from utils import next_weekday, check_jobs
from xml.etree import ElementTree as ET
from telegram import Bot
import pytz
load_dotenv()

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger('httpx').setLevel(logging.WARNING)

ENV = os.environ.get('ENV')
TIMEZONE = os.environ.get('TIMEZONE')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
application = Application.builder().token(os.environ.get('BOT_TOKEN')).build()
job_queue = application.job_queue

# Error handler for Bad Gateway
# def bad_gateway_error_handler(update, context):
#     logging.error(f"Bad Gateway error occurred: {context.error} ({update})")

# # Error handler for Flood control exceeded
# def flood_control_error_handler(update, context):
#     logging.warning(f"Flood control exceeded: {context.error} ({update})")

# Add error handlers to your Application object
# application.add_error_handler(BadRequest, bad_gateway_error_handler)
# application.add_error_handler(TimedOut, flood_control_error_handler)


ENV = os.environ.get('ENV')
TIMEZONE = os.environ.get('TIMEZONE')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
TOKEN = os.environ.get('BOT_TOKEN')
# Funzione per inviare messaggio su Telegram
async def send_message(message):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text=message)



### INFLATION ###

MONTHS = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

def retrieve_inflation_ISTAT(last_month_date): 
    """Ricerca l'articolo ISTAT riguardo l'inflazione nel mese precedente e ne estrapola le informazioni

    Parameters
    ----------
    last_month_date : str
        Mese e anno di riferimento per la ricerca
        (example: 'Luglio 2023')

    Returns
    -------
    list
        in ordine: 
        due percentuali (inflazione ultimo mese ed ultimo anno), 
        link all'articolo, errore (optional)
    boolean
        è un articolo con dati provvisori o no

    Raises
    ------
    Niente
        Se la richiesta fallisce, restituisce una stringa e None
    """
    
    URL_ISTAT = "https://www.istat.it"
    response = requests.get(URL_ISTAT + "/it/prezzi")
    if response.status_code != 200:
        logging.error(f"Errore nella richiesta HTTP [{response.status_code}]")
        return "Errore nella richiesta HTTP", None

    # Trovo l'articolo (url e percentuali inflazione)
    soup = BeautifulSoup(response.content, "html.parser")
    title_to_find = "Prezzi al consumo - " + last_month_date
    logging.info(f"Searching for '{title_to_find}'...")
    article = soup.find("a", {"title": title_to_find})
    if article:
        is_provisional = False
        url_article = article['href']
        inflation_text = article.text
    else:
        logging.info(f"No article found for '{title_to_find}'")
        title_to_find = "Prezzi al consumo (provvisori) - " + last_month_date
        logging.info(f"Searching for '{title_to_find}'...")
        article = soup.find("a", {"title": title_to_find})
        if not article:
            logging.warning(f"Nessun elemento a trovato con il valore title '{title_to_find}'")
            return f"Nessun elemento a trovato con il valore title '{title_to_find}'", None
        is_provisional = True
        url_article = article['href']
        inflation_text = article.text
    logging.info(f"Link found: {url_article}")
    logging.info(f"Caption: '{inflation_text}'")
    percent_pattern = r"[-+]?\d+,\d+%|\bnulla\b"
    inflations = re.findall(percent_pattern, inflation_text)
    inflations.append(URL_ISTAT + url_article)

    # Apro l'articolo
    full_article = requests.get(URL_ISTAT + url_article)
    if full_article.status_code != 200:
        logging.error(f"Errore nella richiesta HTTP [{response.status_code}]")
        return "Errore nella richiesta HTTP", None
    soup2 = BeautifulSoup(full_article.content, "html.parser")

    # Trovo la next release e creo il job
    next_release_html = soup2.find('p', class_='nextRelease')
    if not next_release_html:
        error_message = "Non è stata trovata nessuna data per la next Release. La prossima esecuzione verrà schedulata tra 3 settimane."
        logging.warning(error_message)
        job_inflation = job_queue.run_once(callback_inflation, datetime.timedelta(weeks=3))
        inflations.append(error_message)
        return inflations, is_provisional
    else:
        next_release_text = next_release_html.span.text
        day, month, year = next_release_text.split(' ')
        months_lower = [ x.lower() for x in MONTHS ]
        month_number = months_lower.index(month)
        next_release_date = datetime.datetime(int(year), month_number + 1, int(day), 8,1, tzinfo=ZoneInfo(TIMEZONE)) # at 8:01 of the specified timezone
        next_release_date += datetime.timedelta(days=1)
        logging.info(f"Next Release: {next_release_date}")
        job_inflation = job_queue.run_once(callback_inflation, next_release_date)
    
    # inflations: % ultimo mese, % ultimo anno, link articolo, (optional) messaggio di errore
    return inflations, is_provisional

async def callback_inflation(context: ContextTypes.DEFAULT_TYPE):
    current_date = datetime.datetime.now(tz=ZoneInfo(TIMEZONE))
    last_month_name = MONTHS[current_date.month - 2]
    last_month_date = last_month_name + " " + str(current_date.year)
    if current_date.month == 1:
        last_month_date = last_month_name + " " + str(current_date.year -1)

    inflations, is_provisional = retrieve_inflation_ISTAT(last_month_date)
    if len(inflations) != 3: # allora contiene un quarto campo, ovvero l'errore
        logging.warning(f"Qualcosa è andato storto nell'estrapolare i dati dell'inflazione dal testo: '{inflations}'")
        return
    
    # se il link già presente in chat, return (è il caso in cui il bot è stato aggiornato alla versione più recente)
    url_chat = 'https://t.me/s/' + CHANNEL_ID.replace('@','')
    response = requests.get(url_chat)
    if response.status_code != 200:
        logging.error(f"Errore nella richiesta HTTP [{response.status_code}]")
        return "Errore nella richiesta HTTP"
    soup = BeautifulSoup(response.content, "html.parser")
    link_last_article = soup.find("a", href = inflations[2])
    if link_last_article and ENV == "prod":
        logging.info('link già trovato in chat.')
        return

    inflations[0] = f"`{inflations[0].replace(',', '.')}`"
    inflations[1] = f"`{inflations[1].replace(',', '.')}`"

    provvisori = " (provvisori)" if is_provisional else ""
    message = f"""Secondo [dati ISTAT{provvisori}]({inflations[2]}) in Italia a {last_month_date}:
Inflazione nel mese di *{last_month_name}*: {inflations[0]}
Inflazione nell'*ultimo anno*: {inflations[1]}
"""
    if len(inflations) >= 4:
        message += "\n\n" + inflations[3]
    
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message, disable_web_page_preview=True, parse_mode = ParseMode.MARKDOWN)
    #check_jobs(job_queue)

#################


### EURO STR ###

async def callback_euro_str(context: ContextTypes.DEFAULT_TYPE):
    euro_str_value = retrieve_euro_str()
    message = f"[Euro short-term rate]({URL_EU}) (`€STR`) odierno: `{euro_str_value}`"
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message, disable_web_page_preview=True, parse_mode = ParseMode.MARKDOWN)

################







API_URL = "https://sdmx.istat.it/SDMXWS/rest/data/167_744/M.00.IT.7.39/"
PARAMS = {
    "startPeriod": "2024-10-31"
}
HEADERS = {
    "Accept": "application/json"
}


# Funzione per fare la chiamata API e leggere l'XML
async def fetch_and_process_xml():
    try:
        logging.info("dentor la unzione")
        # Esegui la chiamata all'API
        response = requests.get(API_URL, params=PARAMS, headers=HEADERS)
        response.raise_for_status()  # Verifica se la risposta è OK

        logging.info("analizzo risposta")
        await send_message("sto analizzando")
        data = response.json()  # Usa il metodo json() per convertire la risposta in un dizionario Python

        #results = data.get("dataSets", [])  # Accedi alla chiave 'results' e ottieni una lista
        dataset = data["dataSets"][0]  # Primo elemento nella lista "dataSets"
        series = dataset["series"]  # La chiave "series"
        
        # Accedi alla prima chiave in "series" (ad esempio "0:0:0:0:0")
        first_series_key = next(iter(series))  # Usa iter() per ottenere la prima chiave
        first_series = series[first_series_key]  # Recupera il valore associato
        
        # Accedi a "observations" e alla chiave "0"
        observations = first_series["observations"]
        value = observations["0"][0]  # Primo elemento nella lista associata alla chiave "0"
        
        return value

    except requests.exceptions.RequestException as e:
        logging.error(f"Errore nella richiesta API: {e}")

    except json.JSONDecodeError as e:
        logging.error(f"Errore nel parsing del JSON: {e}")
        return f"Errore nel parsing del JSON: {e}"

    except KeyError as e:
        logging.error(f"Chiave mancante nei dati JSON: {e}")
        return f"Chiave mancante: {e}"

    except IndexError as e:
        logging.error(f"Errore negli indici dei dati JSON: {e}")
        return f"Errore negli indici: {e}"

    except TypeError as e:
        logging.error(f"Errore di tipo nei dati JSON: {e}")
        return f"Errore di tipo: {e}"

    except Exception as e:
        logging.error(f"Errore imprevisto: {e}")
        return f"Errore imprevisto: {e}"


# Funzione per pianificare l'esecuzione del 20 di ogni mese
async def job():
    logging.info("entrato nel job")
    current_date = datetime.datetime.now()
    #if current_date.day == 20:
    value = await fetch_and_process_xml()
    logging.info(f"Valore estratto: {value}")

# Pianifica il task ogni giorno (ma eseguirà la chiamata solo il 20)
#schedule.every().day.at("08:30").do(lambda: asyncio.create_task(job()))  # Usare lambda per creare task asincroni
#schedule.every(1).minute.do(lambda: asyncio.create_task(job()))














def error_listener(event):
    if event.exception:
        logging.error(f"Job {event.job_id} failed: {event.exception}")



async def task_monthly():
    logging.info("Running the monthly task (20th of the month)")
    value = await fetch_and_process_xml()
    logging.info(f"Valore estratto: {value}")
    await send_message(f"ho recuperato il valore: {value}")
    last_month_date = "bho"
    last_month_name = "gennaio"
    message = f"""Secondo [dati ISTAT]({"www.google.com"}) in Italia a {last_month_date}:
Inflazione nel mese di *{last_month_name}*: {value}
Inflazione nell'*ultimo anno*: {value}
"""
    await send_message(message)


async def task_weekly():
    logging.info("Running the weekly task (every Monday)")
    euro_str_value = retrieve_euro_str()
    message = f"[Euro short-term rate]({URL_EU}) (`€STR`) odierno: `{euro_str_value}`"
    await send_message(message)


def error_listener(event):
    if event.exception:
        logging.error(f"Job {event.job_id} failed with exception: {event.exception}")
    else:
        logging.info(f"Job {event.job_id} completed successfully.")

        # View all scheduled jobs after successful execution
        logging.info("Upcoming scheduled jobs:")
        for job in event.scheduler.get_jobs():  # Use event.scheduler to access the scheduler instance
            logging.info(f"Job ID: {job.id}, Next Run: {job.next_run_time}")




# Avvia il bot e esegue la pianificazione
def main():
    #asyncio.run(task_monthly())
    #asyncio.run(task_weekly())
    scheduler = AsyncIOScheduler()
    timezone = pytz.timezone(TIMEZONE)

    scheduler.add_job(task_monthly, CronTrigger(day=20, hour=8, minute=30, timezone=timezone), id="monthly_task")
    scheduler.add_job(task_weekly, CronTrigger(day_of_week="mon", hour=9, minute=0, timezone=timezone), id="weekly_task")

    scheduler.add_listener(error_listener, EVENT_JOB_ERROR)
    scheduler.start()

    logging.info("Scheduler started. Tasks are scheduled.")
    
    # View all scheduled jobs
    logging.info("Scheduled jobs:")
    for job in scheduler.get_jobs():
        logging.info(f"Job ID: {job.id}, Next Run: {job.next_run_time}")

    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()







    """ job_inflation = job_queue.run_once(callback_inflation, datetime.datetime.now(tz=ZoneInfo(TIMEZONE)) + datetime.timedelta(seconds=3))
    if ENV == "dev":
        job_euro_str = job_queue.run_repeating(callback_euro_str, datetime.timedelta(seconds=15), datetime.datetime.now(tz=ZoneInfo(TIMEZONE))+ datetime.timedelta(seconds=1))
    else:
        d = datetime.datetime.now(tz=ZoneInfo(TIMEZONE))
        next_monday = next_weekday(d, 0).replace(hour=8,minute=30,second=0) # 0 = Monday, 1=Tuesday ..
        logging.info(f"Prima esecuzione per la ricerca dell'EURO STR schedulata per {str(next_monday)}. Successivamente ogni lunedì.")
        job_euro_str = job_queue.run_repeating(callback_euro_str, datetime.timedelta(weeks=1), next_monday)
    application.run_polling() """
