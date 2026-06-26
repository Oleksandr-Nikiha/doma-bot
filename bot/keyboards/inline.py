from math import ceil

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.models.category import get_active_categories
from bot.models.menu_item import get_items_count, get_items_by_category
from bot.models.price_item import get_prices_by_item
from bot.data.callbacks import ItemsCD, NavCD, CategoryCD, CartCD, CheckoutCD, ItemCD, PriceCD


def empty_btn() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=" ", 
        callback_data=NavCD(to='noop').pack()
    )


def back_btn() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="↩ Назад", 
        callback_data=NavCD(to='back').pack()
    )


async def category_keyboard() -> InlineKeyboardMarkup:
    categories = await get_active_categories()

    buttons = []
    row = []

    for i, cat in enumerate(categories):
        row.append(
            InlineKeyboardButton(
                text=f"{cat.emoji} {cat.name}",
                callback_data=CategoryCD(id=cat.category_id).pack()
            )
        )
        
        if len(row) == 2:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def items_keyboard(category_id: int, offset: int = 0, limit: int = 8, columns: int = 2) -> InlineKeyboardMarkup:
    total = await get_items_count(category_id)
    items = await get_items_by_category(category_id, limit=limit, offset=offset)

    buttons = []
    row = []
    nav = []

    for i, item in enumerate(items):
        row.append(
            InlineKeyboardButton(
                text=f"{item.name}",
                callback_data=ItemCD(id=item.item_id).pack()
            )
        )
        
        if len(row) == columns:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)

    current_page = offset // limit + 1
    total_pages  = ceil(total / limit)

    nav.append(
        InlineKeyboardButton(
            text="◀️", 
            callback_data=ItemsCD(category_id=category_id, offset=offset - limit).pack()
        )
        if offset > 0 else empty_btn()
    )

    nav.append(InlineKeyboardButton(
        text=f"{current_page}/{total_pages}",
        callback_data=NavCD(to='noop').pack()
    ))

    nav.append(
        InlineKeyboardButton(
            text="▶️", 
            callback_data=ItemsCD(category_id=category_id, offset=offset + limit).pack()
        )
        if offset + limit < total else empty_btn()
    )

    buttons.append(nav)
    buttons.append([back_btn()])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def prices_keyboard(item_id) -> InlineKeyboardMarkup:
    sizes = await get_prices_by_item(item_id)
    
    buttons = [
        [
            InlineKeyboardButton(
                text = f"{size.name} - {f'{size.size_cm} см/' if size.size_cm else ''}{size.weight_g} г - {size.price} 🇺🇦",
                callback_data=PriceCD(id=size.price_id).pack()
            )
        ]
        for size in sizes
    ]
    
    buttons.append([back_btn()])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def added_to_cart_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🛒 Замовити ще", 
                callback_data=NavCD(to='order_more').pack()
            ),
            InlineKeyboardButton(
                text="🧺 Кошик", 
                callback_data=NavCD(to='cart').pack()
            )
        ]
    ])


def cart_keyboard(items: list) -> InlineKeyboardMarkup:
    buttons = []

    for item in items:
        buttons.append([
            InlineKeyboardButton(
                text="➖", 
                callback_data=CartCD(action='minus', order_item_id=item.order_item_id).pack()
            ),
            InlineKeyboardButton(
                text=f"{item.item_name} {item.size_name}", 
                callback_data=NavCD(to='noop').pack()
            ),
            InlineKeyboardButton(
                text="➕", 
                callback_data=CartCD(action='plus', order_item_id=item.order_item_id).pack()
            ),
        ])

    buttons.append([
        InlineKeyboardButton(
            text="🗑 Очистити", 
            callback_data=CartCD(action='clear').pack()
        ),
        InlineKeyboardButton(
            text="✅ Оформити", 
            callback_data=CartCD(action='confirm').pack()
        ),
    ])

    buttons.append(
        [back_btn()]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def delivery_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚗 Доставка", 
                callback_data=CheckoutCD(to='delivery').pack()
            ),
            InlineKeyboardButton(
                text="🏃 Самовивіз", 
                callback_data=CheckoutCD(to='pickup').pack()
            )
        ],
        [
            back_btn()
        ]
    ])


def time_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⚡ Найближчим", 
                callback_data=CheckoutCD(to='asap_time').pack()
            ),
            InlineKeyboardButton(
                text="🕐 Певний", 
                callback_data=CheckoutCD(to='some_time').pack()
            )
        ],
        [
            back_btn()
        ]
    ])


def payment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💵 Готівка", 
                callback_data=CheckoutCD(to='payment_cash').pack()
            ),
            InlineKeyboardButton(
                text="💳 Картка", 
                callback_data=CheckoutCD(to='payment_card').pack()
            )
        ],
        [
            back_btn()
        ]
    ])


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_btn()]])