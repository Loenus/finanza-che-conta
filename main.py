import os
import re
import requests
import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from telegram.ext import ContextTypes, Application
from dotenv import load_dotenv
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

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def check_jobs():
    job_names = [job.name for job in job_queue.jobs()]
    print(job_names)
    primo = job_queue.jobs()[0]
    next_run_time = primo.next_t
    print(f"Next run of the job is scheduled at: {next_run_time}")


### INFLATION ###

MONTHS = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

def retrieve_inflation(last_month_date): 
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
    percent_pattern = r"[-+]?\d+,\d+%"
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
    
    next_release_text = next_release_html.span.text
    day, month, year = next_release_text.split(' ')
    months_lower = [ x.lower() for x in MONTHS ]
    month_number = months_lower.index(month)
    next_release_date = datetime.datetime(int(year), month_number + 1, int(day), 8,1, tzinfo=ZoneInfo(TIMEZONE)) # at 8:01 of the specified timezone
    next_release_date += datetime.timedelta(days=1)
    logging.info(f"Next Release: {next_release_date}")
    job_inflation = job_queue.run_once(callback_inflation, next_release_date)
    
    return inflations, is_provisional

async def callback_inflation(context: ContextTypes.DEFAULT_TYPE):
    current_date = datetime.datetime.now(tz=ZoneInfo(TIMEZONE))
    last_month_name = MONTHS[current_date.month - 2]
    last_month_date = last_month_name + " " + str(current_date.year)
    if current_date.month == 1:
        last_month_date = last_month_name + " " + str(current_date.year -1)

    inflations, is_provisional = retrieve_inflation(last_month_date)
    if len(inflations) != 3:
        logging.warning(f"Qualcosa è andato storto nell'estrapolare i dati dell'inflazione dal testo: '{inflations[3]}'")
    
    # se il link già presente in chat, return (è il caso in cui il bot è stato aggiornato alla versione più recente)
    url_chat = 'https://t.me/s/' + CHANNEL_ID.replace('@','')
    response = requests.get(url_chat)
    if response.status_code != 200:
        logging.error(f"Errore nella richiesta HTTP [{response.status_code}]")
        return "Errore nella richiesta HTTP"
    soup = BeautifulSoup(response.content, "html.parser")
    arrr = soup.find("a", href = inflations[2])
    if arrr and ENV == "prod":
        logging.info('link già trovato in chat.')
        return

    provvisori = " (provvisori)" if is_provisional else ""
    message = f"""Secondo dati ISTAT{provvisori} in Italia a {last_month_date}:
Inflazione nel mese di {last_month_name}: {inflations[0]}
Inflazione nell'ultimo anno: {inflations[1]}
{inflations[2]}"""
    if len(inflations) >= 4:
        message += "\n\n" + inflations[3]
    
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message, disable_web_page_preview=True)
    #check_jobs()

#################


### EURO STR ###

URL_EU = "https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html"

def retrieve_euro_str():
    response = requests.get(URL_EU)
    if response.status_code != 200:
        logging.error(f"Errore nella richiesta HTTP [{response.status_code}]")
        return "Errore nella richiesta HTTP"
    soup = BeautifulSoup(response.content, "html.parser")
    euro_str_value = soup.find('td').strong.text
    if not euro_str_value:
        logging.warning('valore di STR eur non trovato.')
        return 'valore di STR eur non trovato.'
    return euro_str_value

async def callback_euro_str(context: ContextTypes.DEFAULT_TYPE):
    euro_str_value = retrieve_euro_str()
    message = f"Euro short-term rate (€STR) odierno: {euro_str_value}\n{URL_EU}"
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message)

################


job_inflation = job_queue.run_once(callback_inflation, datetime.datetime.now(tz=ZoneInfo(TIMEZONE)) + datetime.timedelta(seconds=3))
if ENV == "dev":
    job_euro_str = job_queue.run_repeating(callback_euro_str, datetime.timedelta(seconds=15), datetime.datetime.now(tz=ZoneInfo(TIMEZONE))+ datetime.timedelta(seconds=1))
else:
    d = datetime.datetime.now(tz=ZoneInfo(TIMEZONE))
    next_monday = next_weekday(d, 0).replace(hour=8,minute=0,second=0) # 0 = Monday, 1=Tuesday ..
    logging.info(f"Prima esecuzione per la ricerca dell'EURO STR schedulata per {str(next_monday)}. Successivamente ogni lunedì.")
    job_euro_str = job_queue.run_repeating(callback_euro_str, datetime.timedelta(weeks=1), next_monday)
application.run_polling()
