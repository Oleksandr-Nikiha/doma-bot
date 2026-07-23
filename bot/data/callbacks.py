from aiogram.filters.callback_data import CallbackData
from typing import Optional


class NavCD(CallbackData, prefix="nav"):
    to: str


class CategoryCD(CallbackData, prefix="cat"):
    id: int


class ItemsCD(CallbackData, prefix="items"):
    category_id: int
    offset: int


class CartCD(CallbackData, prefix="cart"):
    action: str
    order_item_id: Optional[int] = None


class CheckoutCD(CallbackData, prefix="checkout"):
    to: str


class ItemCD(CallbackData, prefix="item"):
    id: int


class PriceCD(CallbackData, prefix="price"):
    id: int
