from dataclasses import dataclass
from bot.services.database import db

@dataclass
class OrderItem:
    order_item_id: int
    order_id: int
    item_id: int
    price_id: int
    quantity: int
    price: int
    item_name: str
    size_name: str


async def add_item_to_order(order_id: int, item_id: int, price_id: int, price: int) -> int:
    row = await db.fetchrow(
        """
        INSERT INTO order_items (order_id, item_id, price_id, quantity, price)
        VALUES ($1, $2, $3, 1, $4)
        ON CONFLICT (order_id, item_id, price_id) 
        DO UPDATE SET quantity = order_items.quantity + 1
        RETURNING order_item_id
        """,
        order_id, item_id, price_id, price
    )
    return row["order_item_id"]


async def get_order_item_by_id(order_item_id: int) -> OrderItem | None:
    row = await db.fetchrow(
        """
        SELECT 
            oi.order_item_id, oi.order_id, oi.item_id, 
            oi.price_id, oi.quantity, oi.price,
            mi.name AS item_name,
            st.name AS size_name
        FROM order_items oi
        JOIN menu_items mi ON mi.item_id = oi.item_id
        JOIN item_prices ip ON ip.price_id = oi.price_id
        JOIN size_templates st ON st.size_id = ip.size_id
        WHERE oi.order_item_id = $1
        """,
        order_item_id
    )
    if not row:
        return None
    return OrderItem(**dict(row))


async def get_order_items(order_id: int) -> list[OrderItem]:
    rows = await db.fetch(
        """
        SELECT 
            oi.order_item_id, oi.order_id, oi.item_id, 
            oi.price_id, oi.quantity, oi.price,
            mi.name AS item_name,
            st.name AS size_name
        FROM order_items oi
        JOIN menu_items mi ON mi.item_id = oi.item_id
        JOIN item_prices ip ON ip.price_id = oi.price_id
        JOIN size_templates st ON st.size_id = ip.size_id
        WHERE oi.order_id = $1
        ORDER BY oi.order_item_id
        """,
        order_id
    )

    return [OrderItem(**dict(row)) for row in rows]


async def add_quantity_order_item(order_item_id: int):
    await db.execute(
        "UPDATE order_items SET quantity = quantity + 1 WHERE order_item_id = $1",
        order_item_id
    )


async def reduce_quantity_order_item(order_item_id: int):
    updated_row = await db.fetchrow(
        """
        UPDATE order_items 
        SET quantity = quantity - 1 
        WHERE order_item_id = $1 AND quantity > 1 
        RETURNING quantity
        """,
        order_item_id
    )

    if updated_row is None:
        await remove_item_from_order(order_item_id)


async def remove_item_from_order(order_item_id: int):
    await db.execute(
        "DELETE FROM order_items WHERE order_item_id = $1;",
        order_item_id
    )


async def clear_order(order_id: int):
    await db.execute(
        "DELETE FROM order_items WHERE order_id = $1;",
        order_id
    )
