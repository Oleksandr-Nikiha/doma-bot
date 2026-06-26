from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from bot.services.messages import get_message

from bot.models.user import get_user_by_tgid
from bot.models.category import get_category_by_id
from bot.models.menu_item import get_item_by_id
from bot.models.price_item import get_price_by_id
from bot.models.order import get_or_create_draft_order
from bot.models.order_item import add_item_to_order

from bot.keyboards.inline import category_keyboard, items_keyboard, prices_keyboard, added_to_cart_keyboard

from bot.states.order import OrderStates

router = Router()


@router.message(F.text == '🛒 Замовити')
async def order_menu(message: Message, state: FSMContext):
    await state.set_state(OrderStates.choosing_category)

    text = await get_message('order', 'category_menu')
    kb = await category_keyboard()

    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == 'nav:back', OrderStates.choosing_item)
async def return_order_menu(query: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing_category)

    text = await get_message('order', 'category_menu')
    kb = await category_keyboard()

    await query.answer()
    await query.message.edit_text(text, reply_markup=kb)


async def _show_items(query: CallbackQuery, state: FSMContext, category_id: int, columns: int):
    await state.set_state(OrderStates.choosing_item)
    await state.update_data(category_id=category_id)

    text = await get_message('order', 'position_menu')
    kb = await items_keyboard(category_id=category_id, columns=columns)

    await query.answer()

    if query.message.photo:
        await query.message.answer(text=text, reply_markup=kb)
        await query.message.delete()
    else:
        await query.message.edit_text(text=text, reply_markup=kb)

@router.callback_query(F.data.startswith('cat:'), OrderStates.choosing_category)
async def item_menu(query: CallbackQuery, state: FSMContext):
    category_id = int(query.data.split(':')[1])
    category = await get_category_by_id(category_id)

    await _show_items(query, state, category.category_id, category.keyboard_columns)


@router.callback_query(F.data == 'nav:back', OrderStates.choosing_size)
async def back_to_items(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data.get('category_id')
    category = await get_category_by_id(category_id)
    await _show_items(query, state, category.category_id, category.keyboard_columns)


@router.callback_query(F.data.startswith('items:'), OrderStates.choosing_item)
async def items_page(query: CallbackQuery, state: FSMContext):
    _, category_id, offset = query.data.split(':')
    category_id = int(category_id)
    offset = int(offset)

    await state.update_data(category_id=category_id)

    kb = await items_keyboard(category_id=category_id, offset=offset)
    await query.answer()
    await query.message.edit_reply_markup(reply_markup=kb)


@router.callback_query(F.data.startswith('item:'), OrderStates.choosing_item)
async def choose_item(query: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing_size)

    item_id = int(query.data.split(':')[1])
    await state.update_data(item_id=item_id)

    item_db = await get_item_by_id(item_id=item_id)
    text = await get_message('order', 'choose_item', item_name=item_db.name, item_desc=item_db.description)
    kb = await prices_keyboard(item_db.item_id)

    await query.answer()
    if item_db.photo_id:
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=item_db.photo_id,
                caption=text,
                parse_mode="HTML"
            ),
            reply_markup=kb
        )
    else:
        await query.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith('price:'), OrderStates.choosing_size)
async def add_to_cart(query: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.confirming_order)
    data = await state.get_data()

    item_id = data.get('item_id')
    item = await get_item_by_id(item_id)

    price_id = int(query.data.split(':')[1])
    price = await get_price_by_id(price_id)

    tg_user = query.from_user.id
    user = await get_user_by_tgid(tg_user)

    order = await get_or_create_draft_order(user.user_id)
    await add_item_to_order(order.order_id, item.item_id, price.price_id, price.price)
        
    text = await get_message('order', 'added_to_cart', item_name=item.name, size=price.name, price=price.price)
    kb = added_to_cart_keyboard()
    
    await query.answer()
    if query.message.photo:
        await query.message.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
    else:
        await query.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == 'nav:order_more')
async def order_more(query: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing_category)
    text = await get_message('order', 'category_menu')
    kb = await category_keyboard()
    await query.answer()
    if query.message.photo:
        await query.message.answer(text=text, reply_markup=kb)
        await query.message.delete()
    else:
        await query.message.edit_text(text=text, reply_markup=kb)


@router.callback_query(F.data == 'nav:noop')
async def noop_handler(query: CallbackQuery):
    await query.answer()