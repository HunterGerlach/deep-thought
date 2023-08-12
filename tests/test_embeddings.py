import unittest
from unittest.mock import patch, MagicMock
import logging

from src.embeddings import EmbeddingSource

class TestEmbeddingSource(unittest.TestCase):

    def setUp(self):
        logging.getLogger().setLevel(logging.WARNING)

    @patch('src.embeddings.PGVector')
    def test_get_source(self, MockPGVector):
        mock_doc = MagicMock()
        mock_doc.metadata = {'source': 'test_source'}
        mock_doc.page_content = 'test_content'
        mock_db = MockPGVector.return_value
        mock_db.similarity_search_with_score.return_value = [(mock_doc, 'test_score')]
        embedding_source = EmbeddingSource()
        results = embedding_source.get_source('test_query', 5)
        expected_results = [{'score': 'test_score', 'source': 'test_source', 'content': 'test_content'}]
        self.assertEqual(results, expected_results)

    @patch('src.embeddings.PGVector')
    def test_get_source_exception(self, MockPGVector):
        MockPGVector.side_effect = Exception('test_exception')
        embedding_source = EmbeddingSource()
        results = embedding_source.get_source('test_query', 5)
        self.assertEqual(results, {'error': 'PostgreSQL connection failed: test_exception'})

if __name__ == "__main__":
    unittest.main()
