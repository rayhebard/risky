import json
import uuid
from datetime import date
from unittest.mock import patch

import pytest


# TODO: Update the test_example with the latest spend plan structure
# TODO should the charge param be being used?
def make_simple_labor_spend_plan(name, charge):
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "start_date": None,
        "end_date": None,
        "description": "",
        "tasks": [
            {
                "name": None,
                "start_date": None,
                "end_date": None,
                "description": "",
                "charges": [
                    {"year": date.today().year, "restriction": "labor", "data": []}
                ],
            }
        ],
    }


@pytest.mark.skip("Currently not working - contains() leads to list index out of range")
@patch("backstop_dd.routers.spend_plan.rethinkdb_wrap")
def test_post_spend_plan(mocked_rethink_spend_plan, mock_db, fast_api_mock_client):
    # TODO failing in spend_plan on table(tables.spend).get_all(id).contains().run(conn)
    # the error is in handle_contains() where we get IndexError: list index out of range
    mocked_rethink_spend_plan.return_value = mock_db
    spend_plan = make_simple_labor_spend_plan(
        "Test Example",
        {"display_name": "John Doe", "charge_type": "hours", "charges": {"jan": 40}},
    )
    response = fast_api_mock_client.post(
        "/spend_plan/",
        headers={"Content-type": "application/json"},
        data=json.dumps(spend_plan),
    )
    assert response.status_code == 200
    assert response.json()["current"]["inserted"] == 1


# def test_get_spend_plan_by_id():
#     response = client.get("/spend_plan/id/303")
#     assert response.status_code == 200
#     assert response.json()[0]["id"] == "303"

# def test_get_spend_plan_by_name():
#     response = client.get("/spend_plan/name/hello")
#     assert response.status_code == 200
#     assert re.match( "(?i)hello", response.json()[0]["name"] )

# def test_get_spend_plan_by_search():
#     response = client.get("/spend_plan/search/world")
#     assert response.status_code == 200
#     assert re.search( "(?i)world", response.json()[0]["name"] )


@patch("backstop_dd.routers.spend_plan.rethinkdb_wrap")
def test_read_employee_basic_info(
    mocked_rethink_spend_plan, mock_db, fast_api_mock_client
):
    mocked_rethink_spend_plan.return_value = mock_db
    response = fast_api_mock_client.get("/spend_plan/get_employee_basic_info")
    assert response.status_code == 200
    assert len(response.json()) > 0


@patch("backstop_dd.routers.spend_plan.rethinkdb_wrap")
def test_read_employee_rates_info(
    mocked_rethink_spend_plan, mock_db, fast_api_mock_client
):
    mocked_rethink_spend_plan.return_value = mock_db
    response = fast_api_mock_client.get("/spend_plan/get_rates_by_employee")
    assert response.status_code == 200
    assert len(response.json()) > 0


@patch("backstop_dd.init_db.rethinkdb_wrap")
@patch("backstop_dd.routers.spend_plan.rethinkdb_wrap")
def test_refresh_employee_basic_info(
    mocked_rethink_spend_plan, mocked_rethink_init_db, mock_db, fast_api_mock_client
):
    mocked_rethink_spend_plan.return_value = mock_db
    mocked_rethink_init_db.return_value = mock_db
    response = fast_api_mock_client.post("/spend_plan/get_employee_basic_info")
    assert response.status_code == 200
    assert len(response.json()) > 0


@patch("backstop_dd.init_db.rethinkdb_wrap")
@patch("backstop_dd.routers.spend_plan.rethinkdb_wrap")
def test_refresh_employee_rates_info(
    mocked_rethink_spend_plan, mocked_rethink_init_db, mock_db, fast_api_mock_client
):
    mocked_rethink_spend_plan.return_value = mock_db
    mocked_rethink_init_db.return_value = mock_db
    response = fast_api_mock_client.post("/spend_plan/get_rates_by_employee")
    assert response.status_code == 200
    assert len(response.json()) > 0


@patch("backstop_dd.routers.spend_plan.rethinkdb_wrap")
def test_search_employee_basic_info(
    mocked_rethink_spend_plan, mock_db, fast_api_mock_client
):
    mocked_rethink_spend_plan.return_value = mock_db
    response = fast_api_mock_client.get("/spend_plan/get_employee_basic_info/johnson")
    assert response.status_code == 200


@patch("backstop_dd.workers.spend_plan.rethinkdb_wrap")
@patch("backstop_dd.routers.spend_plan.rethinkdb_wrap")
def test_search_employee_rates_info(
    mocked_rethink_spend_plan_r,
    mocked_rethink_spend_plan_w,
    mock_db,
    fast_api_mock_client,
):
    mocked_rethink_spend_plan_r.return_value = mock_db
    mocked_rethink_spend_plan_w.return_value = mock_db
    response = fast_api_mock_client.get("/spend_plan/get_rates_by_employee/3587111")
    assert response.status_code == 200


@patch("backstop_dd.routers.spend_plan.rethinkdb_wrap")
def test_find_full_working_hours(
    mocked_rethink_spend_plan, mock_db, fast_api_mock_client
):
    mocked_rethink_spend_plan.return_value = mock_db
    response = fast_api_mock_client.get(
        "/spend_plan/find_full_working_hours/10/2021?end_month=1&end_year=2022"
    )
    assert response.status_code == 200
    assert len(response.json()) == 4
