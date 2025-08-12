import aiohttp, os
import logging

from aiogram import F, Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from handlers.start import categories, get_keyboard

router = Router()

valid_statuses = ["Заплановано", "Дивлюсь", "Переглянуто"]

# FSM для додавання аніме
class MediaForm(StatesGroup):
    waiting_for_title = State()
    waiting_for_status = State()
    waiting_for_episode = State()
    waiting_for_filter_status = State()
    waiting_for_edit_title = State()
    waiting_for_anime_action = State()

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

# Хендлер для старту додавання аніме
@router.message(MediaForm.waiting_for_anime_action, F.text == "Додати аніме")
async def start_add_anime(message: Message, state: FSMContext):
    await state.set_data({"mode": "add"})
    await message.answer("Введіть назву аніме:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    ))
    await state.set_state(MediaForm.waiting_for_title)
    
# Хендлер для редагування записів 
@router.message(MediaForm.waiting_for_anime_action, F.text == "Редагувати аніме")
async def start_edit_anime(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user is not None else None
    media_list = await get_user_media(user_id)
    if not media_list:
        await message.answer("У вас ще немає доданих аніме.")
        return
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=media["title"])] for media in media_list] + [[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    await state.set_data({"mode": "edit", "media_list": media_list})
    await message.answer("Оберіть аніме для редагування:", reply_markup=keyboard)
    await state.set_state(MediaForm.waiting_for_edit_title)

@router.message(MediaForm.waiting_for_title)
async def anime_title_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    # Якщо режим редагування — шукаємо аніме у списку
    if data.get("mode") == "edit":
        media_list = data.get("media_list", [])
        selected = next((m for m in media_list if m["title"] == message.text), None)
        if not selected:
            await message.answer("Аніме не знайдено у вашому списку. Спробуйте ще раз або натисніть 'Назад'.")
            return
        await state.update_data(
            title=selected["title"],
            id=selected["id"],  # Зберігаємо id для PATCH
            status=selected["status"],
            current_episode=selected["current_episode"]
        )
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=status)] for status in valid_statuses] + [[KeyboardButton(text="Назад")]],
            resize_keyboard=True
        )
        await message.answer(
            f"Поточний статус: <b>{selected['status']}</b>\n"
            f"Поточна серія: <b>{selected['current_episode']}</b>\n"
            "Виберіть новий статус (Заплановано/Дивлюсь/Переглянуто):",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await state.update_data(title=message.text)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=status)] for status in valid_statuses] + [[KeyboardButton(text="Назад")]],
            resize_keyboard=True
        )
        await message.answer("Виберіть статус (Заплановано/Дивлюсь/Переглянуто):", reply_markup=keyboard)
    await state.set_state(MediaForm.waiting_for_status)

