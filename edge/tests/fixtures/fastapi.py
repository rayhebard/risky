import pytest
from fastapi.testclient import TestClient

from edge.main import app


@pytest.fixture(scope="module")
def fast_api_mock_client():
    return TestClient(app)
