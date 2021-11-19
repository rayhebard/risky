import os
from unittest.mock import patch

from backstop_dd.workers import projections, tables
from rethinkdb import RethinkDB


def get_project(mock_db):
    """Get project from DB."""
    with mock_db.connect() as conn:
        projects = RethinkDB().db("Backstop").table(tables.projects).run(conn)
    return projects[0]


db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


@patch("backstop_dd.workers.projections.rethinkdb_wrap")
def test_get_calculations_by_project_id(mocked_rethink_projections, mock_db):
    mocked_rethink_projections.return_value = mock_db
    project = get_project(mock_db)
    project_id = project["id"]

    calc = projections.get_calculations_by_project_id(project_id)

    assert isinstance(calc, dict)
    assert isinstance(float(calc["burn_per_day"]), float)
    assert isinstance(float(calc["funds_expended_amount"]), float)
    assert isinstance(float(calc["funds_remaining"]), float)


def test_get_projected_expenses_at_end_date():

    burn = 3000.0
    times = 10
    expected = burn * times

    expense = projections.get_projected_expenses_at_end_date(burn, times)

    assert expense == expected


@patch("backstop_dd.workers.projections.rethinkdb_wrap")
def test_construct_project_overview_projections(mocked_rethink_projections, mock_db):
    mocked_rethink_projections.return_value = mock_db
    project = get_project(mock_db)

    projection_overview = projections.construct_project_overview_projections(project)

    if bool(projection_overview):  # if projection_overview is non-empty

        assert isinstance(projection_overview, dict)
        assert isinstance(float(projection_overview["current_funding"]), float)
        assert isinstance(projection_overview["end_is_past"], bool)
        assert isinstance(projection_overview["average_burn"], dict)
        assert isinstance(projection_overview["last_thirty_burn"], dict)
        assert isinstance(projection_overview["linear_closeout"], dict)


# test_construct_trend_lines() in test_workers_budget_expenses.py covers the tests
# for the following functions:
#   generate_linear_closeout()
#   generate_average_monthly_spend_projection()
#   generate_last_thirty_days_burn_projection()
#   generate_linear_projection()
