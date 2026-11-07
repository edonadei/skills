import calendar
from datetime import date


def add_months(d: date, months: int) -> date:
    """Same day-of-month `months` later, clamped to the month's last day (Jan 31 + 1 -> Feb 28/29)."""
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


def monthly_dates(start: date, n: int) -> list[date]:
    """start, start + 1 month, ... (n dates). Each is computed from `start`, so Jan 31 gives Feb 28 then Mar 31."""
    return [add_months(start, i) for i in range(n)]
