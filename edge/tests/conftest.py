import pytest

from edge.tests.fixtures.fastapi import (  # pylint: disable=unused-import
    fast_api_mock_client,
)
from edge.tests.fixtures.rethinkdb import mock_db  # pylint: disable=unused-import


@pytest.fixture(autouse=True)
def no_rethinkdb_connect(monkeypatch):
    """Disallow connecting to RethinkDB outside of mock."""
    monkeypatch.delattr("rethinkdb.RethinkDB.connect")
