import sys
import json
import requests
from multiprocessing import Process
import shutil
import argparse
import os

import src.scripts.api_spec_validator.specification_comparer as specification_comparer
import src.scripts.api_spec_validator.server_manager as server_manager
from src.logging_setup import setup_logger

logger = setup_logger()

def parse_args():
    parser = argparse.ArgumentParser(description='Compare OpenAPI Specifications.')
    parser.add_argument('--server-host', default=os.getenv('SERVER_HOST', '127.0.0.1'), help='Host of the FastAPI server.')
    parser.add_argument('--server-port', type=int, default=int(os.getenv('SERVER_PORT', 8000)), help='Port of the FastAPI server.')
    parser.add_argument('--server-url', default=os.getenv('SERVER_URL', 'http://127.0.0.1:8000/openapi.json'), help='URL of the FastAPI server.')
    parser.add_argument('--spec-file', required=True, help='Path to the OpenAPI specification file.')
    parser.add_argument('--ignore-keys', nargs='*', default=[os.getenv('SPEC_KEYS_TO_IGNORE', "")], help='List of keys to ignore during comparison.')
    parser.add_argument('--timeout', type=int, default=int(os.getenv('TIMEOUT', 10)), help='Timeout for waiting for the server.')
    return parser.parse_args()

def main():
    try:
        args = parse_args()

        column_width = int(shutil.get_terminal_size().columns / 2)

        comparer = specification_comparer.SpecificationComparer(column_width, args.ignore_keys)

        server = server_manager.ServerManager(args.server_host, args.server_port, args.server_url, args.timeout)

        server_process = Process(target=server.start_server, args=(args.server_host, args.server_port))
        server_process.start()

        if not server.wait_for_server(args.server_url, args.timeout):
            logger.error("Server was not ready, exiting...")
            server_process.terminate()
            sys.exit(1)

        logger.info("Fetching JSON from FastAPI endpoint...")
        try:
            response = requests.get(args.server_url)
            response.raise_for_status()
            obj1 = response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching JSON from FastAPI endpoint: {e}")
            server.terminate()
            sys.exit(1)

        try:
            with open(args.spec_file) as f2:
                obj2 = json.load(f2)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading local JSON file for comparison: {e}")
            server_process.terminate()
            sys.exit(1)

        logger.info("Comparing objects...")
        exit_code = comparer.compare_objects(obj1, obj2)

        server_process.terminate()

        return exit_code
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
