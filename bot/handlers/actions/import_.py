from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from ..media_shared import MediaForm, send_media_to_api_async
from ..constants import get_keyboard, categories
import csv
from io import StringIO

router = Router()

@router.message(MediaForm.waiting_for_anime_action, F.text == "Імпортувати аніме")
async def import_anime_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Надішліть CSV-файл, експортований з бота або створений вручну. Формат: Назва,Статус,Серія",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(MediaForm.waiting_for_import_file)

@router.message(MediaForm.waiting_for_import_file, F.document)
async def import_anime_file(message: types.Message, state: FSMContext, bot):
    if not message.document:
        await message.answer("Будь ласка, надішліть файл у форматі CSV.")
        return
    file = await bot.get_file(message.document.file_id)
    file_path = file.file_path
    file_bytes = await bot.download_file(file_path)
    content = file_bytes.read().decode("utf-8-sig")  # utf-8-sig для BOM

    reader = csv.reader(StringIO(content))
    header = next(reader, None)
    count = 0
    for row in reader:
        if len(row) < 3:
            continue
        title, status, episode = row[0], row[1], row[2]
        try:
            episode = int(episode)
        except Exception:
            episode = 0
        user_id = message.from_user.id if message.from_user else None
        username = message.from_user.username if message.from_user else None
        media_data = {
            "title": title,
            "category": "anime",
            "status": status,
            "current_episode": episode,
            "user_id": user_id,
            "username": username,
        }
        try:
            await send_media_to_api_async(media_data)
            count += 1
        except Exception:
            continue

    await message.answer(
        f"Імпорт завершено! Додано {count} записів.",
        reply_markup=get_keyboard(categories)
    )
    await state.clear()