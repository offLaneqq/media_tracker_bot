from aiogram import Router, F
from ..media_shared import MediaForm, get_user_media
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from ..constants import get_keyboard, categories
import aiohttp
import os

router = Router()

@router.message(MediaForm.waiting_for_anime_action, F.text == "Видалити аніме")
async def start_delete_anime(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user is not None else None
    media_list = await get_user_media(user_id)
    if not media_list:
        await message.answer("У вас ще немає доданих аніме.")
        return

    # Клавіатура по два аніме на рядок
    buttons = [KeyboardButton(text=media["title"]) for media in media_list]
    keyboard_rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    keyboard_rows.append([KeyboardButton(text="Назад")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True
    )

    await state.set_data({"media_list": media_list})
    await message.answer("Оберіть аніме для видалення:", reply_markup=keyboard)
    await state.set_state(MediaForm.waiting_for_delete_title)  # Використаємо цей стан для вибору

@router.message(MediaForm.waiting_for_delete_title)
async def delete_anime_selected(message: Message, state: FSMContext):
    data = await state.get_data()
    media_list = data.get("media_list", [])
    selected = next((m for m in media_list if m["title"] == message.text), None)
    if not selected:
        await message.answer("Аніме не знайдено у вашому списку. Спробуйте ще раз або натисніть 'Назад'.")
        return

    # Видалення через API
    url = f"{os.getenv('API_URL', 'http://api:8000')}/api/media/{selected['id']}/"
    async with aiohttp.ClientSession() as session:
        async with session.delete(url) as resp:
            if resp.status == 204:
                await message.answer("Аніме видалено! Повертаємось до вибору категорії.", reply_markup=get_keyboard(categories))
            else:
                await message.answer("Сталася помилка при видаленні.")
    await state.clear()