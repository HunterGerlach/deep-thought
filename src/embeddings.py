import os
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from typing import List, Union
from dotenv import load_dotenv

from src.config import *

load_dotenv()

class EmbeddingSource:
    def __init__(self):
        self.connection_string = CONNECTION_STRING
        self.collection_name = COLLECTION_NAME
        self.model_name = EMBEDDING_MODEL_NAME
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)

    def get_source(self, query: Union[str, List[str]], num_results: int) -> Union[dict, List[dict]]:
        try:
            db = PGVector(
                collection_name=self.collection_name,
                connection_string=self.connection_string,
                embedding_function=self.embeddings,
            )
        except Exception as e:
            return {'error': f"PostgreSQL connection failed: {str(e)}"}

        if isinstance(query, list):
            query = ' '.join(query)

        docs_with_score = db.similarity_search_with_score(query, k=num_results)
        results = [{'score': score, 'source': doc.metadata['source'], 'content': doc.page_content} for doc, score in docs_with_score]
        return results
