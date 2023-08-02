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


application = Application.builder().token(os.environ.get('BOT_TOKEN')).build()
job_queue = application.job_queue

def retrieve_inflation(last_month_date): 
    URL = "https://www.istat.it/it/prezzi"
    response = requests.get(URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        news_list = soup.find("div", {"id": "main-content"})
        if news_list:
            title_to_find = "Prezzi al consumo (provvisori) - " + last_month_date
            logging.info(title_to_find)
            article = news_list.find("a", {"title": title_to_find}) # find( lambda tag: tag.name == "a" and "VALORE_TITLE_SPECIFICO" in tag.get("title", "") )
            if article:
                url_article = article['href']
                inflation_text = article.text
                logging.info(f"Link trovato: {url_article}")
                logging.info(f"Cosa dice: {inflation_text}")

                # estrapolo solo l'inflazione percentuale
                percent_pattern = r"[-+]?\d+,\d+%"
                inflations = re.findall(percent_pattern, inflation_text)
                return inflations
            else:
                logging.warning(f"Nessun elemento a trovato con il valore title '{title_to_find}'")
                return f"Nessun elemento a trovato con il valore title '{title_to_find}'"
        else:
            logging.warning("Nessun elemento div trovato con ID 'main-content'")
            return "Nessun elemento div trovato con ID 'main-content'"
    else:
        logging.error("Errore nella richiesta HTTP")
        return "Errore nella richiesta HTTP"

async def callback_month(context: ContextTypes.DEFAULT_TYPE):
    current_date = datetime.datetime.now()
    month_array = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
    last_month_name = month_array[current_date.month - 2] # -1 perché current_date.month è [1,12] e month_array è [0,11], -1 perché il primo del mese deve riferirsi al mese passato
    last_month_date = last_month_name + " " + str(current_date.year)
    if current_date.month == 1:
        last_month_date = last_month_name + " " + str(current_date.year -1)

    inflations = retrieve_inflation(last_month_date)
    if len(inflations) != 2:
        logging.warning("Qualcosa è andato storto nell'estrapolare i dati dell'inflazione dal testo. " + str(inflations))
    message = f"""Secondo dati ISTAT (provvisori) in Italia a {last_month_date}:
Inflazione nel mese di {last_month_name}: {inflations[0]}
Inflazione nell'ultimo anno: {inflations[1]}"""

    CHANNEL_ID = os.environ.get('CHANNEL_ID')
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message)

data_check = datetime.time(14,23)
job_month = job_queue.run_monthly(callback_month, data_check, 2)

application.run_polling()