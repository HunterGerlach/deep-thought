"""Module to manage a FastAPI server."""

import time
import requests
import uvicorn
from src.logging_setup import setup_logger

logger = setup_logger()

class ServerManager:
    """Class to manage the starting, waiting, and terminating of a FastAPI server."""

    def __init__(self, host, port, url, timeout=10):
        self.host = host
        self.port = port
        self.url = url
        self.timeout = timeout
        self.process = None

    def start_server(self, host_param, port_param):
        """Start the FastAPI server."""
        logger.info("Starting FastAPI server on %s:%s...", host_param, port_param)
        uvicorn.run("src.app:app", host=host_param, port=port_param)

    def wait_for_server(self, url, timeout=10):
        """Wait for the server to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                if response.status_code == 200:
                    logger.info("Server is ready!")
                    return True
            except requests.RequestException as err:
                logger.warning("Server not ready, waiting... Error: %s", err)
                time.sleep(1)
        logger.error("Timed out waiting for server.")
        return False

    def terminate(self):
        """Terminate the server process."""
        logger.info("Terminating the server process...")
        try:
            self.process.terminate()
        except AttributeError as err:
            logger.error("Error terminating server process: Process not initialized: %s", err)
        except OSError as err:
            logger.error("Error terminating server process: Operating system error: %s", err)
        except Exception as err: # pylint: disable=W0718
            logger.error("Error terminating server process: Unexpected error: %s", err)
        logger.info("Done.")