@router.message(MediaForm.waiting_for_status)
async def anime_status_entered(message: Message, state: FSMContext): 
    
    if message.text not in valid_statuses:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=status)] for status in valid_statuses] + [[KeyboardButton(text="Назад")]],
            resize_keyboard=True
        )
        await message.answer("Будь ласка, виберіть статус з клавіатури:", reply_markup=keyboard)
        return
    
    await state.update_data(status=message.text)
    await message.answer("Введіть номер серії:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    ))
    await state.set_state(MediaForm.waiting_for_episode)

@router.message(MediaForm.waiting_for_episode)
async def anime_episode_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text is None:
        await message.answer("Будь ласка, введіть номер серії.")
        return
    try:
        episode = int(message.text)
        if episode <= 0:
            raise ValueError("Номер серії має бути додатнім числом.")
    except ValueError:
        await message.answer("Будь ласка, введіть коректний номер серії.")
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
        if data.get("mode") == "edit":
            media_data["id"] = data["id"]
            media_data.pop("user_id", None) 
            await patch_media_to_api_async(media_data)
            await message.answer("Аніме відредаговано! Повертаємось до вибору категорії.", reply_markup=get_keyboard(categories))
        else:
            await send_media_to_api_async(media_data)
            await message.answer("Аніме додано! Повертаємось до вибору категорії.", reply_markup=get_keyboard(categories))
    except Exception as e:
        await message.answer(f"Сталася помилка при додаванні: {e}")
    await state.clear()
 
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

@router.message(MediaForm.waiting_for_anime_action, F.text == "Переглянути список аніме")
async def show_anime_list(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user is not None else None
    media_list = await get_user_media(user_id)
    if not media_list:
        await message.answer("У вас ще немає доданих аніме.")
        return

    # Формуємо таблицю з нумерацією та вирівнюванням
    table = "<b>Ваш список аніме:</b>\n\n"
    table += f"<pre>{'№':<3} {'Назва':<22} {'Статус':<12} {'Серія':<5}\n"
    table += "-" * 45 + "\n"
    for idx, media in enumerate(media_list, 1):
        table += f"{idx:<3} {media['title'][:20]:<22} {media['status']:<12} {str(media['current_episode']):<5}\n"
    table += "</pre>"
    await message.answer(table, parse_mode="HTML")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=status)] for status in valid_statuses] + [[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    # Зберігаємо prev_state для повернення до дій з аніме
    await state.update_data(prev_state=None)  # або інший стан, якщо потрібно
    await message.answer("Бажаєте переглянути аніме за статусом? Оберіть статус:", reply_markup=keyboard)
    await state.set_state(MediaForm.waiting_for_filter_status)

@router.message(F.text == "Переглянути за статусом")
async def choose_status(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=status)] for status in valid_statuses] + [[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    await message.answer("Оберіть статус для перегляду:", reply_markup=keyboard)
    await state.set_state(MediaForm.waiting_for_filter_status)  # Використовуємо новий стан!

@router.message(MediaForm.waiting_for_filter_status)
async def show_by_status(message: Message, state: FSMContext):
    if message.text not in valid_statuses:
        await message.answer("Будь ласка, оберіть статус з клавіатури.")
        return
    user_id = message.from_user.id if message.from_user is not None else None
    media_list = await get_user_media(user_id)
    filtered = [m for m in media_list if m["status"] == message.text]
    if not filtered:
        await message.answer("Немає аніме з таким статусом.")
        await state.clear()
        return
    table = "<b>Ваші аніме зі статусом:</b>\n\n"
    table += f"<pre>{'№':<3} {'Назва':<22} {'Серія':<5}\n"
    table += "-" * 32 + "\n"
    for idx, media in enumerate(filtered, 1):
        table += f"{idx:<3} {media['title'][:20]:<22} {str(media['current_episode']):<5}\n"
    table += "</pre>"
    await message.answer(table, parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    ))
    await state.clear()

from typing import Optional

async def get_user_media(user_id: Optional[int]):
    url = f"{os.getenv('API_URL', 'http://api:8000')}/api/media/?telegram_id={user_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

@router.message(MediaForm.waiting_for_edit_title)
async def anime_edit_title_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    media_list = data.get("media_list", [])
    selected = next((m for m in media_list if m["title"] == message.text), None)
    if not selected:
        await message.answer("Аніме не знайдено у вашому списку. Спробуйте ще раз або натисніть 'Назад'.")
        return
    await state.update_data(
        title=selected["title"],
        id=selected["id"],
        status=selected["status"],
        current_episode=selected["current_episode"]
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=status)] for status in valid_statuses] + [[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    await message.answer(
        f"Поточний статус: <b>{selected['status']}</b>\n"
        f"Поточна серія: <b>{selected['current_episode']}</b>\n"
        "Виберіть новий статус (Заплановано/Дивлюсь/Переглянуто):",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(MediaForm.waiting_for_status)

@router.message(F.text == "Назад")
async def go_back(message: Message, state: FSMContext):
    data = await state.get_data()
    prev_state = data.get("prev_state")
    if prev_state:
        await state.set_state(prev_state)
        # Далі — повторіть питання для цього стану (наприклад, знову покажіть клавіатуру)
        # Можна винести логіку повтору питання у окрему функцію для кожного стану
    else:
        # Якщо prev_state немає — повертаємо на головну
        await state.clear()
        await message.answer(
            "Повертаємось до вибору категорії.",
            reply_markup=get_keyboard(categories)
        )

@router.message(MediaForm.waiting_for_filter_status, F.text == "Назад")
async def back_to_anime_actions(message: Message, state: FSMContext):
    actions = ["Додати аніме", "Редагувати аніме", "Переглянути список аніме"]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=action)] for action in actions],
        resize_keyboard=True
    )
    await state.set_state(MediaForm.waiting_for_anime_action)
    await message.answer("Повертаємось до дій з аніме. Оберіть дію:", reply_markup=keyboard)

@router.message(F.text == "Аніме")
async def anime_category_selected(message: Message, state: FSMContext):
    actions = ["Додати аніме", "Редагувати аніме", "Переглянути список аніме"]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=action)] for action in actions] + [[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    await state.set_state(MediaForm.waiting_for_anime_action)
    await message.answer("Ви вибрали категорію: Аніме. Оберіть дію нижче.", reply_markup=keyboard)
