from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from ..media_shared import get_user_media
from ..constants import CATEGORY_LABELS, STATUS_LABELS
import matplotlib.pyplot as plt
from io import BytesIO

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
        # Для діаграми
        pie_labels = []
        pie_counts = []
        for status, status_label in STATUS_LABELS.items():
            count = cat_stats["statuses"].get(status, 0)
            percent = int(count / total * 100) if total else 0
            text += f"  {status_label}: <b>{count}</b> ({percent}%)\n"
            if count > 0:
                pie_labels.append(status_label)
                pie_counts.append(count)
            if count > max_count:
                max_count = count
                max_status = status_label
        if max_status:
            text += f"  Найпопулярніший статус: <b>{max_status}</b> ({max_count} з {total})\n"
        text += "\n"

        # Генеруємо кругову діаграму для цієї категорії
        if pie_counts:
            # Кастомна палітра без жовтого
            custom_colors = ["#4e79a7", "#f28e2b", "#59a14f", "#e15759", "#76b7b2", "#b07aa1"]
            fig, ax = plt.subplots(figsize=(6, 6), dpi=120)
            pie_result = ax.pie(
                pie_counts,
                labels=pie_labels,
                autopct='%1.0f%%',
                startangle=90,
                colors=custom_colors[:len(pie_counts)],
                wedgeprops=dict(width=0.5, edgecolor='w', linewidth=2),
                pctdistance=0.7,
                shadow=True
            )
            if len(pie_result) == 3:
                wedges, texts, autotexts = pie_result
                plt.setp(autotexts, size=16, weight="bold", color="white")
            else:
                wedges, texts = pie_result
            plt.setp(texts, size=14)
            ax.set_title(f"{cat_label}", fontsize=18, fontweight='bold')
            # Легенда під діаграмою
            ax.legend(wedges, pie_labels, title="Статуси", loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol=2)
            plt.tight_layout(rect=(0, 0.05, 1, 1))
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            await message.answer_photo(
                BufferedInputFile(buf.read(), filename=f"{cat_label}_pie.png"),
                caption=f"Статуси для {cat_label.lower()}"
            )

    await message.answer(text, parse_mode="HTML")
