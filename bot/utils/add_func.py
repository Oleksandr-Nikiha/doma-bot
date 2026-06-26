from bot.models.order_item import OrderItem

def calculate_order_price(items: list[OrderItem]) -> int:
    return sum(item.price * item.quantity for item in items)