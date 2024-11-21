import requests
import logging
import json
from constants import URL_ISTAT_API, HEADERS_JSON
from utils import get_last_day_of_previous_month


def extract_values(data):
    # List comprehension
    values = [
        dataset['series'][key]['observations']['0'][0]
        for dataset in data['dataSets']
        for key in dataset['series']
        if key in ['0:0:0:0:0', '0:0:0:1:0']
    ]
    return values[0], values[1]


async def retrieve_inflation():
    """Ricerca info ISTAT riguardo l'indice dei prezzi al consumo 
    per l'intera collettività

    Returns
    -------
    var_congiunturale
        variazione percentuale congiunturale:
        variazione rispetto al mese esattamente precedente.
    var_tendenziale
        variazione percentuale tendenziale:
        variazione rispetto allo stesso mese dell'anno precedente.
        Anche definita "inflazione".
    Raises
    ------
    RequestException
        Se la richiesta fallisce
    JSONDecodeError
        Errore nel parsing del JSON di risposta
    Exception
        Errore generico, non previsto
    """

    try:
        PARAMS = { "startPeriod": get_last_day_of_previous_month() }
        response = requests.get(URL_ISTAT_API, params=PARAMS, headers=HEADERS_JSON)
        response.raise_for_status()  # Verifica se la risposta è OK
        logging.info(f"## [INFLATION] ## Response: {response.text}")
        data = response.json()
        return extract_values(data)

    except requests.exceptions.RequestException as e:
        logging.error(f"Errore nella richiesta API: {e}")

    except json.JSONDecodeError as e:
        logging.error(f"Errore nel parsing del JSON: {e}")
        return f"Errore nel parsing del JSON: {e}"

    except Exception as e:
        logging.error(f"Errore imprevisto: {e}")
        return f"Errore imprevisto: {e}"
