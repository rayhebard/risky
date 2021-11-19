import os
from datetime import datetime

from backstop_dd.workers import calculator

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


def test_day_delta():

    date1 = datetime.strptime("2021-09-01", "%Y-%m-%d")
    date2 = datetime.strptime("2021-09-11", "%Y-%m-%d")

    time_delta = calculator.day_delta(date1, date2)

    assert float(time_delta) == 10.0


def test_get_daily_burn():

    funds = 5500.0
    days = 10

    daily_burn = calculator.get_daily_burn(funds, days)

    assert float(daily_burn) == 550.0


def test_calculate_months_remaining():

    funds = 5500.0
    burn = 550.0

    months = calculator.calculate_months_remaining(funds, burn)

    assert float(months) == 10.0


def test_calculate_burn_per_month():

    current_expense = 5000.0
    last_expense = 1000.0
    past_days = 15
    total_days = 30

    burn = calculator.calculate_burn_per_month(
        current_expense, last_expense, past_days, total_days
    )

    assert burn == 5500.0


def test_calculate_burn_per_day():

    burn_rate = 6000.0

    burn = calculator.calculate_burn_per_day(burn_rate)

    assert burn == 200.0


def test_calculate_burn_per_week():

    daily_burn = 1000.0

    burn = calculator.calculate_burn_per_week(daily_burn)

    assert burn == 7000.0


def test_calculate_funds_expended_percent():

    budget = 5000.0
    funds_available = 3000.0

    percent = calculator.calculate_funds_expended_percent(budget, funds_available)

    assert percent == 40.0


def test_calculate_funds_expended_amount():

    budget = 5000.0
    funds_available = 3000.0

    expended = calculator.calculate_funds_expended_amount(budget, funds_available)

    assert expended == 2000.0
