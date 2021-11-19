from unittest.mock import patch

from backstop_dd.init_db import create_table, create_tables
from rethinkdb import RethinkDB


@patch("backstop_dd.init_db.rethinkdb_wrap")
def test_create_databases(mocked_rethink_init_db, mock_db, fast_api_mock_client):
    mocked_rethink_init_db.return_value = mock_db
    fast_api_mock_client.get("/")
    with mock_db.connect() as conn:
        assert "Backstop" in RethinkDB().db_list().run(conn)


@patch("backstop_dd.init_db.rethinkdb_wrap")
def test_create_table(mocked_rethink_init_db, mock_db):
    mocked_rethink_init_db.return_value = mock_db
    test_table_name = "A Good Ole Test Table"
    create_table("Backstop", test_table_name)


@patch("backstop_dd.init_db.rethinkdb_wrap")
def test_create_tables(mocked_rethink_init_db, mock_db):
    mocked_rethink_init_db.return_value = mock_db
    test_table_names = ["A Good Ole Test Table", "Another Good Ole Test Table"]
    create_tables("Backstop", test_table_names)
