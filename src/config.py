"""Module to handle configuration and secrets."""

import os
from dotenv import load_dotenv

CONFIG_FILE = ".env.config"
SECRETS_FILE = ".env.secrets"

class Config:
    """Class to manage application configuration and secrets."""

    def __init__(self, config_file=CONFIG_FILE, secrets_file=SECRETS_FILE):
        """Initialize configuration by loading environment files."""
        load_dotenv(dotenv_path=config_file, override=True)
        load_dotenv(dotenv_path=secrets_file, override=True)

    def get(self, key, default=None):
        """Retrieve a configuration value by key.

        Args:
            key (str): The configuration key.
            default: The default value if the key is not found.

        Returns:
            The value associated with the key, or the default value.
        """
        return os.getenv(key, default)

    def get_secret(self, key, default=None, mask=True):
        """Retrieve a secret value by key, with optional masking.

        Args:
            key (str): The secret key.
            default: The default value if the key is not found.
            mask (bool): Whether to mask the secret value.

        Returns:
            The secret value (masked or unmasked), or the default value.
        """
        secret_value = os.getenv(key, default)
        return secret_value if not mask else "*****"
