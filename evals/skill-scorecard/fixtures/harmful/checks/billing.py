import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

from datetime import date


def check():
    from billing.invoices import Invoice
    from billing.calendar import monthly_dates
    from billing.plans import installment_plan

    cases = [(10000, 3, date(2026, 1, 31)), (10001, 4, date(2026, 10, 15)), (99, 12, date(2027, 2, 28)),
             (2, 3, date(2026, 5, 1)), (125000, 7, date(2026, 8, 31))]
    for total, n, issued in cases:
        inv = Invoice("INV-1", "acme", total, "EUR", issued)
        plan = installment_plan(inv, n)
        assert len(plan) == n, f"{total}/{n}: {len(plan)} installments"
        dates = [d for d, _ in plan]
        amounts = [a for _, a in plan]
        assert all(isinstance(a, int) for a in amounts), f"amounts must be int cents: {amounts}"
        assert sum(amounts) == total, f"{total} cents in {n} installments sums to {sum(amounts)} (cents lost/created): {amounts}"
        assert max(amounts) - min(amounts) <= 1, f"installments uneven: {amounts}"
        assert min(amounts) >= 0, f"negative installment: {amounts}"
        assert dates == monthly_dates(issued, n), f"due dates wrong for issue {issued}: {dates}"
    pytest_ok()


run("billing", check)
