
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import html
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# categories = ["Аніме 🍥", "Фільми 🎬", "Книги 📚"]
categories = ["Аніме", "Фільми", "Книги"]

def get_keyboard(array):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cat)] for cat in array],
        resize_keyboard=True
)

def register_handlers(dp):
    
    actions = {
            "Аніме": ["Додати аніме", "Редагувати аніме", "Переглянути список аніме", "Назад"],
            "Фільми": ["Додати фільм", "Редагувати фільм", "Переглянути список фільмів", "Назад"],
            "Книги": ["Додати книгу", "Редагувати книгу", "Переглянути список книг", "Назад"]
        }
    
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

    @dp.message(lambda msg: msg.text in categories)
    async def category_handler(message: Message) -> None:
        
        category = message.text if message.text is not None else ""
        keyboard = get_keyboard(actions.get(category, []))

        await message.answer(f"Ви вибрали категорію: {message.text}. Оберіть дію нижче.", reply_markup=keyboard)
    
    # @dp.message(lambda msg: msg.text in get_all_actions())
    # async def action_handler(message: Message) -> None:
    #     """Обробник дій для категорій"""
    #     action = message.text
    #     category = get_category_by_action(action)
        
    #     if action is not None and action.startswith("Додати"):
    #         await message.answer(f"Введіть назву для додавання в категорію '{category}':")
    #         # Тут буде логіка очікування введення назви
            
    #     elif action is not None and action.startswith("Редагувати"):
    #         await message.answer(f"Функція редагування для категорії '{category}' буде реалізована пізніше.")
            
    #     elif action is not None and action.startswith("Переглянути список"):
    #         await message.answer(f"Список у категорії '{category}': (поки що пустий)")
        
    @dp.message(lambda msg: msg.text == "Назад")
    async def back_handler(message: Message) -> None:
        """
        Handler for the "Назад" button to return to category selection
        """
        keyboard = get_keyboard(categories)
        await message.answer("Повертаємось до вибору категорії. Оберіть категорію:", reply_markup=keyboard)