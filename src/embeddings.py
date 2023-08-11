import os
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from typing import List, Union
from dotenv import load_dotenv

load_dotenv()

class EmbeddingSource:
    def __init__(self):
        self.connection_string = os.getenv('CONNECTION_STRING', "postgresql://default_connection_string")
        self.collection_name = os.getenv('COLLECTION_NAME', "default_collection")
        self.model_name = os.getenv('MODEL_NAME', "all-MiniLM-L6-v2")
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
