import json
from unittest.mock import patch

import pytest


# pylint: disable=unused-argument
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, data, status_code):
            self.data = data
            self.status_code = status_code
            self.text = json.dumps(data)

        def json(self):
            return self.data

    resp = None
    if args[0].endswith("/projects"):
        resp = [{"PROJ": []}]
    elif args[0].endswith("/calculations"):
        resp = [{"CALC": []}]
    elif args[0].endswith("/chiefs"):
        resp = [{"CHIEFS": []}]

    if resp is None:
        return MockResponse(None, 404)

    return MockResponse(resp, 200)


def test_read_root(fast_api_mock_client):
    response = fast_api_mock_client.get("/edge/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Back Stop Edge Service"}


@patch("edge.main.requests.get")
def test_read_project(mocked_get, fast_api_mock_client):
    mocked_get.side_effect = mocked_requests_get
    response = fast_api_mock_client.get("/edge/projects")
    assert response.status_code == 200
    assert response.json()[0] == {"PROJ": []}


@patch("edge.main.requests.get")
def test_read_project_calculations(mocked_get, fast_api_mock_client):
    mocked_get.side_effect = mocked_requests_get
    response = fast_api_mock_client.get("/edge/calculations")
    assert response.status_code == 200
    assert response.json()[0] == {"CALC": []}


@pytest.mark.skip("Not implemented at this time")
def test_read_deliverable_by_charge_number():
    assert True


@patch("edge.main.requests.get")
def test_read_chiefs(mocked_get, fast_api_mock_client):
    mocked_get.side_effect = mocked_requests_get
    response = fast_api_mock_client.get("/edge/chiefs")
    assert response.status_code == 200
    assert response.json()[0] == {"CHIEFS": []}


@pytest.mark.skip("Not implemented at this time")
def test_read_funds():
    assert True
