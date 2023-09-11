import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import logging

from src.v1.endpoints import router, call_language_model, get_bot_response
from src.v1.endpoints import token_cost, calculate_total_spent, spend_limit_exceeded

class TestMain(unittest.TestCase):

    def setUp(self):
        self.app = TestClient(router)
        logging.getLogger().setLevel(logging.WARNING)

    #TODO
    def test_call_vertexai(self):
        pass

    #TODO
    def test_call_openai(self):
        pass

    @patch('src.v1.endpoints.call_language_model')
    def test_get_bot_response_hello(self, mock_call_language_model):
        mock_call_language_model.return_value = 'Hi there!'
        response = get_bot_response('hello')
        self.assertEqual(response, 'Hi there!')

    def test_get_bot_response_name(self):
        response = get_bot_response('what is your name?')
        self.assertEqual(response, 'My name is Chat Bot!')

    @patch('src.v1.endpoints.call_language_model')
    def test_get_bot_response_other(self, mock_call_language_model):
        mock_call_language_model.return_value = 'Language model response'
        response = get_bot_response('other_input')
        self.assertEqual(response, 'Language model response')

    def test_handle_request_get(self):
        response = self.app.get('/')
        self.assertEqual(response.json(), {'error': 'Only POST requests are allowed'})

    @patch('src.v1.endpoints.get_bot_response')
    def test_handle_request_post(self, mock_get_bot_response):
        mock_get_bot_response.return_value = 'Bot response'
        response = self.app.post('/', json={'user_input': 'test_input'})
        self.assertEqual(response.json(), {'bot_response': 'Bot response'})

    @patch('src.v1.endpoints.EmbeddingSource')
    def test_find_sources(self, MockEmbeddingSource):
        mock_get_source = MockEmbeddingSource.return_value.get_source
        mock_get_source.return_value = 'Test response'
        response = self.app.post('/find_sources', json={'query': 'test_query', 'num_results': 5})
        self.assertEqual(response.json(), {'find_sources': 'Test response'})

    @patch('src.v1.endpoints.call_language_model')
    @patch('src.v1.endpoints.EmbeddingSource')
    def test_ask(self, MockEmbeddingSource, mock_call_language_model):
        mock_get_source = MockEmbeddingSource.return_value.get_source
        mock_get_source.return_value = [{'source': 'test_source', 'content': 'test_content'}]
        mock_call_language_model.return_value = 'Language model response'
        response = self.app.post('/ask', json={'query': 'test_query', 'num_results': 5})
        self.assertEqual(response.json(), {'bot_response': 'Language model response\n\nPossibly Related Sources:\n<a href="#">test_source</a>'})

    @patch('src.v1.endpoints.calculate_total_spent', return_value=0.0005)
    @patch('src.v1.endpoints.config.get', side_effect=lambda x, y: '0.001' if x == 'SPEND_LIMIT' else y)
    def test_spend_limit_exceeded(self, mock_config, mock_total_spent):
        result = spend_limit_exceeded()
        self.assertEqual(result, False)



if __name__ == "__main__":
    unittest.main()
