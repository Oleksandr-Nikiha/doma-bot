from dataclasses import dataclass
from datetime import datetime
from bot.services.database import db


@dataclass
class User:
    telegram_id: int
    user_id: int | None = None
    display_name: str | None = None
    phone: str | None = None
    is_registered: bool = False
    created_at: datetime | None = None


async def get_user_by_tgid(telegram_id: int) -> User:
    row = await db.fetchrow(
        "SELECT * FROM users WHERE telegram_id = $1 AND is_registered = true",
        telegram_id,
    )

    return User(**dict(row))


async def get_or_create_user(telegram_id: int) -> User:
    row = await db.fetchrow(
        "SELECT * FROM users WHERE telegram_id = $1",
        telegram_id,
    )
    if row:
        return User(**dict(row))

    await db.execute(
        """
        INSERT INTO users (telegram_id)
        VALUES ($1)
        ON CONFLICT (telegram_id) DO NOTHING
        RETURNING *
        """,
        telegram_id,
    )
    return User(telegram_id=telegram_id)


async def registration_user(telegram_id: int, phone: str, display_name: str) -> User:
    row = await db.fetchrow(
        """
        UPDATE users
        SET phone=$2, display_name=$3, is_registered=true
        WHERE telegram_id = $1
        RETURNING *
        """,
        telegram_id, phone, display_name,
    )
    return User(**dict(row))
