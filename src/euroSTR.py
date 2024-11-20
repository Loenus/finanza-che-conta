import logging
import requests
from bs4 import BeautifulSoup
from constants import URL_EU

def retrieve_euro_str():
    try:
        response = requests.get(URL_EU)
        soup = BeautifulSoup(response.content, "html.parser")
        euro_str_value = soup.find('td').strong.text
        if not euro_str_value:
            logging.warning('### [EURO STR] ### Valore di STR eur non trovato.')
            return 'not found'
        return euro_str_value
    except requests.exceptions.RequestException as e:
        logging.error(f"### [EURO STR] ### Errore nella richiesta API: {e}")
