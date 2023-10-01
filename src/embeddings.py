"""Module for handling embeddings."""

from typing import List, Union
from fastapi import HTTPException

from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings

from config import Config
from logging_setup import setup_logger

config = Config()
logger = setup_logger()

embedding_model_name = config.get('EMBEDDING_MODEL_NAME', "all-MiniLM-L6-v2")

class EmbeddingSource: # pylint: disable=R0903
    """Class to handle embedding sources."""

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

    def get_source(self, query: Union[str, List[str]], num_results: int) -> Union[dict, List[dict]]:
        """Retrieve source based on the query.

        Args:
            query: The query text or list of texts.
            num_results: Number of results to retrieve.

        Returns:
            A dictionary or list of dictionaries containing the results.
        """
        logger.debug("EMBEDDING_MODEL_NAME: %s", embedding_model_name)
        connection_string = config.get_secret(
            'CONNECTION_STRING', "postgresql://UNDEFINED", mask=False)
        logger.debug("CONNECTION_STRING: %s", config.get_secret('CONNECTION_STRING'))
        collection_name = config.get('COLLECTION_NAME', "sample_collection")
        logger.debug("COLLECTION_NAME: %s", collection_name)
        logger.debug("query: %s, num_results: %s", query, num_results)
        try:
            database = PGVector(
                collection_name=collection_name,
                connection_string=connection_string,
                embedding_function=self.embeddings,
            )
        except ConnectionError as err:
            error_message = f'PostgreSQL connection failed: {str(err)}'
            logger.warning(error_message)
            raise HTTPException(status_code=401, detail="PostgreSQL connection failed") from err
        except Exception as err: # pylint: disable=W0703
            error_message = f'PostgreSQL connection failed: {str(err)}'
            logger.warning(error_message)
            raise HTTPException(status_code=401, detail="PostgreSQL connection failed") from err

        if isinstance(query, list):
            query = ' '.join(query)

        docs_with_score = database.similarity_search_with_score(query, k=num_results)
        results = [{'score': score, 'source': doc.metadata['source'], 'content': doc.page_content}
                   for doc, score in docs_with_score]
        return results
