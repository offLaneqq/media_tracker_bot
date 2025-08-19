from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from ..media_shared import MediaForm, get_user_media
import csv
from io import StringIO
from datetime import datetime
import zoneinfo 

router = Router()

@router.message(MediaForm.waiting_for_anime_action, F.text == "Експортувати аніме ⬆️")
async def export_anime(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user is not None else None
    media_list = await get_user_media(user_id)
    if not media_list:
        await message.answer("У вас ще немає доданих аніме.")
        return

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Назва", "Статус", "Серія"])
    for media in media_list:
        writer.writerow([media["title"], media["status"], media["current_episode"]])
    output.seek(0)

    kyiv_tz = zoneinfo.ZoneInfo("Europe/Kyiv")
    now = datetime.now(kyiv_tz).strftime("%Y%m%d_%H%M")
    filename = f"anime_export_{now}.csv"

    # Додаємо BOM для коректного відкриття в Excel
    bom = '\ufeff'
    csv_bytes = (bom + output.getvalue()).encode("utf-8")

    await message.answer_document(
        types.BufferedInputFile(csv_bytes, filename=filename),
        caption="Ваш експортований список аніме"
    )