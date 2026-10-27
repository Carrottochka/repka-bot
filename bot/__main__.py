import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN
from bot.handlers import router

_LOG_PATH = Path(__file__).resolve().parent.parent / "bot.log"


def _require_token() -> None:
    if not BOT_TOKEN or BOT_TOKEN.startswith("123456:"):
        raise SystemExit(
            "Укажите токен бота в telegram-bot/.env: BOT_TOKEN=...\n"
            "Токен выдаёт @BotFather после команды /newbot."
        )


async def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(_LOG_PATH, encoding="utf-8"),
        ],
    )
    bot = Bot(BOT_TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    _require_token()
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
