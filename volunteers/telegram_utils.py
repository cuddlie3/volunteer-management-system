import os

from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()


async def broadcast_message(recipients, message):
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN не найден в .env")

    bot = Bot(token=token)

    sent = 0
    failed = 0

    try:
        for telegram_id in recipients:
            try:
                await bot.send_message(
                    chat_id=telegram_id,
                    text=message,
                )
                sent += 1

            except TelegramError as exc:
                print(
                    f"Ошибка отправки сообщения {telegram_id}: {exc}"
                )
                failed += 1

    finally:
        await bot.shutdown()

    return sent, failed