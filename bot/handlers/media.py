import aiohttp, os

from aiogram import F, Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import aiohttp, os

router = Router()

# FSM для додавання аніме
class AddAnime(StatesGroup):
    waiting_for_title = State()
    waiting_for_status = State()
    waiting_for_episode = State()

# Асинхронна функція для надсилання POST-запиту до API
async def send_media_to_api_async(media_data: dict):
    url = f"{os.getenv('API_URL', 'http://api:8000')}/api/media/"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=media_data) as resp:
            resp.raise_for_status()
            return await resp.json()
        

# Хендлер для старту додавання аніме
@router.message(F.text == "Додати аніме")
async def start_add_anime(message: Message, state: FSMContext):
    await message.answer("Введіть назву аніме:")
    await state.set_state(AddAnime.waiting_for_title)

@router.message(AddAnime.waiting_for_title)
async def anime_title_entered(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="заплановано")],
            [KeyboardButton(text="дивлюсь")],
            [KeyboardButton(text="переглянуто")]
        ],
        resize_keyboard=True
    )
    await message.answer("Введіть статус (заплановано/дивлюсь/переглянуто):", reply_markup=keyboard)
    await state.set_state(AddAnime.waiting_for_status)

@router.message(AddAnime.waiting_for_status)
async def anime_status_entered(message: Message, state: FSMContext):
    await state.update_data(status=message.text)
    await message.answer("Введіть номер серії:")
    await state.set_state(AddAnime.waiting_for_episode)

@router.message(AddAnime.waiting_for_episode)
async def anime_episode_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text is None:
        await message.answer("Будь ласка, введіть номер серії.")
        return
    user_id = message.from_user.id if message.from_user is not None else None
    media_data = {
        "title": data["title"],
        "category": "anime",
        "status": data["status"],
        "current_episode": int(message.text),
        "user_id": user_id,  # або інший спосіб отримати user_id
        "username": message.from_user.username if message.from_user is not None else None,
    }
    try:
        await send_media_to_api_async(media_data)
        await message.answer("Аніме додано!")
    except Exception as e:
        await message.answer(f"Сталася помилка при додаванні: {e}")
    await state.clear()

# Аналогічно можна реалізувати FSM для фільмів та книг