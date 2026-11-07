from datetime import date

from billing.calendar import add_months, monthly_dates


def test_clamps_month_end():
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)


def test_monthly_dates_keep_anchor():
    assert monthly_dates(date(2026, 1, 31), 3) == [date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31)]
