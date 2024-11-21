from dotenv import load_dotenv
import logging
import os
from constants import DEFAULT_TIMEZONE

def load_config():
    load_dotenv()
    os.environ.setdefault('TIMEZONE', DEFAULT_TIMEZONE)
    TIMEZONE = os.getenv('TIMEZONE')
    if not TIMEZONE:
        os.environ['TIMEZONE'] = DEFAULT_TIMEZONE
        
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.getLogger('httpx').setLevel(logging.WARNING)
