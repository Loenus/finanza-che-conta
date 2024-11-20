import requests
import logging
import json

API_URL = "https://sdmx.istat.it/SDMXWS/rest/data/167_744/M.00.IT.7.39/"
PARAMS = {
    "startPeriod": "2024-10-31"
}
HEADERS = {
    "Accept": "application/json"
}

async def retrieve_inflation():
    """Ricerca info ISTAT riguardo l'indice dei prezzi al consumo per l'intera collettività

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
    KeyError
        Chiave specificata non presente nel JSON
    IndexError
        Indice non presente nel JSON
    TypeError
        Errore di tipo nei dati JSON
    Exception
        Errore generico, non previsto
    """

    try:
        # Esegui la chiamata all'API
        response = requests.get(API_URL, params=PARAMS, headers=HEADERS)
        response.raise_for_status()  # Verifica se la risposta è OK

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
