import os
from datetime import datetime
from unittest.mock import patch

import pytest

from backstop_dd.workers import budget_expenses, supplemental, tables
from rethinkdb import RethinkDB

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


def get_project(mock_db):
    """Get project from DB."""
    with mock_db.connect() as conn:
        projects = RethinkDB().db("Backstop").table(tables.projects).run(conn)
    return projects[0]


@pytest.fixture
@patch("backstop_dd.workers.supplemental.rethinkdb_wrap")
def get_financial_supplemental(mocked_rethink_supplemental, mock_db):
    mocked_rethink_supplemental.return_value = mock_db
    project = get_project(mock_db)
    fin_supp = {}

    if project["level_1_project_number"] in ["D8150", "D8479"]:
        with mock_db.connect() as conn:
            fin_supp = supplemental.get_financial_supplemental(project, conn)

    return fin_supp


@pytest.fixture
@patch("backstop_dd.workers.budget_expenses.rethinkdb_wrap")
def get_cost_value(mocked_rethink_budget_expenses, mock_db):
    mocked_rethink_budget_expenses.return_value = mock_db
    project = get_project(mock_db)
    charge_numbers = project["charge_numbers"].split(",")
    cost_value = 0

    if len(charge_numbers) == 1 and "." not in charge_numbers[0]:
        charge_number = charge_numbers[0]
        with mock_db.connect() as conn:
            cost_value = budget_expenses.get_cost_value(charge_number, conn)

    return cost_value


@pytest.fixture
# @patch("backstop_dd.workers.budget_expenses.rethinkdb_wrap")
def get_budget_expense_for_all_periods():  # (mocked_rethink_budget_expenses, mock_db):
    # mocked_rethink_budget_expenses.return_value = mock_db
    # project = get_project(mock_db)
    # with mock_db.connect() as conn:
    #     periods = budget_expenses.get_budget_expense_for_all_periods(project, conn)
    periods = [
        {
            "period": "03/2021",
            "period_totals": {"totalBudget": 10000, "fundsAvailable": 2000},
        },
        {
            "period": "04/2021",
            "period_totals": {"totalBudget": 20000, "fundsAvailable": 2000},
        },
    ]
    return periods


@pytest.fixture
def set_period_ceiling_funding_and_funds_expended(
    get_budget_expense_for_all_periods, get_cost_value
):

    if isinstance(get_cost_value, str):
        period_ceiling_and_funds_exp = (
            budget_expenses.set_period_ceiling_funding_and_funds_expended(
                get_budget_expense_for_all_periods
            )
        )
    else:
        period_ceiling_and_funds_exp = (
            budget_expenses.set_period_ceiling_funding_and_funds_expended(
                get_budget_expense_for_all_periods, get_cost_value
            )
        )

    return period_ceiling_and_funds_exp


@pytest.fixture
def add_supplemental_data_to_all_periods(
    set_period_ceiling_funding_and_funds_expended, get_financial_supplemental
):

    period_ceiling_and_funds_exp = set_period_ceiling_funding_and_funds_expended

    if len(get_financial_supplemental) > 0:
        period_ceiling_and_funds_exp = (
            budget_expenses.add_supplemental_data_to_all_periods(
                set_period_ceiling_funding_and_funds_expended,
                get_financial_supplemental,
            )
        )

    return period_ceiling_and_funds_exp


@pytest.fixture
def shift_all_data(add_supplemental_data_to_all_periods):

    return budget_expenses.shift_all_data(add_supplemental_data_to_all_periods)


@pytest.fixture
@patch("backstop_dd.workers.budget_expenses.rethinkdb_wrap")
def add_points_on_financial_performance_graph(
    mocked_rethink_budget_expenses, shift_all_data, mock_db
):
    mocked_rethink_budget_expenses.return_value = mock_db
    project = get_project(mock_db)
    # find today's date and pop end date
    today_date = datetime.today()

    end_date = project["osp_+_contract_pop_end_date"]

    if end_date is not None and end_date != "None":
        truncated_date = end_date.split("T")[0]
    else:
        truncated_date = None

    if truncated_date == None or len(truncated_date) < 1:
        end_pop_date = budget_expenses.last_day_of_month(datetime.today())
    else:
        end_pop_date = datetime.strptime(truncated_date, "%Y-%m-%d")

    # extract the last period's data
    last_period = shift_all_data[-1]

    period = last_period["period"]
    ceiling = last_period["ceiling"]
    funding = last_period["funding"]
    percent_expended_75 = last_period["75_percent_expended"]

    points_to_add = budget_expenses.add_points_on_financial_performance_graph(
        today_date, end_pop_date, period, ceiling, funding, percent_expended_75
    )

    return points_to_add


