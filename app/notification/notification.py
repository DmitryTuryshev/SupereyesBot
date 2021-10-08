from aiogram import Bot
from app.database.db_work import get_users_by_cur_date, get_user, get_books_by_user, get_users_by_notification, get_users_by_cur_date_n, set_last_notification_date
import configparser
from aiogram import Bot, types
from time import sleep
import asyncio


async def send_notification_to_admin(bot: Bot):
    users_n=get_users_by_notification()

    config=configparser.ConfigParser()
    config.read("config/bot.ini")
    before_day=config["notification"]["before"]
    users=get_users_by_cur_date_n(before_day)
    if len(users) < 1:
        print("В ближайшее время нет именинников!")
        return
    else:
        if len(users) == 1:
            mes = "Именинник:\n\n".upper()
        else:
            mes = "Именинники: \n\n".upper()
        # await message.answer(mes, parse_mode=types.ParseMode.HTML)

        for user in users:
            set_last_notification_date(user[0])
            date = user[6].split("-")
            mes += f"<b>{date[2]}.{date[1]} - "
            mes += user[1]
            mes += "</b>\n"
            books=get_books_by_user(user[0])
            if not books or books is None:
                mes += "    Нет ни одной книги\n\n"
            else:
                for index, book in enumerate(books):
                    if index>3:
                        break
                    mes += f"    Название:  <i>{book[1]}</i>\n"
                    mes += f"    Автор:  <i>{book[2]}</i>\n"
                    mes += f"    Приоритет:  <i>{book[4]}</i>\n"
                    if book[3]=="active":
                        mes += f"    Статус:  <i>активна</i>\n\n"
                    else:
                        mes += f"    Статус:  <i>подарена</i>\n\n"

    mes += "\nменю: /cancel"
    if len(users_n) < 1:
        print("Нет получателей рассылки")
        return

    for user in users_n:
        await bot.send_message(user[0], mes, parse_mode=types.ParseMode.HTML)

async def run_notification(bot: Bot):
    while True:
        await send_notification_to_admin(bot)
        await asyncio.sleep(60)

