import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.v2.endpoints import router

client = TestClient(router)

class TestMain(unittest.TestCase):

    def test_read_items(self):
        response = client.get("/api_version_test/")
        assert response.status_code == 200
        assert response.json() == [{"version": "V2"}]

if __name__ == "__main__":
    unittest.main()
