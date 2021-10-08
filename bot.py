import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.bot_command import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import configparser
from app.handlers.registration import register_handlers_user
from app.handlers.common import register_handlers_common
from app.handlers.book import register_handlers_book
from app.handlers.birthday import register_handlers_birthday
from app.handlers.admin import register_handlers_admin
from app.notification.notification import send_notification_to_admin, run_notification
import asyncio
from time import sleep


logger=logging.getLogger(__name__)

async def set_commands(bot: Bot):
    commads=[
        BotCommand(command="/reg", description="Зарегистрироваться"),
        BotCommand(command="/book", description="Отменить текущее действие"),
        BotCommand(command="/birthday", description="Отменить текущее действие"),
        BotCommand(command="/cancel", description="Отменить текущее действие"),
    ]
    await bot.set_my_commands(commads)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    config=configparser.ConfigParser()
    config.read("config/bot.ini")

    bot=Bot(token=config["tg_bot"]["token"])
    dp=Dispatcher(bot, storage=MemoryStorage())

    register_handlers_common(dp)
    register_handlers_user(dp)
    register_handlers_book(dp)
    register_handlers_birthday(dp)
    register_handlers_admin(dp)

    await set_commands(bot)

    await dp.start_polling()


async def cic():
    taskA=loop.create_task(main())
    config = configparser.ConfigParser()
    config.read("config/bot.ini")
    bot = Bot(token=config["tg_bot"]["token"])
    taskB=loop.create_task(run_notification(bot))
    await asyncio.wait([taskA, taskB])

if __name__=="__main__":
    try:
        loop=asyncio.get_event_loop()
        loop.run_until_complete(cic())
    except:
        pass