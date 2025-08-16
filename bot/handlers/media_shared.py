from aiogram.fsm.state import State, StatesGroup
import aiohttp, os

from aiogram import F, Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.start import categories, get_keyboard
from typing import Optional

router = Router()

valid_statuses = ["Заплановано", "Дивлюсь", "Переглянуто"]

class MediaForm(StatesGroup):
    waiting_for_title = State()
    waiting_for_status = State()
    waiting_for_episode = State()
    waiting_for_filter_status = State()
    waiting_for_edit_title = State()
    waiting_for_anime_action = State()
    waiting_for_delete_title = State()
    waiting_for_import_file = State()

async def get_user_media(user_id: Optional[int]):
    url = f"{os.getenv('API_URL', 'http://api:8000')}/api/media/?telegram_id={user_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

@router.message(MediaForm.waiting_for_filter_status, F.text == "Назад")
async def back_to_anime_actions(message: Message, state: FSMContext):
    actions = ["Додати аніме", "Редагувати аніме", "Переглянути список аніме"]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=action)] for action in actions],
        resize_keyboard=True
    )
    await state.set_state(MediaForm.waiting_for_anime_action)
    await message.answer("Повертаємось до дій з аніме. Оберіть дію:", reply_markup=keyboard)


# Асинхронна функція для надсилання POST-запиту до API
async def send_media_to_api_async(media_data: dict):
    url = f"{os.getenv('API_URL', 'http://api:8000')}/api/media/"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=media_data) as resp:
            resp.raise_for_status()
            return await resp.json()
        
# Асинхронна функція для надсилання PATCH-запиту до API
async def patch_media_to_api_async(media_data: dict):
    url = f"{os.getenv('API_URL', 'http://api:8000')}/api/media/{media_data['id']}/"
    async with aiohttp.ClientSession() as session:
        async with session.patch(url, json=media_data) as resp:
            resp.raise_for_status()
            return await resp.json()
        
@router.message(MediaForm.waiting_for_title, F.text == "Назад")
@router.message(MediaForm.waiting_for_status, F.text == "Назад")
@router.message(MediaForm.waiting_for_episode, F.text == "Назад")
@router.message(MediaForm.waiting_for_edit_title, F.text == "Назад")
async def anime_add_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Додавання скасовано. Повертаємось до вибору категорії.",
        reply_markup=get_keyboard(categories)
    )

async def handle_status_entered(message, state, is_edit=False):
    data = await state.get_data()
    user_id = message.from_user.id if message.from_user is not None else None
    media_data = {
        "title": data["title"],
        "category": "anime",
        "status": message.text,
        "current_episode": 0 if message.text == "Заплановано" else None,
        "user_id": user_id,
        "username": message.from_user.username if message.from_user is not None else None,
    }
    try:
        if is_edit:
            media_data["id"] = data["id"]
            media_data.pop("user_id", None)
            await patch_media_to_api_async(media_data)
            await message.answer("Аніме відредаговано! Повертаємось до вибору категорії.", reply_markup=get_keyboard(categories))
        else:
            await send_media_to_api_async(media_data)
            await message.answer("Аніме додано! Повертаємось до вибору категорії.", reply_markup=get_keyboard(categories))
    except Exception as e:
        await message.answer(f"Сталася помилка: {e}")
    await state.clear()