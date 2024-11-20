from dotenv import load_dotenv
import logging

def load_config():
    load_dotenv()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.getLogger('httpx').setLevel(logging.WARNING)

load_config()