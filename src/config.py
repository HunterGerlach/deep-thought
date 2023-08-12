from dotenv import load_dotenv
import os

load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "vertex")

VERTEX_MODEL_NAME = os.getenv("VERTEX_MODEL_NAME", "text-bison")

API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "text-davinci-002")
OPENAI_MODEL_PRICE = os.getenv("OPENAI_MODEL_PRICE", "0.000006")
TOKENIZERS_PARALLELISM = os.getenv("TOKENIZERS_PARALLELISM", "false")

SPEND_LOG_FILE = os.getenv("SPEND_LOG_FILE", "spend.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

CONNECTION_STRING = os.getenv("CONNECTION_STRING", "postgresql://default_connection_string")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "default_connection_name")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")