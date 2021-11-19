from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backstop_dd.main import app


# pylint: disable=too-many-arguments
@pytest.fixture(scope="module")
@patch("backstop_dd.init_db.rethinkdb_wrap")
@patch("backstop_dd.routers.calculations.rethinkdb_wrap")
@patch("backstop_dd.routers.chiefs.rethinkdb_wrap")
@patch("backstop_dd.routers.fin.rethinkdb_wrap")
@patch("backstop_dd.routers.projects.rethinkdb_wrap")
@patch("backstop_dd.routers.spend_plan.rethinkdb_wrap")
@patch("backstop_dd.routers.health.rethinkdb_wrap")
def fast_api_mock_client(
    mocked_rethink_health,
    mocked_rethink_spend_plan,
    mocked_rethink_projects,
    mocked_rethink_fin,
    mocked_rethink_chiefs,
    mocked_rethink_calculations,
    mocked_rethink_init_db,
    mock_db,
):
    mocked_rethink_health.return_value = mock_db
    mocked_rethink_spend_plan.return_value = mock_db
    mocked_rethink_projects.return_value = mock_db
    mocked_rethink_fin.return_value = mock_db
    mocked_rethink_chiefs.return_value = mock_db
    mocked_rethink_calculations.return_value = mock_db
    mocked_rethink_init_db.return_value = mock_db
    return TestClient(app)