@pytest.fixture
def create_data_point_for_today(
    shift_all_data, add_points_on_financial_performance_graph
):

    expanded_period_ceiling_and_funds_exp = (
        shift_all_data + add_points_on_financial_performance_graph
    )

    current_period_index = len(shift_all_data) - 1

    proj_exp = expanded_period_ceiling_and_funds_exp[current_period_index][
        "funds_expended"
    ]

    return budget_expenses.create_data_point_for_today(
        proj_exp, expanded_period_ceiling_and_funds_exp, current_period_index
    )


@pytest.fixture
@patch("backstop_dd.workers.projections.rethinkdb_wrap")
def construct_trend_lines(
    mocked_rethink_projections,
    mock_db,
    create_data_point_for_today,
    add_supplemental_data_to_all_periods,
):
    mocked_rethink_projections.return_value = mock_db
    project = get_project(mock_db)
    end_date = project["osp_+_contract_pop_end_date"]

    if end_date is not None and end_date != "None":
        truncated_date = end_date.split("T")[0]
    else:
        truncated_date = None

    if truncated_date == None or len(truncated_date) < 1:
        end_pop_date = budget_expenses.last_day_of_month(datetime.today())
    else:
        end_pop_date = datetime.strptime(truncated_date, "%Y-%m-%d")

    if (
        project["spending_start_date"] is not None
        or project["spending_start_date"] != "None"
    ):
        spend_date = datetime.strptime(project["spending_start_date"], "%Y-%m-%d")
    else:
        spend_date = datetime.today()

    # call shift_all_data to get the original data with the field funds_expended still there
    shifted_period_ceiling_and_funds_exp = budget_expenses.shift_all_data(
        add_supplemental_data_to_all_periods
    )

    current_period_index = len(shifted_period_ceiling_and_funds_exp) - 1

    current_exsp = shifted_period_ceiling_and_funds_exp[current_period_index][
        "funds_expended"
    ]

    data = budget_expenses.construct_trend_lines(
        project,
        create_data_point_for_today,
        current_exsp,
        current_period_index,
        spend_date,
        end_pop_date,
    )

    return data


def test_get_cost_value(get_cost_value):

    # ensure output of get_cost_value has expected data type
    if isinstance(get_cost_value, str):
        assert get_cost_value.lower() == "cost value amount not found"
    else:
        assert isinstance(float(get_cost_value), float)


def test_last_day_of_month():

    # ensure output of last_day_of_month is correct
    day_in = datetime.strptime("2021-08-15", "%Y-%m-%d")

    day_out = budget_expenses.last_day_of_month(day_in)
    day_out_str = datetime.strftime(day_out, "%Y-%m-%d")

    day_out_expected = "2021-09-14"

    assert isinstance(day_out, datetime)
    assert day_out_str == day_out_expected


@pytest.mark.skip("Test not working")
def test_get_budget_expense_for_all_periods(get_budget_expense_for_all_periods):
    # TODO inside budget_expenses.get_budget_expense_for_all_periods as it tries to
    # write to DB, it raises an exception in rql_rewrite.py (TypeError)

    # ensure output of get_budget_expense_for_all_periods is non-empty with proper data type
    assert len(get_budget_expense_for_all_periods) > 0

    for period in get_budget_expense_for_all_periods:

        assert isinstance(datetime.strptime(period["period"], "%m/%Y"), datetime)
        assert isinstance(float(period["period_totals"]["totalBudget"]), float)
        assert isinstance(float(period["period_totals"]["fundsAvailable"]), float)


@pytest.mark.skip(
    "Test not working - TypeError with set_period_ceiling_funding_and_funds_expended"
)
def test_set_period_ceiling_funding_and_funds_expended(
    set_period_ceiling_funding_and_funds_expended,
):
    # TODO inside budget_expenses.get_budget_expense_for_all_periods as it tries to
    # write to DB, it raises an exception in rql_rewrite.py (TypeError)

    # ensure output of set_period_ceiling_funding_and_funds_expended has proper data type
    for period in set_period_ceiling_funding_and_funds_expended:

        assert isinstance(period, dict)
        assert isinstance(period["period"], datetime)
        assert isinstance(float(period["ceiling"]), float)
        assert isinstance(float(period["funding"]), float)
        assert isinstance(float(period["75_percent_expended"]), float)
        assert isinstance(float(period["funds_expended"]), float)


