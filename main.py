import os
import re
import requests
import datetime
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

CHANNEL_ID = os.environ.get('CHANNEL_ID')
application = Application.builder().token(os.environ.get('BOT_TOKEN')).build()
job_queue = application.job_queue

def check_jobs():
    job_names = [job.name for job in job_queue.jobs()]
    print(job_names)
    primo = job_queue.jobs()[0]
    next_run_time = primo.next_t
    print(f"Next run of the job is scheduled at: {next_run_time}")


### INFLATION ###

MONTHS = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
data_check = datetime.time(10,25, second=30)
day_check = 3

def retrieve_inflation(last_month_date): 
    URL_ISTAT = "https://www.istat.it"
    response = requests.get(URL_ISTAT + "/it/prezzi")
    if response.status_code != 200:
        logging.error(f"Errore nella richiesta HTTP [{response.status_code}]")
        return "Errore nella richiesta HTTP", None

    # Trovo l'articolo
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
        job_inflation = job_queue.run_once(callback_inflation, datetime.timedelta(seconds=5))
        inflations.append(error_message)
        return inflations, is_provisional
    
    next_release_text = next_release_html.span.text
    day, month, year = next_release_text.split(' ')
    months_lower = [ x.lower() for x in MONTHS ]
    month_number = months_lower.index(month)
    next_release_date = datetime.datetime(int(year), month_number + 1, int(day), 8,1)
    next_release_date += datetime.timedelta(days=1)
    logging.info(f"Next Release: {next_release_date}")
    job_inflation = job_queue.run_once(callback_inflation, next_release_date)
    
    return inflations, is_provisional

async def callback_inflation(context: ContextTypes.DEFAULT_TYPE):
    current_date = datetime.datetime.now()
    last_month_name = MONTHS[current_date.month - 2]
    last_month_date = last_month_name + " " + str(current_date.year)
    if current_date.month == 1:
        last_month_date = last_month_name + " " + str(current_date.year -1)

    inflations, is_provisional = retrieve_inflation(last_month_date)
    if len(inflations) != 2:
        logging.warning(f"Qualcosa è andato storto nell'estrapolare i dati dell'inflazione dal testo: '{str(inflations)}'")
    
    provvisori = " (provvisori)" if is_provisional else ""
    message = f"""Secondo dati ISTAT{provvisori} in Italia a {last_month_date}:
Inflazione nel mese di {last_month_name}: {inflations[0]}
Inflazione nell'ultimo anno: {inflations[1]}"""
    if inflations[2]:
        message += "\n" + inflations[2]
    
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message)
    #check_jobs()

#################


job_inflation = job_queue.run_once(callback_inflation, datetime.datetime.now() - datetime.timedelta(hours=2) + datetime.timedelta(seconds=3))
application.run_polling()
