from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btn_share_contact = KeyboardButton(text="🪪 Поділитися контактом", request_contact=True)

btn_order = KeyboardButton(text="🛒 Замовити")
btn_cart = KeyboardButton(text="🧺 Кошик")
btn_history = KeyboardButton(text="🕓 Історія")
btn_contacts = KeyboardButton(text="📞 Контакти")


def registration_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[btn_share_contact]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[btn_order, btn_cart], [btn_history, btn_contacts]],
        resize_keyboard=True,
        #one_time_keyboard=True
    )