@pytest.mark.skip(
    "Test not working - TypeError with set_period_ceiling_funding_and_funds_expended"
)
def test_add_supplemental_data_to_all_periods(add_supplemental_data_to_all_periods):
    # TODO this is failing for same reason as others. this calls ....
    # add_supplemental_data_to_all_periods -> set_period_ceiling_funding_and_funds_expended
    # it raises an exception in rql_rewrite.py (TypeError)

    # ensure output of add_supplemental_data_to_all_periods has proper data type
    for period in add_supplemental_data_to_all_periods:

        assert isinstance(period, dict)
        assert isinstance(period["period"], datetime)
        assert isinstance(float(period["ceiling"]), float)
        assert isinstance(float(period["funding"]), float)
        assert isinstance(float(period["75_percent_expended"]), float)
        assert isinstance(float(period["funds_expended"]), float)


@pytest.mark.skip(
    "Test not working - TypeError with set_period_ceiling_funding_and_funds_expended"
)
def test_shift_all_data(shift_all_data, add_supplemental_data_to_all_periods):
    # TODO came issue as add_supplemental_data_to_all_periods causes it

    # ensure output of shift_all_data length and the values of some fields
    # are the same from the last two dictionaries in shift_all_data
    shift_prev = shift_all_data[-2]
    shift_last = shift_all_data[-1]

    assert len(shift_all_data) == len(add_supplemental_data_to_all_periods)
    assert shift_prev["ceiling"] == shift_last["ceiling"]
    assert shift_prev["funding"] == shift_last["funding"]
    assert shift_prev["75_percent_expended"] == shift_last["75_percent_expended"]


@pytest.mark.skip("NEED TO REVISIT - Test not working")
def test_add_points_on_financial_performance_graph(
    add_points_on_financial_performance_graph,
):

    # ensure outpout of add_points_on_financial_performance_graph is correct
    if len(add_points_on_financial_performance_graph) > 0:

        period = add_points_on_financial_performance_graph[0]["period"]
        ceiling = add_points_on_financial_performance_graph[0]["ceiling"]
        funding = add_points_on_financial_performance_graph[0]["funding"]
        percent_expended_75 = add_points_on_financial_performance_graph[0][
            "75_percent_expended"
        ]
        funds_expended = add_points_on_financial_performance_graph[0]["funds_expended"]

        for data in add_points_on_financial_performance_graph:

            assert period <= data["period"]
            assert ceiling == data["ceiling"]
            assert funding == data["funding"]
            assert percent_expended_75 == data["75_percent_expended"]
            assert funds_expended == data["funds_expended"]

            period = data["period"]


def test_create_data_point_for_today(
    create_data_point_for_today,
    shift_all_data,
    add_points_on_financial_performance_graph,
):

    # ensure output length of create_data_point_for_today is expected
    expanded_period_ceiling_and_funds_exp = (
        shift_all_data + add_points_on_financial_performance_graph
    )

    assert (
        len(create_data_point_for_today)
        == len(expanded_period_ceiling_and_funds_exp) + 1
    )


def test_construct_trend_lines(construct_trend_lines, shift_all_data, mock_db):
    project = get_project(mock_db)
    # ensure output of construct_trend_lines is expected
    end_date = project["osp_+_contract_pop_end_date"]

    if end_date is not None and end_date != "None":
        truncated_date = end_date.split("T")[0]
    else:
        truncated_date = None

    if truncated_date == None or len(truncated_date) < 1:
        end_pop_date = budget_expenses.last_day_of_month(datetime.today())
    else:
        end_pop_date = datetime.strptime(truncated_date, "%Y-%m-%d")

    current_period_index = len(shift_all_data) - 1

    for data in construct_trend_lines:

        if data["period"].date() <= end_pop_date.date():

            assert isinstance(float(data["linear_guide"]), float)

    for data in construct_trend_lines[current_period_index:]:

        assert isinstance(float(data["projected_funds_expended"]), float)
        assert isinstance(float(data["linear_average_monthly_burn"]), float)

    assert isinstance(
        float(construct_trend_lines[current_period_index]["linear_closeout"]), float
    )


def test_add_origin_point(construct_trend_lines, mock_db):
    project = get_project(mock_db)
    # ensure output of add_origin_point is expected
    periods = budget_expenses.add_origin_point(
        construct_trend_lines, project["start_date"]
    )

    period = periods[0]

    assert period["period"] == project["start_date"]
    assert period["ceiling"] == construct_trend_lines[0]["ceiling"]
    assert period["funding"] == construct_trend_lines[0]["funding"]
    assert period["75_percent_expended"] == construct_trend_lines[0]["funding"] * 0.75
    assert period["funds_expended"] == 0
    assert period["linear_guide"] == 0


def test_monthdelta():
    # ensure between 11/2021 and 5/2022 there are 6 months
    day1 = datetime.strptime("11-2021", "%m-%Y")
    day2 = datetime.strptime("5-2022", "%m-%Y")
    expected = 6

    actual = budget_expenses.monthdelta(day1, day2)

    assert expected == actual
