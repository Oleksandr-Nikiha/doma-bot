from aiogram.fsm.state import State, StatesGroup

class CheckoutStates(StatesGroup):
    choosing_delivery = State()
    waiting_address = State()
    choosing_time = State()
    waiting_time = State()
    choosing_payment = State()
    waiting_change = State()
    confirming = State()