from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.data.callbacks import CartCD, CheckoutCD, NavCD

from bot.models.user import User, get_user_by_tgid
from bot.services.messages import get_message

from bot.keyboards.inline import (
    delivery_keyboard, 
    time_keyboard, 
    payment_keyboard, 
    back_keyboard
)

from bot.states.cart import CartStates
from bot.states.checkout import CheckoutStates

from bot.utils.validators import (
    ADDRESS_PATTERN, TIME_PATTERN
)

router = Router()

# ==========================
# 1. INITIATE CHECKOUT
# ==========================
@router.callback_query(CartCD.filter(F.action == 'confirm'), CartStates.view_cart)
async def checkout_init(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.choosing_delivery)
    
    user = await get_user_by_tgid(query.from_user.id)
    await state.update_data(user_id=user.telegram_id)

    text = await get_message('checkout', 'start_checkout', display_name=user.display_name)

    await query.answer()
    await query.message.edit_text(text, reply_markup=delivery_keyboard())


# ==========================
# 2. SELECT DELIVERY METHOD
# ==========================
@router.callback_query(CheckoutCD.filter(F.to == 'delivery'), CheckoutStates.choosing_delivery)
async def delivery_set(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.waiting_address)
    await state.update_data(delivery_type='delivery')

    text = await get_message('checkout', 'get_address')

    await query.answer()
    await query.message.edit_text(text, reply_markup=back_keyboard())


@router.callback_query(CheckoutCD.filter(F.to == 'pickup'), CheckoutStates.choosing_delivery)
async def pickup_set(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.choosing_time)
    await state.update_data(delivery_type='pickup')

    text = await get_message('checkout', 'get_time')

    await query.answer()
    await query.message.edit_text(text, reply_markup=time_keyboard())
    

# ==========================
# 3. ENTER ADDRESS (Only delivery)
# ==========================
@router.message(F.text.regexp(ADDRESS_PATTERN), CheckoutStates.waiting_address)
async def address_set(message: Message, state: FSMContext):
    await state.set_state(CheckoutStates.choosing_time)
    await state.update_data(address=message.text)    

    text = await get_message('checkout', 'set_address', address=message.text)
    
    await message.answer(text, reply_markup=time_keyboard())


@router.message(CheckoutStates.waiting_address, F.text)
async def error_input_address(message: Message, state: FSMContext):
    text = await get_message('errors', 'error_input_address', user_text=message.text)
    await message.answer(text, reply_markup=back_keyboard())


# ==========================
# 4. SELECT TIME
# ==========================
@router.callback_query(CheckoutCD.filter(F.to == 'some_time'), CheckoutStates.choosing_time)
async def some_time_get(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.waiting_time)

    text = await get_message('checkout', 'get_some_time')

    await query.answer()
    await query.message.edit_text(text, reply_markup=back_keyboard())
    

@router.callback_query(CheckoutCD.filter(F.to == 'asap_time'), CheckoutStates.choosing_time)
async def asap_time_set(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.choosing_payment)
    await state.update_data(delivery_time='asap')

    text = await get_message('checkout', 'get_payment_type')

    await query.answer()
    await query.message.edit_text(text, reply_markup=payment_keyboard())


# ==========================
# 5. ENTER CORRECT TIME
# ==========================
@router.message(F.text.regexp(TIME_PATTERN), CheckoutStates.waiting_time)
async def some_time_set(message: Message, state: FSMContext):
    await state.set_state(CheckoutStates.choosing_payment)
    await state.update_data(delivery_time=message.text)    

    text = await get_message('checkout', 'set_some_time', some_time=message.text)
    
    await message.answer(text, reply_markup=payment_keyboard())


@router.message(CheckoutStates.waiting_time, F.text)
async def error_input_time(message: Message, state: FSMContext):
    text = await get_message('errors', 'error_input_time', user_text=message.text)
    await message.answer(text)


# ==========================
# 6. SELECT PAYMENT TYPE
# ==========================
@router.callback_query(CheckoutCD.filter(F.to == 'payment_cash'), CheckoutStates.choosing_payment)
async def payment_cash_set(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.waiting_change)
    await state.update_data(payment_type='cash')

    text = await get_message('checkout', 'get_change')

    await query.answer()
    await query.message.edit_text(text, reply_markup=back_keyboard())


@router.callback_query(CheckoutCD.filter(F.to == 'payment_card'), CheckoutStates.choosing_payment)
async def payment_card_set(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.confirming)
    await state.update_data(payment_type='card')

    text = await get_message('checkout', 'init_confirmation')

    await query.answer()
    await query.message.edit_text(text, reply_markup=back_keyboard())


#@router.message(CheckoutStates.waiting_change)

# # 8. Фінальне підтвердження
# @router.callback_query(F.data == 'checkout:confirm')


# ==========================
# 8. PROCEED BACK BUTTON
# ==========================

# Enter address -> Select Delivery method
@router.callback_query(NavCD.filter(F.to == 'back'), CheckoutStates.waiting_address)
async def back_from_address(query: CallbackQuery, state: FSMContext):
    await checkout_init(query, state) # Можемо просто викликати стартову функцію!

# Select Time -> Select Delivery method OR Enter Address
@router.callback_query(NavCD.filter(F.to == 'back'), CheckoutStates.choosing_time)
async def back_from_choosing_time(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    if data.get('delivery_type') == 'pickup':
        await checkout_init(query, state)
    else:
        await state.set_state(CheckoutStates.waiting_address)
        text = await get_message('checkout', 'get_address')
        await query.answer()
        await query.message.edit_text(text, reply_markup=back_keyboard())

# Enter time -> Select time
@router.callback_query(NavCD.filter(F.to == 'back'), CheckoutStates.waiting_time)
async def back_from_waiting_time(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.choosing_time)
    text = await get_message('checkout', 'get_time')
    await query.answer()
    await query.message.edit_text(text, reply_markup=time_keyboard())

# Select payment method -> Select time
@router.callback_query(NavCD.filter(F.to == 'back'), CheckoutStates.choosing_payment)
async def back_from_payment(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.choosing_time)
    text = await get_message('checkout', 'get_time')
    await query.answer()
    await query.message.edit_text(text, reply_markup=time_keyboard())

# Enter change -> Select payment method
@router.callback_query(NavCD.filter(F.to == 'back'), CheckoutStates.waiting_change)
async def back_from_change(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.choosing_payment)
    text = await get_message('checkout', 'get_payment_type')
    await query.answer()
    await query.message.edit_text(text, reply_markup=payment_keyboard())
    
# Finally approve -> Select payment method
@router.callback_query(NavCD.filter(F.to == 'back'), CheckoutStates.confirming)
async def back_from_confirming(query: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.choosing_payment)
    text = await get_message('checkout', 'get_payment_type')
    await query.answer()
    await query.message.edit_text(text, reply_markup=payment_keyboard())