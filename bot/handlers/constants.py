from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# categories = ["Аніме 🍥", "Фільми 🎬", "Книги 📚"]
categories = ["Аніме", "Фільми", "Книги"]

actions = {
    "Аніме": ["Додати аніме", "Редагувати аніме", "Видалити аніме", "Переглянути список аніме", "Експортувати аніме", "Назад"],
    "Фільми": ["Додати фільм", "Редагувати фільм", "Видалити фільм", "Переглянути список фільмів", "Експортувати фільми", "Назад"],
    "Книги": ["Додати книгу", "Редагувати книгу", "Видалити книгу", "Переглянути список книг", "Експортувати книги", "Назад"]
}

def get_keyboard(array):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cat)] for cat in array],
        resize_keyboard=True
)