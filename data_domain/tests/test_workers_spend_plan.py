import os
from unittest.mock import patch

from backstop_dd.workers import assembler, tables
from rethinkdb import RethinkDB

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


def get_project(mock_db):
    """Get project from DB."""
    with mock_db.connect() as conn:
        projects = RethinkDB().db("Backstop").table(tables.projects).run(conn)
    return projects[0]


def test_search_employee_basic_data(mock_db):

    # retrieve employees basic info data
    with mock_db.connect(host=db_host, port=db_port) as conn:
        res = RethinkDB().db("Backstop").table(tables.employee_basic_info).run(conn)
    basic_employee_info_list = list(res)

    assert len(basic_employee_info_list) > 0
    assert "employeeID" in basic_employee_info_list[0]
    assert "firstName" in basic_employee_info_list[0]
    assert "lastName" in basic_employee_info_list[0]
    assert "nickname" in basic_employee_info_list[0]
    assert "email" in basic_employee_info_list[0]
    assert "directSupervisor" in basic_employee_info_list[0]
    assert "branch" in basic_employee_info_list[0]
    assert "title" in basic_employee_info_list[0]

    # call search_employee_basic_data to test
    word = "johnson"
    matched = assembler.search_employee_basic_data(basic_employee_info_list, word)

    # test the output matched
    for matched1 in matched:

        firstname = matched1["firstName"].lower()
        lastname = matched1["lastName"].lower()
        nickname = matched1["nickname"].lower()

        assert word in firstname or word in lastname or word in nickname


@patch("backstop_dd.workers.spend_plan.rethinkdb_wrap")
def test_search_employee_rates_data(mocked_rethink_spend_plan, mock_db):
    mocked_rethink_spend_plan.return_value = mock_db
    # retrieve employees rates info data
    with mock_db.connect(host=db_host, port=db_port) as conn:
        res = RethinkDB().db("Backstop").table(tables.employee_rates_info).run(conn)
    rates_employee_info_list = list(res)

    assert len(rates_employee_info_list) > 0
    assert "employeeID" in rates_employee_info_list[0]
    assert "employeeName" in rates_employee_info_list[0]
    assert "effectiveDate" in rates_employee_info_list[0]
    assert "employeeMax" in rates_employee_info_list[0]
    assert "govRate" in rates_employee_info_list[0]
    assert "indRate" in rates_employee_info_list[0]
    assert "internalRate" in rates_employee_info_list[0]
    assert "pubRate" in rates_employee_info_list[0]

    # call search_employee_rates_data to test
    employee_id = "0090838"
    matched = assembler.search_employee_rates_data(
        rates_employee_info_list, employee_id
    )

    # test the output matched
    for matched1 in matched:

        assert employee_id == matched1["employeeID"]


def test_find_full_working_hours():

    # specify test inputs
    start_month = 10
    start_year = 2021
    end_month = 1
    end_year = 2022

    # specify expected output
    expected = {
        "2021-10-01": 168,
        "2021-11-01": 176,
        "2021-12-01": 184,
        "2022-01-01": 168,
    }

    # call find_full_working_hours to test
    actual = assembler.find_full_working_hours(
        start_month, start_year, end_month, end_year
    )

    assert expected == actual
