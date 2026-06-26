from dataclasses import dataclass
from bot.services.database import db


@dataclass
class Category:
    category_id: int
    name: str
    emoji: str
    is_active: bool
    position: int
    keyboard_columns: int


async def get_category_by_id(category_id) -> Category:
    row = await db.fetchrow(
        "SELECT * FROM categories WHERE category_id = $1",
        category_id,
    )

    return Category(**dict(row))


async def get_active_categories() -> list[Category]:
    rows = await db.fetch(
        "SELECT * FROM categories WHERE is_active = true ORDER BY position",
    )

    return [Category(**dict(row)) for row in rows]
