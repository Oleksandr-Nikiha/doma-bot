from dataclasses import dataclass
from datetime import datetime
from bot.services.database import db


@dataclass
class Order:
    order_id: int
    user_id: int
    status: str
    comment: str | None
    delivery_type: str | None
    address: str | None
    delivery_time: str | None
    payment_type: str | None
    change_from: int | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


async def get_draft_order(user_id) -> Order | None:
    row = await db.fetchrow(
        "SELECT * FROM orders WHERE user_id = $1 and status = 'draft'",
        user_id,
    )

    if not row:
        return None
    return Order(**dict(row))


async def create_order(user_id) -> Order:
    row = await db.fetchrow(
        """
        INSERT INTO orders (user_id, status)
        VALUES ($1, 'draft')
        RETURNING *
        """,
        user_id,
    )
    return Order(**dict(row))


async def get_or_create_draft_order(user_id: int) -> Order:
    order = await get_draft_order(user_id)
    if order:
        return order
    return await create_order(user_id)
