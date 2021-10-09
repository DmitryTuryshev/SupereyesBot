import logging
from aiogram import Bot, Dispatcher
from aiogram.types.bot_command import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import configparser
from app.handlers.registration import register_handlers_user
from app.handlers.common import register_handlers_common
from app.handlers.book import register_handlers_book
from app.handlers.birthday import register_handlers_birthday
from app.handlers.admin import register_handlers_admin
from app.notification.notification import run_notification
import asyncio

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commads = [
        BotCommand(command="/reg", description="Зарегистрироваться"),
        BotCommand(command="/book", description="Книги"),
        BotCommand(command="/birthday", description="Ближайший ДР"),
        BotCommand(command="/cancel", description="Отменить текущее действие"),
    ]
    await bot.set_my_commands(commads)


async def main(bot: Bot):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_common(dp)
    register_handlers_user(dp)
    register_handlers_book(dp)
    register_handlers_birthday(dp)
    register_handlers_admin(dp)

    await set_commands(bot)

    await dp.start_polling()


async def cic():
    config = configparser.ConfigParser()
    config.read("config/bot.ini")
    bot = Bot(token=config["tg_bot"]["token"])
    taskA = loop.create_task(main(bot))
    taskB = loop.create_task(run_notification(bot))
    await asyncio.wait([taskA, taskB])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cic())
