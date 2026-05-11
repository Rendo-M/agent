import os
import sys
import asyncio

# Ensure the project root is on sys.path when running bot/bot.py directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from aiogram import Bot, Dispatcher
from aiogram.types import Message

from dotenv import load_dotenv
from bot.client import ApiClient
from bot.command_handler import BotCommandHandler
from services.reminders import ReminderEngine
from services.logger import log_message

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()
api_client = ApiClient()
reminder_engine = ReminderEngine(bot=bot)
command_handler = BotCommandHandler(api_client=api_client, reminder_engine=reminder_engine)

@dp.message()
async def handle_message(message: Message):
    """Forward incoming Telegram messages to the command handler. / Перенаправляет входящие сообщения Telegram в обработчик команд."""
    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name or "Unknown"
    text = message.text or ""
    log_message(username, user_id, "rsv", text)
    await command_handler.handle_message(message)

async def main() -> None:
    """Start the bot polling loop and the reminder worker. / Запускает polling бота и воркер напоминаний."""
    reminder_task = asyncio.create_task(reminder_engine.start())
    try:
        await dp.start_polling(bot, timeout=60)
    finally:
        reminder_engine.stop()
        await reminder_task
        await api_client.close()

if __name__ == "__main__":
    asyncio.run(main())