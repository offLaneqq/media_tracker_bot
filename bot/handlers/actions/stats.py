from aiogram import Router, F
from aiogram.types import Message
from ..media_shared import get_user_media
from ..constants import CATEGORY_LABELS, STATUS_LABELS

router = Router()


@router.message(F.text == "Моя статистика")
async def show_full_stats(message: Message, state):
    user_id = message.from_user.id if message.from_user is not None else None
    media_list = await get_user_media(user_id)
    if not media_list:
        await message.answer("У вас ще немає доданих медіа.")
        return

    # Групуємо по категоріях
    stats = {}
    for item in media_list:
        cat = item.get("category", "anime")
        stats.setdefault(cat, {"total": 0, "statuses": {}})
        stats[cat]["total"] += 1
        status = item.get("status", "Заплановано")
        stats[cat]["statuses"][status] = stats[cat]["statuses"].get(
            status, 0) + 1

    text = "<b>Ваша персональна статистика:</b>\n\n"
    for cat, cat_label in CATEGORY_LABELS.items():
        cat_stats = stats.get(cat)
        if not cat_stats:
            continue
        total = cat_stats["total"]
        text += f"📚 <b>{cat_label}</b>: <b>{total}</b>\n"
        max_status = None
        max_count = 0
        for status, status_label in STATUS_LABELS.items():
            count = cat_stats["statuses"].get(status, 0)
            percent = int(count / total * 100) if total else 0
            text += f"  {status_label}: <b>{count}</b> ({percent}%)\n"
            if count > max_count:
                max_count = count
                max_status = status_label
        if max_status:
            text += f"  Найпопулярніший статус: <b>{max_status}</b> ({max_count} з {total})\n"
        text += "\n"

    await message.answer(text, parse_mode="HTML")
