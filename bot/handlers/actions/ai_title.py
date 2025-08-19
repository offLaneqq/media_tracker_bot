import os
from google.generativeai import configure, GenerativeModel # type: ignore

# Налаштування API ключа
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")
configure(api_key=GEMINI_API_KEY)

# Створення моделі
model = GenerativeModel('gemini-1.5-flash')

async def get_original_anime_title(uk_title: str) -> str:
    prompt = (
        f'Яка оригінальна англійська назва аніме, якщо українською воно називається "{uk_title}"? '
        'Відповідь тільки назвою.'
    )
    
    # Асинхронний виклик API
    response = await model.generate_content_async(prompt)
    
    return response.text.strip()

async def get_ukrainian_anime_title(en_title: str) -> str:
    prompt = (
        f'Як українською зазвичай називають аніме "{en_title}"? '
        'Відповідь тільки назвою.'
    )
    response = await model.generate_content_async(prompt)
    return response.text.strip()
