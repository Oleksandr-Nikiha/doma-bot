from aiogram.fsm.state import State, StatesGroup

class CartStates(StatesGroup):
    view_cart = State()
    confirm_cart = State()
    