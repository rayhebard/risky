import json
from pathlib import Path

import pytest
from rethinkdb_mock import MockThink

from backstop_dd.init_db import Lab

DB_NAME = "Backstop"
TEST_DB_DATA = "tests/data/mock_db_data"


class MockThinkPatched(MockThink):
    # pylint: disable=unused-argument
    def connect(self, *args, **kwargs):
        return super().connect()


@pytest.fixture(scope="module")
def mock_db():
    tables = {
        json_file.name.replace(".json", ""): json.loads(json_file.read_text())
        for json_file in Path(TEST_DB_DATA).glob("*.json")
    }
    database = {"dbs": {lab.value.upper(): {"tables": tables} for lab in Lab}}
    return MockThinkPatched(database)
