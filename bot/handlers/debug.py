from aiogram import Router, F
from aiogram.types import Message

from bot.models.menu_item import save_image_item

router = Router()

@router.message(F.photo)
async def get_photo_id(message: Message):
    file_id = message.photo[-1].file_id
    item_id = int(message.caption)
    await save_image_item(file_id, item_id)
    await message.answer(f"`{file_id}`", parse_mode="Markdown")