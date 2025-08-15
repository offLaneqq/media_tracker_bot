import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import asyncio
from handlers.start import register_handlers

# Завантаження змінних середовища з .env
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise RuntimeError('BOT_TOKEN is not set in environment')

# Ініціалізація бота та диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
register_handlers(dp)

from handlers.media import register_media_handlers
register_media_handlers(dp)

if __name__ == '__main__':
    print('Starting bot...')
    async def main():
        await dp.start_polling(bot, skip_updates=True)
    asyncio.run(main())