import os

from typing import List, Union
from dotenv import load_dotenv

from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings

from src.config import *
from src.logging_setup import setup_logger

load_dotenv()

logger = setup_logger()

class EmbeddingSource:    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    def get_source(self, query: Union[str, List[str]], num_results: int) -> Union[dict, List[dict]]:
        logger.debug(f"EMBEDDING_MODEL_NAME: {EMBEDDING_MODEL_NAME}")
        logger.debug(f"CONNECTION_STRING: {CONNECTION_STRING}")
        logger.debug(f"COLLECTION_NAME: {COLLECTION_NAME}")
        logger.debug(f"query: {query}, num_results: {num_results}")
        try:
            db = PGVector(
                collection_name=COLLECTION_NAME,
                connection_string=CONNECTION_STRING,
                embedding_function=self.embeddings,
            )
        except Exception as e:
            return {'error': f"PostgreSQL connection failed: {str(e)}"}

        if isinstance(query, list):
            query = ' '.join(query)

        docs_with_score = db.similarity_search_with_score(query, k=num_results)
        results = [{'score': score, 'source': doc.metadata['source'], 'content': doc.page_content} for doc, score in docs_with_score]
        return results
