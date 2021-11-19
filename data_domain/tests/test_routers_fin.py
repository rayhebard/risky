from unittest.mock import patch

import pytest

from backstop_dd.workers import tables
from rethinkdb import RethinkDB


def get_project_id(mock_db):
    """Get project from DB."""
    with mock_db.connect() as conn:
        projects = RethinkDB().db("Backstop").table(tables.projects).run(conn)
    return projects[0]["id"]


# pylint: disable=too-many-arguments
@patch("backstop_dd.workers.projections.rethinkdb_wrap")
@patch("backstop_dd.workers.assembler.rethinkdb_wrap")
@patch("backstop_dd.routers.fin.rethinkdb_wrap")
@patch("backstop_dd.routers.projects.rethinkdb_wrap")
def test_burn_projections(
    mocked_rethink_projects,
    mocked_rethink_fin,
    mocked_rethink_assembler,
    mocked_rethink_projections,
    mock_db,
    fast_api_mock_client,
):
    mocked_rethink_projects.return_value = mock_db
    mocked_rethink_fin.return_value = mock_db
    mocked_rethink_assembler.return_value = mock_db
    mocked_rethink_projections.return_value = mock_db
    path = "/fin/burn_projections/" + get_project_id(mock_db)
    response = fast_api_mock_client.get(path)
    assert response.status_code == 200


@pytest.mark.skip("test currenty not working.")
@patch("backstop_dd.workers.supplemental.rethinkdb_wrap")
@patch("backstop_dd.workers.budget_expenses.rethinkdb_wrap")
@patch("backstop_dd.workers.assembler.rethinkdb_wrap")
@patch("backstop_dd.routers.fin.rethinkdb_wrap")
@patch("backstop_dd.routers.projects.rethinkdb_wrap")
def test_graph_data(
    mocked_rethink_projects,
    mocked_rethink_fin,
    mocked_rethink_assembler,
    mocked_rethink_budget_expenses,
    mocked_rethink_budget_supplememtal,
    mock_db,
    fast_api_mock_client,
):
    mocked_rethink_projects.return_value = mock_db
    mocked_rethink_fin.return_value = mock_db
    mocked_rethink_assembler.return_value = mock_db
    mocked_rethink_budget_expenses.return_value = mock_db
    mocked_rethink_budget_supplememtal.return_value = mock_db
    path = "/fin/graph_data/" + get_project_id(mock_db)
    response = fast_api_mock_client.get(path)
    assert response.status_code == 200


@pytest.mark.skip("test currenty not working.")
def test_load_spreadsheets(fast_api_mock_client):
    path = "/fin/spreadsheets/" + tables.financial_summary_header
    response = fast_api_mock_client.post(path)
    assert response.status_code == 200
    assert len(response.json()) > 0


@patch("backstop_dd.routers.fin.rethinkdb_wrap")
def test_read_supplemental(mocked_rethink, mock_db, fast_api_mock_client):
    mocked_rethink.return_value = mock_db
    path = "/fin/supplemental"
    response = fast_api_mock_client.get(path)
    assert response.status_code == 200
