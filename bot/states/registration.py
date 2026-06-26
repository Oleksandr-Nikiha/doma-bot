from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_phone = State()
    waiting_name = State()