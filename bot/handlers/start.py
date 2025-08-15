from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import html
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from .constants import categories, actions, get_keyboard

def register_handlers(dp):
    
    def get_all_actions():
        """Повертає список всіх дій для всіх категорій (крім 'Назад')"""
        all_actions = []
        for actions_list in actions.values():
            all_actions.extend([action for action in actions_list if action != "Назад"])
        return all_actions
    
    def get_category_by_action(action_text):
        """Знаходить категорію за текстом дії"""
        for category, category_actions in actions.items():
            if action_text in category_actions:
                return category
        return None
    
    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        """
        This handler receives messages with `/start` command
        """
        user_full_name = message.from_user.full_name if message.from_user else "User"

        keyboard = get_keyboard(categories)
        
        await message.answer(
            f"Привіт, {user_full_name}! Я Media Tracker Bot. Я готовий до роботи. Оберіть категорію:",
            reply_markup=keyboard
        )

    @dp.message(lambda msg: msg.text == "Назад")
    async def back_handler(message: Message, state: FSMContext) -> None:
        """
        Handler for the "Назад" button to return to category selection
        """
        await state.clear()  # Додаємо очищення FSM!
        keyboard = get_keyboard(categories)
        await message.answer("Повертаємось до вибору категорії. Оберіть категорію:", reply_markup=keyboard)