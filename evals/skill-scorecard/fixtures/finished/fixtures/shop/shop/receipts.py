from .models import Order
from .money import format_money


def render_receipt(order: Order) -> str:
    lines = [f"Order {order.id}", ""]
    for item in order.items:
        lines.append(f"{item.quantity} x {item.sku}  {format_money(item.unit_price_cents * item.quantity, order.currency)}")
    lines.append(f"Shipping  {format_money(order.shipping_cents, order.currency)}")
    lines.append(f"Total  {format_money(order.total_cents, order.currency)}")
    return "\n".join(lines)
