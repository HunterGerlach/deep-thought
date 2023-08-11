import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import logging

from src.main import app, call_openai, get_bot_response

class TestMain(unittest.TestCase):

    def setUp(self):
        self.app = TestClient(app)
        logging.getLogger().setLevel(logging.WARNING)

    @patch('src.main.LLMChain')
    @patch('src.main.OpenAI')
    @patch('src.main.PromptTemplate')
    def test_call_openai(self, MockPromptTemplate, MockOpenAI, MockLLMChain):
        mock_chain = MockLLMChain.return_value
        mock_chain.run.return_value = 'Test response'
        response = call_openai('test_input')
        self.assertEqual(response, 'Test response')

    @patch('src.main.call_openai')
    def test_get_bot_response_hello(self, mock_call_openai):
        mock_call_openai.return_value = 'Hi there!'
        response = get_bot_response('hello')
        self.assertEqual(response, 'Hi there!')

    def test_get_bot_response_name(self):
        response = get_bot_response('what is your name?')
        self.assertEqual(response, 'My name is Chat Bot!')

    @patch('src.main.call_openai')
    def test_get_bot_response_other(self, mock_call_openai):
        mock_call_openai.return_value = 'OpenAI response'
        response = get_bot_response('other_input')
        self.assertEqual(response, 'OpenAI response')

    def test_handle_request_get(self):
        response = self.app.get('/')
        self.assertEqual(response.json(), {'error': 'Only POST requests are allowed'})

    @patch('src.main.get_bot_response')
    def test_handle_request_post(self, mock_get_bot_response):
        mock_get_bot_response.return_value = 'Bot response'
        response = self.app.post('/', json={'user_input': 'test_input'})
        self.assertEqual(response.json(), {'bot_response': 'Bot response'})

    @patch('src.main.EmbeddingSource')
    def test_get_embedding_source(self, MockEmbeddingSource):
        mock_get_source = MockEmbeddingSource.return_value.get_source
        mock_get_source.return_value = 'Test response'
        response = self.app.post('/get_embedding_sources', json={'query': 'test_query', 'num_results': 5})
        self.assertEqual(response.json(), {'embedding_source': 'Test response'})

    @patch('src.main.call_openai')
    @patch('src.main.EmbeddingSource')
    def test_synthesize_response(self, MockEmbeddingSource, mock_call_openai):
        mock_get_source = MockEmbeddingSource.return_value.get_source
        mock_get_source.return_value = [{'source': 'test_source', 'content': 'test_content'}]
        mock_call_openai.return_value = 'OpenAI response'
        response = self.app.post('/synthesize_response', json={'query': 'test_query', 'num_results': 5})
        self.assertEqual(response.json(), {'bot_response': 'OpenAI response\n\nPossibly Related Sources:\n<a href="#">test_source</a>'})

if __name__ == "__main__":
    unittest.main()
