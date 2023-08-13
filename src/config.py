from dotenv import load_dotenv
import os

CONFIG_FILE = "src/.env.config"
SECRETS_FILE = "src/.env.secrets"

class Config:
    def __init__(self, config_file=CONFIG_FILE, secrets_file=SECRETS_FILE):
        load_dotenv(dotenv_path=config_file, override=True)
        load_dotenv(dotenv_path=secrets_file, override=True)

    def get(self, key, default=None):
        return os.getenv(key, default)

    def get_secret(self, key, default=None, mask=True):
        secret_value = os.getenv(key, default)
        return secret_value if not mask else "*****"
