import os

from typing import List, Union

from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings

from src.config import Config
from src.logging_setup import setup_logger

config = Config()
logger = setup_logger()

embedding_model_name = config.get('EMBEDDING_MODEL_NAME', "all-MiniLM-L6-v2")

class EmbeddingSource:    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    
    def get_source(self, query: Union[str, List[str]], num_results: int) -> Union[dict, List[dict]]:
        logger.debug(f"EMBEDDING_MODEL_NAME: {embedding_model_name}")
        connection_string = config.get_secret('CONNECTION_STRING', "postgresql://UNDEFINED", mask=False)
        logger.debug(f"CONNECTION_STRING: {config.get_secret('CONNECTION_STRING')}")
        collection_name = config.get('COLLECTION_NAME', "sample_collection")
        logger.debug(f"COLLECTION_NAME: {collection_name}")
        logger.debug(f"query: {query}, num_results: {num_results}")
        try:
            db = PGVector(
                collection_name=collection_name,
                connection_string=connection_string,
                embedding_function=self.embeddings,
            )
        except Exception as e:
            return {'error': f"PostgreSQL connection failed: {str(e)}"}

        if isinstance(query, list):
            query = ' '.join(query)

        docs_with_score = db.similarity_search_with_score(query, k=num_results)
        results = [{'score': score, 'source': doc.metadata['source'], 'content': doc.page_content} for doc, score in docs_with_score]
        return results
