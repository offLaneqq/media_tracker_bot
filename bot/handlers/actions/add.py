from aiogram import F, Router
from ..media_shared import MediaForm, valid_statuses, patch_media_to_api_async, send_media_to_api_async, handle_status_entered
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from ..constants import categories, get_keyboard
from .translation import translate_to_english

router = Router()

# Хендлер для старту додавання аніме


@router.message(MediaForm.waiting_for_anime_action, F.text == "Додати аніме")
async def start_add_anime(message: Message, state: FSMContext):
    await state.set_data({"mode": "add"})
    await message.answer("Введіть назву аніме:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    ))
    await state.set_state(MediaForm.waiting_for_title)


@router.message(MediaForm.waiting_for_title)
async def anime_title_entered(message: Message, state: FSMContext):
    title_uk = message.text if message.text is not None else ""
    title_en = await translate_to_english(title_uk)

    data = await state.get_data()
    # Якщо режим редагування — шукаємо аніме у списку
    if data.get("mode") == "edit":
        media_list = data.get("media_list", [])
        selected = next(
            (m for m in media_list if m["title"] == message.text), None)
        if not selected:
            await message.answer("Аніме не знайдено у вашому списку. Спробуйте ще раз або натисніть 'Назад'.")
            return
        await state.update_data(
            title=selected["title"],
            title_en=selected.get("title_en", ""),
            id=selected["id"],  # Зберігаємо id для PATCH
            status=selected["status"],
            current_episode=selected["current_episode"]
        )
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(
                text=status)] for status in valid_statuses] + [[KeyboardButton(text="Назад")]],
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
        await state.update_data(title=title_uk, title_en=title_en)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(
                text=status)] for status in valid_statuses] + [[KeyboardButton(text="Назад")]],
            resize_keyboard=True
        )
        await message.answer(
            f"Ваша назва: <b>{title_uk}</b>\nАнглійською: <b>{title_en}</b>\nВиберіть статус (Заплановано/Дивлюсь/Переглянуто):",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await state.set_state(MediaForm.waiting_for_status)


@router.message(MediaForm.waiting_for_status)
async def anime_status_entered(message: Message, state: FSMContext):
    if message.text not in valid_statuses:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(
                text=status)] for status in valid_statuses] + [[KeyboardButton(text="Назад")]],
            resize_keyboard=True
        )
        await message.answer("Будь ласка, виберіть статус з клавіатури:", reply_markup=keyboard)
        return

    await state.update_data(status=message.text)
    data = await state.get_data()
    if message.text == "Заплановано":
        await handle_status_entered(message, state, is_edit=(data.get("mode") == "edit"))
    else:
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
        "title_en": data.get("title_en", ""),
        "category": "anime",
        "status": data["status"],
        "current_episode": int(message.text),
        "user_id": user_id,
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
