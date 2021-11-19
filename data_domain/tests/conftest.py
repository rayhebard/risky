import pytest

from backstop_dd.tests.fixtures.fastapi import (  # pylint: disable=unused-import
    fast_api_mock_client,
)
from backstop_dd.tests.fixtures.rethinkdb import (  # pylint: disable=unused-import
    mock_db,
)


@pytest.fixture(autouse=True)
def no_rethinkdb_connect(monkeypatch):
    """Disallow connecting to RethinkDB outside of mock."""
    monkeypatch.delattr("rethinkdb.RethinkDB.connect")
