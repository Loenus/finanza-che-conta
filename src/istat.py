import requests
import logging
import json
from constants import URL_ISTAT_API, HEADERS_JSON
from utils import get_last_day_of_previous_month
from requests.adapters import HTTPAdapter, Retry


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
        logging.info(f"## [INFLATION] ## Requesting ISTAT API at url: {URL_ISTAT_API} " +
                     f"| with params: {PARAMS} | with headers: {HEADERS_JSON}")
        
        s = requests.Session()
        retries = Retry(
            total=5, 
            backoff_factor=2, 
            status_forcelist=[ 500, 502, 503, 504 ],
            allowed_methods={'GET'}
        )
        s.mount('https://', HTTPAdapter(max_retries=retries))
        response = s.get(URL_ISTAT_API, params=PARAMS, headers=HEADERS_JSON, timeout=300)
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
