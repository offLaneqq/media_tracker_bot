from aiogram import F, Router
from ..media_shared import MediaForm, valid_statuses, patch_media_to_api_async, send_media_to_api_async
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from ..constants import categories, get_keyboard
from .translation import translate
from .jikan import search_anime_jikan
from .ai_title import get_original_anime_title, get_ukrainian_anime_title

router = Router()

# Хендлер для старту додавання аніме


@router.message(MediaForm.waiting_for_anime_action, F.text == "Додати аніме ✍️")
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
    title_en = await get_original_anime_title(title_uk)
    search_results = await search_anime_jikan(title_en)

    if not search_results:
        await message.answer(
            f"Не знайдено аніме за назвою: {title_en}. Введіть іншу назву або спробуйте ще раз."
        )
        return

    translated_titles = []
    for anime in search_results:
        uk_title = await get_ukrainian_anime_title(anime["title"])
        genres = [g["name"] for g in anime.get("genres", [])]
        # Перекладаємо жанри на українську
        genres_uk = [translate(genre, target_lang="UK") for genre in genres]
        image_url = anime.get("images", {}).get("jpg", {}).get("image_url")
        translated_titles.append({
            "uk_title": uk_title,
            "en_title": anime["title"],
            "mal_id": anime["mal_id"],
            "genres": genres_uk,
            "image_url": image_url
        })

    buttons = [KeyboardButton(text=anime["uk_title"])
               for anime in translated_titles]
    keyboard_rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    keyboard_rows.append([KeyboardButton(text="Назад")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True
    )

    await state.update_data(
        title=title_uk,
        search_results=translated_titles
    )
    await message.answer(
        "Оберіть аніме зі списку або натисніть 'Назад':",
        reply_markup=keyboard
    )
    await state.set_state(MediaForm.waiting_for_title_selection)


@router.message(MediaForm.waiting_for_title_selection)
async def anime_title_selected(message: Message, state: FSMContext):
    data = await state.get_data()
    search_results = data.get("search_results", [])
    selected = next(
        (anime for anime in search_results if anime["uk_title"] == message.text), None)
    if not selected:
        await message.answer("Будь ласка, виберіть аніме зі списку або натисніть 'Назад'.")
        return

    if not selected.get("mal_id"):
        await message.answer("Не вдалося знайти унікальний ідентифікатор аніме. Спробуйте іншу назву.")
        return

    if not selected.get("en_title"):
        await message.answer("Не вдалося знайти англійську назву аніме. Спробуйте іншу назву.")
        return

    image_url = selected.get("image_url") or selected.get("image") or None
    genres = selected.get("genres", [])
    genres_str = ", ".join(genres) if genres else "Жанри не знайдено"

    await state.update_data(
        title_en=selected["en_title"],
        mal_id=selected["mal_id"]
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(
            text=status)] for status in valid_statuses] + [[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    await message.answer(
        f"Вибрано: <b>{selected['uk_title']}</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    if image_url:
        await message.answer_photo(
            photo=image_url,
            caption=f"<b>{selected['uk_title']}</b>\nЖанри: {genres_str}",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"<b>{selected['uk_title']}</b>\nЖанри: {genres_str}",
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

    # Якщо статус "Заплановано", одразу викликаємо фінальний хендлер
    if message.text == "Заплановано":
        await anime_episode_entered(message, state)
    else:
        await message.answer("Введіть номер серії:", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Назад")]],
            resize_keyboard=True
        ))
        await state.set_state(MediaForm.waiting_for_episode)


@router.message(MediaForm.waiting_for_episode)
async def anime_episode_entered(message: Message, state: FSMContext):
    data = await state.get_data()

    # Якщо статус "Заплановано", епізод завжди 0
    if data.get("status") == "Заплановано":
        episode = 0
    else:
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
        "status": data.get("status"),
        "current_episode": episode,
        "user_id": user_id,
        "username": message.from_user.username if message.from_user is not None else None,
    }

    if data.get("mal_id"):
        media_data["mal_id"] = data.get("mal_id")

    try:
        if data.get("mode") == "edit":
            media_data["id"] = data["id"]
            media_data.pop("user_id", None)
            await patch_media_to_api_async(media_data)
            await message.answer("Аніме відредаговано! Повертаємось до головного меню.", reply_markup=get_keyboard(categories))
        else:
            await send_media_to_api_async(media_data)
            await message.answer("Аніме додано! Повертаємось до головного меню.", reply_markup=get_keyboard(categories))
    except Exception as e:
        if str(e) == "duplicate":
            await message.answer(
                "❗️ Це аніме вже є у вашому списку!\n\nПовертаємось до головного меню.",
                reply_markup=get_keyboard(categories)
            )
        else:
            await message.answer(f"Сталася помилка: {e}")
    await state.clear()
