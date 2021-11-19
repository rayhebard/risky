import json
import os
from unittest.mock import patch

import pytest

from backstop_dd.workers import tables
from rethinkdb import RethinkDB

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


def get_project_id(mock_db):
    """Get project from DB."""
    with mock_db.connect() as conn:
        projects = RethinkDB().db("Backstop").table(tables.projects).run(conn)
    return projects[0]["id"]


# create a risk review test example
risk_review_example = {
    "id": "123",
    "project_id": "string",
    "technical": "string",
    "staffing": "string",
    "financial": "string",
    "contract_customer_sat": "string",
    "technical_customer_sat": "string",
    "future_funding": "string",
    "general_comments": "string",
    "contract_customer_sat_comments": ["string"],
    "technical_customer_sat_comments": ["string"],
}


@patch("backstop_dd.routers.projects.rethinkdb_wrap")
def test_read_projects(mocked_rethink_projects, mock_db, fast_api_mock_client):
    mocked_rethink_projects.return_value = mock_db
    path = "/projects"
    response = fast_api_mock_client.get(path)
    assert response.status_code == 200


@patch("backstop_dd.routers.projects.rethinkdb_wrap")
def test_read_project(mocked_rethink_projects, mock_db, fast_api_mock_client):
    mocked_rethink_projects.return_value = mock_db
    path = "/project/" + get_project_id(mock_db)
    response = fast_api_mock_client.get(path)
    assert response.status_code == 200


@pytest.mark.skip("test currenty not working.")
@patch("backstop_dd.routers.projects.rethinkdb_wrap")
def test_refresh_projects(mocked_rethink_projects, mock_db, fast_api_mock_client):
    mocked_rethink_projects.return_value = mock_db
    path = "/projects"
    response = fast_api_mock_client.post(path)
    assert response.status_code == 200
    assert len(response.json()) > 0


@patch("backstop_dd.routers.projects.rethinkdb_wrap")
def test_get_risk_reviews(mocked_rethink_projects, mock_db, fast_api_mock_client):
    mocked_rethink_projects.return_value = mock_db
    path = "/projects/risk_reviews"
    response = fast_api_mock_client.get(path)
    assert response.status_code == 200


@patch("backstop_dd.routers.projects.rethinkdb_wrap")
def test_get_risk_reviews_history(
    mocked_rethink_projects, mock_db, fast_api_mock_client
):
    mocked_rethink_projects.return_value = mock_db
    path = "/projects/risk_reviews_history"
    response = fast_api_mock_client.get(path)
    assert response.status_code == 200


@pytest.mark.skip("test currenty not working.")
@patch("backstop_dd.routers.projects.rethinkdb_wrap")
def test_save_risk_review(mocked_rethink_projects, mock_db, fast_api_mock_client):
    # TODO getting error in rethinkdb_mock.rql_rewrite.handle_contains where it tries to
    # access the 2nd entry in a list and returns  IndexError: list index out of range
    # seems like maybe .contains() needs a param? ()
    mocked_rethink_projects.return_value = mock_db
    path = "/projects/risk_review/0c041ca9-b749-4a2c-8804-e7091b672c8d"
    response = fast_api_mock_client.post(
        path,
        headers={"Content-type": "application/json"},
        data=json.dumps(risk_review_example),
    )

    assert response.status_code == 200
    assert (
        response.json()["current"]["inserted"] == 1
        or response.json()["history"]["inserted"] == 1
    )
