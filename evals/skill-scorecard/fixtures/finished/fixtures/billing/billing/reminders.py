from datetime import date

from .calendar import add_months
from .invoices import Invoice


def reminder_dates(invoice: Invoice) -> list[date]:
    """Payment reminders one and two months after issue."""
    return [add_months(invoice.issued, 1), add_months(invoice.issued, 2)]
