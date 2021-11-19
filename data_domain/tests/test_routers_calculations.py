from unittest.mock import patch

import pytest


@patch("backstop_dd.routers.calculations.rethinkdb_wrap")
def test_read_calculations(mocked_rethink_calculations, mock_db, fast_api_mock_client):
    mocked_rethink_calculations.return_value = mock_db
    response = fast_api_mock_client.get("/calculations")
    assert response.status_code == 200


# pylint: disable=too-many-arguments
@pytest.mark.skip(
    "test is not currently working - query_current is list, expects .items"
)
@patch("backstop_dd.workers.financials.get_last")
@patch("backstop_dd.workers.financials.get_current")
@patch("backstop_dd.workers.financials.rethinkdb_wrap")
@patch("backstop_dd.routers.projects.rethinkdb_wrap")
@patch("backstop_dd.routers.calculations.rethinkdb_wrap")
def test_generate_project_calculations(
    mocked_rethink_calculations,
    mocked_rethink_projects,
    mocked_rethink_financials,
    mock_get_current,
    mock_get_last,
    mock_db,
    fast_api_mock_client,
):
    # TODO test fails cause in /workers/financials.py, ln 79 query_current is a list but
    # the code tries to access query_current.items. I am thinking that with real RTDB it is some
    # kind of RT object but with the mock it is coming back as a list
    mocked_rethink_projects.return_value = mock_db
    mocked_rethink_calculations.return_value = mock_db
    mocked_rethink_financials.return_value = mock_db
    mock_get_last.return_value = "02/2021"
    mock_get_current.return_value = "03/2021"

    response = fast_api_mock_client.post("/calculations")
    assert response.status_code == 200
    assert len(response.json()) > 0
