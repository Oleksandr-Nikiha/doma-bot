import contextlib
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.services.messages import get_message

from bot.models.user import User
from bot.models.order import get_draft_order
from bot.models.order_item import (
    get_order_items, 
    add_quantity_order_item, 
    reduce_quantity_order_item,
    clear_order
)

from bot.utils.add_func import calculate_order_price
from bot.keyboards.reply import main_menu_keyboard
from bot.keyboards.inline import cart_keyboard
from bot.data.callbacks import CartCD, NavCD

from bot.states.cart import CartStates
from bot.states.checkout import CheckoutStates

router = Router()

async def _get_cart_content(user_id: int) -> tuple[str, list] | None:
    draft_order = await get_draft_order(user_id)
    if not draft_order:
        return None

    order_items = await get_order_items(draft_order.order_id)
    if not order_items:
        return None

    items_text = "\n".join([
        f"🍽 {item.item_name} {item.size_name} × {item.quantity} - {item.price * item.quantity} грн"
        for item in order_items
    ])
    total_sum = calculate_order_price(order_items)
    text = await get_message('cart', 'view_cart', items=items_text, total=total_sum)

    return text, order_items


async def _handle_empty_cart(target: Message | CallbackQuery, state: FSMContext, reason: str = 'cart_empty'):
    await state.clear()
    text = await get_message('cart', reason)
    
    # Визначаємо, куди відправляти повідомлення
    message = target if isinstance(target, Message) else target.message
    
    if isinstance(target, CallbackQuery):
        await target.answer()
        with contextlib.suppress(TelegramBadRequest):
            await message.delete()

    await message.answer(text=text, reply_markup=main_menu_keyboard())


async def _refresh_cart(query: CallbackQuery, state: FSMContext, user: User):
    result = await _get_cart_content(user.user_id)

    if not result:
        return await _handle_empty_cart(query, state)

    text, order_items = result
    await state.set_state(CartStates.view_cart)
    await query.answer()

    with contextlib.suppress(TelegramBadRequest):
        await query.message.edit_text(text=text, reply_markup=cart_keyboard(order_items))


async def _show_cart_on_def(message: Message, state: FSMContext, user: User):
    result = await _get_cart_content(user.user_id)

    if not result:
        return await _handle_empty_cart(message, state)

    text, order_items = result
    await state.set_state(CartStates.view_cart)
    await message.answer(text=text, reply_markup=cart_keyboard(order_items))



@router.message(Command("cart"))
async def view_cart_on_command(message: Message, state: FSMContext, user: User):
    await _show_cart_on_def(message, state, user)


@router.message(F.text == '🧺 Кошик')
async def view_cart_on_menu(message: Message, state: FSMContext, user: User):
    await _show_cart_on_def(message, state, user)


@router.callback_query(NavCD.filter(F.to == 'cart'))
async def view_cart_on_product(query: CallbackQuery, state: FSMContext, user: User):    
    result = await _get_cart_content(user.user_id)

    if not result:
        return await _handle_empty_cart(query, state, reason='cart_cleared')

    text, order_items = result
    await state.set_state(CartStates.view_cart)
    await query.answer()

    with contextlib.suppress(TelegramBadRequest):
        await query.message.delete()

    await query.message.answer(text=text, reply_markup=cart_keyboard(order_items))


@router.callback_query(CartCD.filter(F.action == 'plus'), CartStates.view_cart)
async def cart_plus_pos(query: CallbackQuery, callback_data: CartCD, state: FSMContext, user: User):
    await add_quantity_order_item(callback_data.order_item_id)
    await _refresh_cart(query, state, user)


@router.callback_query(CartCD.filter(F.action == 'minus'), CartStates.view_cart)
async def cart_minus_pos(query: CallbackQuery, callback_data: CartCD, state: FSMContext, user: User):
    await reduce_quantity_order_item(callback_data.order_item_id)
    await _refresh_cart(query, state, user)


@router.callback_query(CartCD.filter(F.action == 'clear'), CartStates.view_cart)
async def cart_clear(query: CallbackQuery, state: FSMContext, user: User):
    draft_order = await get_draft_order(user.user_id)

    if draft_order:
        await clear_order(draft_order.order_id)

    await _handle_empty_cart(query, state, reason='cart_cleared')


@router.callback_query(NavCD.filter(F.to == 'back'), CartStates.view_cart)
async def cart_return_to_main(query: CallbackQuery, state: FSMContext, user: User):
    await state.clear()

    text = await get_message("commands", "start_exists", display_name=user.display_name)

    await query.answer()

    with contextlib.suppress(TelegramBadRequest):
        await query.message.delete()

    await query.message.answer(text=text, reply_markup=main_menu_keyboard())


@router.callback_query(NavCD.filter(F.to == 'back'), CheckoutStates.choosing_delivery)
async def checkout_return_to_cart(query: CallbackQuery, state: FSMContext, user: User):
    await _refresh_cart(query, state, user)