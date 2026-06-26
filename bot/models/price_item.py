from dataclasses import dataclass
from bot.services.database import db


@dataclass
class SizeItem:
    size_id: int
    name: str
    size_cm: int | None
    position: int


@dataclass
class ItemPrice(SizeItem):
    price_id: int
    item_id: int
    weight_g: int | None
    price: int


async def get_prices_by_item(item_id: int) -> list[ItemPrice]:
    rows = await db.fetch(
        """
        SELECT 
            ip.price_id, ip.item_id, ip.weight_g, ip.price,
            st.size_id, st.name, st.size_cm, st.position
        FROM item_prices ip
        JOIN size_templates st ON st.size_id = ip.size_id
        WHERE ip.item_id = $1
        ORDER BY st.position
        """,
        item_id,
    )
    return [ItemPrice(**dict(row)) for row in rows]

async def get_price_by_id(price_id: int) -> ItemPrice:
    row = await db.fetchrow(
        """
        SELECT 
            ip.price_id, ip.item_id, ip.size_id, ip.weight_g, ip.price,
            st.name, st.size_cm, st.position
        FROM item_prices ip
        JOIN size_templates st ON st.size_id = ip.size_id
        WHERE ip.price_id = $1
        """,
        price_id,
    )

    return ItemPrice(**dict(row))