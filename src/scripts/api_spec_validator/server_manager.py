import requests
import time
import uvicorn
from src.logging_setup import setup_logger

logger = setup_logger()

class ServerManager:
    def __init__(self, host, port, url, timeout=10):
        self.host = host
        self.port = port
        self.url = url
        self.timeout = timeout
        self.process = None

    def start_server(self, host, port):
        logger.info(f"Starting FastAPI server on {host}:{port}...")
        uvicorn.run("src.app:app", host=host, port=port)

    def wait_for_server(self, url, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url)
                response.raise_for_status()
                if response.status_code == 200:
                    logger.info("Server is ready!")
                    return True
            except requests.RequestException as e:
                logger.warning(f"Server not ready, waiting... Error: {e}")
                time.sleep(1)
        logger.error("Timed out waiting for server.")
        return False
    
    def terminate(self):
        logger.info("Terminating the server process...")
        try:
            self.process.terminate()
        except Exception as e:
            logger.error(f"Error terminating server process: {e}")
        logger.info("Done.")
