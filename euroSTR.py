import logging #in py it's a singleton, so it has the same configuration of main.py
import requests
from bs4 import BeautifulSoup
from constants import URL_EU

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