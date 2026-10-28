"""Main entry point for Remedial Hub Telegram Bot.

Initializes the bot client, memory storage, database, command menu, and starts
long-polling for updates.
"""

from __future__ import annotations

import asyncio
import logging
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import config
from database import db
from handlers import admin_router, registration_router, start_menu_router

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("RemedialHubBot")


async def setup_bot_commands(bot: Bot) -> None:
    """Register menu commands with Telegram."""
    commands = [
        BotCommand(command="start", description="ዋና ሜኑ / Main Menu"),
        BotCommand(command="status", description="የምዝገባ ሁኔታ / Check Status"),
        BotCommand(command="admin", description="የአድሚን ዳሽቦርድ / Admin Panel"),
    ]
    try:
        await bot.set_my_commands(commands)
        logger.info("Bot menu commands registered successfully")
    except Exception as e:
        logger.warning("Failed to register menu commands: %s", e)


async def main() -> None:
    """Run bot startup sequence and start long-polling."""
    logger.info("=========================================")
    logger.info("  Starting Remedial Hub Telegram Bot 🚀  ")
    logger.info("=========================================")

    # Validate Bot Token
    if not config.BOT_TOKEN or "ExamplePlaceholder" in config.BOT_TOKEN:
        logger.error(
            "CRITICAL: BOT_TOKEN is empty or still set to placeholder in .env!\n"
            "Please obtain a token from @BotFather and set BOT_TOKEN in .env"
        )

    # Initialize SQLite Database
    await db.init_db()

    # Initialize Bot instance with HTML parse mode and optional proxy
    session = None
    if config.PROXY_URL:
        from aiogram.client.session.aiohttp import AiohttpSession
        session = AiohttpSession(proxy=config.PROXY_URL)
        logger.info("Using configured proxy: %s", config.PROXY_URL)

    bot = Bot(
        token=config.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Initialize Dispatcher with in-memory FSM storage
    dp = Dispatcher(storage=MemoryStorage())

    # Register handlers (admin first for priority callbacks/commands, then registration, then start menu)
    dp.include_router(admin_router)
    dp.include_router(registration_router)
    dp.include_router(start_menu_router)

    # Register bot commands menu
    await setup_bot_commands(bot)

    # Drop any pending updates accumulated while the bot was offline
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning("Could not delete webhook: %s", e)

    logger.info("Bot is ready and listening for events! Administrators: %s", config.ADMIN_IDS)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Shutting down bot session...")
        await bot.session.close()
        logger.info("Bot shut down gracefully.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
