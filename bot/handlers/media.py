from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from .media_shared import MediaForm
from .constants import actions

from .actions.add import router as add_router
from .actions.edit import router as edit_router
from .actions.view import router as view_router
from .actions.export import router as export_router
from .actions.delete import router as delete_router
from .actions.import_ import router as import_router
from .actions.stats import router as stats_router

router = Router()


@router.message(F.text == "Аніме")
async def anime_category_selected(message: Message, state: FSMContext):
    actions_list = actions["Аніме"]
    # Формуємо клавіатуру по 2 дії в рядку
    keyboard_rows = [[KeyboardButton(text=action) for action in actions_list[i:i+2]]
                     for i in range(0, len(actions_list), 2)]
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True
    )
    await state.set_state(MediaForm.waiting_for_anime_action)
    await message.answer("Ви вибрали категорію: Аніме. Оберіть дію нижче.", reply_markup=keyboard)


def register_media_handlers(dp):
    dp.include_router(router)
    dp.include_router(add_router)
    dp.include_router(edit_router)
    dp.include_router(view_router)
    dp.include_router(export_router)
    dp.include_router(delete_router)
    dp.include_router(import_router)
    dp.include_router(stats_router)
