from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.models.user import get_or_create_user
from bot.services.messages import get_message
from bot.keyboards.reply import main_menu_keyboard, registration_keyboard
from bot.states.registration import RegistrationStates
 
router = Router()
 
 
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    db_user = await get_or_create_user(message.from_user.id)

    if db_user.is_registered:
        await state.clear()
        text = await get_message("commands", "start_exists", display_name=db_user.display_name)
        kb = main_menu_keyboard()
    else:
        await state.set_state(RegistrationStates.waiting_phone)
        text = await get_message("commands", "start_not_exists")
        kb = registration_keyboard()
        
    await message.answer(text, reply_markup=kb, parse_mode='HTML')


@router.message(Command("help"))
async def cmd_help(message: Message):
    text = await get_message("commands", "help")
    await message.answer(text, parse_mode='HTML')


@router.message(Command("history"))
async def cmd_histroy(message: Message, state: FSMContext):
    db_user = await get_or_create_user(message.from_user.id)

    text = await get_message("commands", "history", display_name=db_user.display_name)
    await message.answer(text, parse_mode='HTML')


@router.message(F.text == '📞 Контакти')
async def contacts_view(message: Message):
    text = await get_message("commands", "contacts")
    kb = main_menu_keyboard()

    await message.answer(text, reply_markup=kb, parse_mode='HTML')
