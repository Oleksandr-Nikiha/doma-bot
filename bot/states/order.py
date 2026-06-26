from aiogram.fsm.state import State, StatesGroup
 
 
class OrderStates(StatesGroup):
    choosing_category = State()
    choosing_item = State()
    choosing_size = State()
    confirming_order = State()
    waiting_comment = State()