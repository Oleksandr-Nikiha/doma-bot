from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.models.user import registration_user
from bot.services.messages import get_message
from bot.keyboards.reply import main_menu_keyboard
from bot.states.registration import RegistrationStates
from bot.utils.validators import NAME_PATTERN

router = Router()

@router.message(F.contact, RegistrationStates.waiting_phone)
async def get_contact_data(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    
    await state.update_data(phone = phone_number)
    await state.set_state(RegistrationStates.waiting_name)

    text = await get_message('registration', 'ask_display_name', phone_number=phone_number)
    await message.answer(text, reply_markup=None)


@router.message(F.text.regexp(NAME_PATTERN), RegistrationStates.waiting_name)
async def get_display_name(message: Message, state: FSMContext):
    state_data = await state.get_data()

    phone_number = state_data.get('phone')
    display_name = message.text

    user = message.from_user
    db_user = await registration_user(user.id, phone_number, display_name)

    text = await get_message('registration', 'end_registration', display_name=db_user.display_name)
    kb = main_menu_keyboard()
    await state.clear()
    await message.answer(text, reply_markup=kb)

@router.message(RegistrationStates.waiting_name)
async def get_display_name_invalid(message: Message):
    user_text = message.text
    text = await get_message("errors", "invalid_name", user_text=user_text)
    
    await message.answer(text, parse_mode='HTML')