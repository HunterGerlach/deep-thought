"""Module to compare OpenAPI specifications and manage FastAPI server."""

import sys
import json
import os
import shutil
import argparse
from multiprocessing import Process

import requests

from src.scripts.api_spec_validator.specification_comparer import SpecificationComparer
from src.scripts.api_spec_validator.server_manager import ServerManager
from src.logging_setup import setup_logger

logger = setup_logger()

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Compare OpenAPI Specifications.')
    parser.add_argument('--server-host',
                        default=os.getenv('SERVER_HOST', '127.0.0.1'),
                        help='Host of the FastAPI server.')
    parser.add_argument('--server-port',
                        type=int,
                        default=int(os.getenv('SERVER_PORT', '8080')),
                        help='Port of the FastAPI server.')
    parser.add_argument('--server-url',
                        default=os.getenv('SERVER_URL', 'http://127.0.0.1:8080/openapi-v1.json'),
                        help='URL of the FastAPI server.')
    parser.add_argument('--spec-file',
                        required=True,
                        help='Path to the OpenAPI specification file.')
    parser.add_argument('--ignore-keys',
                        nargs='*',
                        default=os.getenv('SPEC_KEYS_TO_IGNORE', "").split(),
                        help='List of keys to ignore during comparison.')
    parser.add_argument('--timeout',
                        type=int,
                        default=int(os.getenv('TIMEOUT', '10')),
                        help='Timeout for waiting for the server.')
    return parser.parse_args()

def main():
    """Main function to run the comparison and manage the server."""
    try:
        args = parse_args()

        column_width = int(shutil.get_terminal_size().columns / 2)

        comparer = SpecificationComparer(column_width, args.ignore_keys)

        server = ServerManager(args.server_host, args.server_port, args.server_url, args.timeout)

        server_process = Process(target=server.start_server,
                         args=(args.server_host, args.server_port))

        server_process.start()

        if not server.wait_for_server(args.server_url, args.timeout):
            logger.error("Server was not ready, exiting...")
            server_process.terminate()
            sys.exit(1)

        logger.info("Fetching JSON from FastAPI endpoint...")
        try:
            response = requests.get(args.server_url, timeout=args.timeout)
            logger.error("Server was not ready, exiting1... %s", response)
            response.raise_for_status()
            logger.error("Server was not ready, exiting2... %s", response)
            obj1 = response.json()
            print(obj1)
            logger.error("Server was not ready, exiting3... %s", response)
        except requests.RequestException as err:
            logger.error("Error fetching JSON from FastAPI endpoint: %s", err)
            server.terminate()
            sys.exit(1)

        try:
            with open(args.spec_file, encoding='utf-8') as file_obj:
                obj2 = json.load(file_obj)
        except (FileNotFoundError, json.JSONDecodeError) as err:
            logger.error("Error loading local JSON file for comparison: %s", err)
            server_process.terminate()
            sys.exit(1)

        logger.info("Comparing objects...")
        exit_code = comparer.compare_objects(obj1, obj2)

        server_process.terminate()

        return exit_code
    except Exception as err: # pylint: disable=W0703
        logger.error("An unexpected error occurred: %s", err)
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
