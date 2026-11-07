from .models import Order
from .money import format_money


def order_confirmation(order: Order) -> dict:
    return {
        "to": order.customer_email,
        "subject": f"Your order {order.id}",
        "body": f"Thanks! We received your order of {format_money(order.total_cents, order.currency)}.",
    }
