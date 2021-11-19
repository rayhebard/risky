import os
from unittest.mock import patch

import pytest

from backstop_dd.workers import financials, supplemental, tables
from rethinkdb import RethinkDB

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


# pylint: disable=unused-argument
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, data, status_code):
            self.data = data
            self.status_code = status_code
            self.text = data

        def json(self):
            return self.data

    resp = None
    if "latest_closeout_period" in args[0]:
        resp = "03/2021"

    if resp is None:
        return MockResponse(None, 404)

    return MockResponse(resp, 200)


@patch("backstop_dd.workers.financials.requests.get")
def test_get_current(mocked_latest_closeout_period):
    mocked_latest_closeout_period.side_effect = mocked_requests_get
    closeout = financials.get_current()
    assert isinstance(closeout, str)
    assert len(closeout) > 0


@pytest.mark.skip("test is not currently working")
@patch("backstop_dd.workers.financials.requests.get")
def test_construct_project_calculations(mocked_latest_closeout_period, mock_db):
    # TODO test is failing in get_financial_summary_details_by_project_number on
    # query_current.items because 'list' object has no attribute 'items'
    mocked_latest_closeout_period.side_effect = mocked_requests_get
    with mock_db.connect(host=db_host, port=db_port) as conn:
        projects = RethinkDB().db("Backstop").table(tables.projects).run(conn)
    current_p = financials.get_current()
    last_p = financials.get_last()
    period_before_last = financials.get_period_before_last(last_p)

    assert len(projects) > 0

    for project in projects:
        assert "level_1_project_number" in project
        assert "actual_title" in project
        assert "charge_numbers" in project
        assert "id" in project

        supp_fin = {}
        if project["level_1_project_number"] == "D84A7":
            ptf = project["actual_title"].strip("'").split(":")[0]
            with mock_db.connect(host=db_host, port=db_port) as conn:
                query_supplemental = (
                    RethinkDB()
                    .db("Backstop")
                    .table(tables.supplemental)
                    .filter({"PTF": ptf})
                    .run(conn)
                )
            supp_fin = supplemental.get_financial_supplemental_details(
                query_supplemental
            )

        charge_numbers = project["charge_numbers"].split(",")

        response = financials.get_financial_summary_details_by_project_number(
            charge_numbers,
            current_p,
            last_p,
            period_before_last,
            conn,
            supp_fin=supp_fin,
        )

        assert isinstance(response, dict)
        assert isinstance(response["res_current"]["totalExpense"], float)
        assert isinstance(response["res_current"]["totalBudget"], float)
        assert isinstance(response["res_last"]["totalExpense"], float)
        assert isinstance(response["funds"]["fundsAvailable"], float)

        # reset supp_fin
        supp_fin = {}

        # complete financial calculation for each top level project
        # TODO this call to financials.calculate is missing the param "funds"
        calculations = financials.calculate(
            response["res_current"], response["res_last"], response["funds"]
        )

        assert isinstance(calculations, dict)
        assert "funds_remaining" in calculations
        assert "funds_expended_percent" in calculations
        assert "funds_expended_amount" in calculations
        assert "burn_per_month" in calculations
        assert "burn_per_day" in calculations
        assert "burn_per_week" in calculations
        assert "months_remaining" in calculations
        assert isinstance(calculations["funds_remaining"], float)
        assert isinstance(calculations["funds_expended_percent"], float)
        assert isinstance(calculations["funds_expended_amount"], float)
        assert isinstance(calculations["burn_per_month"], float)
        assert isinstance(calculations["burn_per_day"], float)
        assert isinstance(calculations["burn_per_week"], float)

        if calculations["months_remaining"] is not None:
            assert isinstance(calculations["months_remaining"], float)
