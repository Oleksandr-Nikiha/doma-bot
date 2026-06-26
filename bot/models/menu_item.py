from dataclasses import dataclass
from bot.services.database import db


@dataclass
class MenuItem:
    item_id: int
    category_id: int
    name: str
    description: str | None
    is_active: bool
    position: int
    photo_id: str | None = None


async def get_item_by_id(item_id: int) -> MenuItem:
    row = await db.fetchrow(
        "SELECT * FROM menu_items WHERE item_id = $1",
        item_id,
    )

    return MenuItem(**dict(row))


async def get_items_by_category(category_id: int, limit: int = 8, offset: int = 0) -> list[MenuItem]:
    rows = await db.fetch(
        """
        SELECT * FROM menu_items 
        WHERE category_id = $1 AND is_active = true 
        ORDER BY position
        LIMIT $2 OFFSET $3
        """,
        category_id, limit, offset
    )

    return [MenuItem(**dict(row)) for row in rows]


async def get_items_count(category_id: int) -> int:
    row = await db.fetchrow(
        "SELECT COUNT(*) FROM menu_items WHERE category_id = $1 AND is_active = true",
        category_id
    )
    return row["count"]


async def save_image_item(photo_id, item_id):
    await db.execute(
        "UPDATE menu_items SET photo_id = $1 WHERE item_id = $2;",
        photo_id, item_id
    )