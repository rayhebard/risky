import os
from unittest.mock import patch

import pytest

from backstop_dd.workers import assembler, tables
from rethinkdb import RethinkDB

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


@pytest.mark.skip(
    "Test not working - failing in contract_details.get_earliest_effective_date"
)
@patch("backstop_dd.workers.contract_details.rethinkdb_wrap")
def test_add_project_effective_date_contract_details(
    mocked_rethink_contract_details, mock_db
):
    # TODO failing in get_earliest_effective_date. Exception in makearray_of_datums
    # unexpected elem type: var_1['projNumber']
    mocked_rethink_contract_details.return_value = mock_db
    with mock_db.connect(host=db_host, port=db_port) as conn:
        projects = RethinkDB().db("Backstop").table(tables.projects).run(conn)[:3]

        assert len(projects) > 0
        assert "level_1_project_number" in projects[0]
        assert "actual_title" in projects[0]
        assert "charge_numbers" in projects[0]

        if tables.financial_summary_header in RethinkDB().db(
            "Backstop"
        ).table_list().run(conn) and tables.project_deliverables in RethinkDB().db(
            "Backstop"
        ).table_list().run(
            conn
        ):

            # call add_project_effective_date_contract_details to test
            projects = assembler.add_project_effective_date_contract_details(projects)

            # test first project is sufficient
            assert "effective_start_date" in projects[0]
            assert "spending_start_date" in projects[0]
            assert "start_date" in projects[0]
            assert "contract_type" in projects[0]
            assert "level_1_pd" in projects[0]
            assert "level_1_title" in projects[0]
            assert "level_1_unit" in projects[0]
            assert "contract_number" in projects[0]
            assert "contract_sponsor" in projects[0]
            assert "contract_officer" in projects[0]
            assert "contract_value" in projects[0]
            assert "is_new" in projects[0]
