from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "text-davinci-002")
OPENAI_MODEL_PRICE = os.getenv("OPENAI_MODEL_PRICE", "0.000006")
TOKENIZERS_PARALLELISM = os.getenv("TOKENIZERS_PARALLELISM", "false")

SPEND_LOG_FILE = os.getenv("SPEND_LOG_FILE", "spend.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
