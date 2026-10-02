import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import common_router, file_router, callback_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def setup_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam va qo'llanma"),
        BotCommand(command="formats", description="Barcha formatlar ro'yxati"),
    ]
    await bot.set_my_commands(commands)

import os
from aiohttp import web

async def handle_health(request):
    return web.Response(text="Telegram Converter Bot is running OK!")

async def start_health_server():
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health-check server running on port {port}")
    return runner

async def main():
    if not BOT_TOKEN or "TOKEN" in BOT_TOKEN:
        logger.error("BOT_TOKEN sozlanmagan!")
        return

    logger.info("Universal Converter Bot ishga tushmoqda...")
    
    # Start health-check server for cloud/container deployment
    health_runner = await start_health_server()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Register routers in priority order
    dp.include_router(common_router)
    dp.include_router(callback_router)
    dp.include_router(file_router)

    # Setup bot commands menu
    await setup_commands(bot)

    # Do not drop pending updates so offline messages get processed
    await bot.delete_webhook(drop_pending_updates=False)

    bot_info = await bot.get_me()
    logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username} ({bot_info.first_name})")

    try:
        while True:
            try:
                await dp.start_polling(bot)
                break
            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as poll_err:
                logger.error(f"Polling xatoligi: {poll_err}. 5 soniyadan keyin qayta ulanadi...")
                await asyncio.sleep(5)
    finally:
        await health_runner.cleanup()
        await bot.session.close()
        logger.info("Bot to'xtatildi.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
