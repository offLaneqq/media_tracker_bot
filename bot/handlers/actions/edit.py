from aiogram import F, Router
from ..media_shared import MediaForm, get_user_media, valid_statuses, patch_media_to_api_async, send_media_to_api_async, get_keyboard, categories, handle_status_entered
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()


# Хендлер для редагування записів 
@router.message(MediaForm.waiting_for_anime_action, F.text == "Редагувати аніме")
async def start_edit_anime(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user is not None else None
    media_list = await get_user_media(user_id)
    if not media_list:
        await message.answer("У вас ще немає доданих аніме.")
        return

    # Формуємо клавіатуру по два аніме на рядок
    buttons = [KeyboardButton(text=media["title"]) for media in media_list]
    keyboard_rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    keyboard_rows.append([KeyboardButton(text="Назад")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True
    )

    await state.set_data({"mode": "edit", "media_list": media_list})
    await message.answer("Оберіть аніме для редагування:", reply_markup=keyboard)
    await state.set_state(MediaForm.waiting_for_edit_title)
    
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
    data = await state.get_data()
    if message.text == "Заплановано":
        await handle_status_entered(message, state, is_edit=(data.get("mode") == "edit"))
    else:
        await message.answer("Введіть номер серії:", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Назад")]],
            resize_keyboard=True
        ))
        await state.set_state(MediaForm.waiting_for_episode)