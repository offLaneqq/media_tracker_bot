from aiogram import F, Router
from ..media_shared import MediaForm, valid_statuses, get_user_media
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

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