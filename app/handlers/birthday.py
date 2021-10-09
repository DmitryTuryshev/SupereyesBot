
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from app.database.db_work import get_users_by_cur_date, get_user, get_books_by_user

from app.guard.check import check_access, check_reg


async def birthday_start(message: types.Message, state: FSMContext):
    await state.finish()

    if not check_access(message.from_user.id):
        await message.answer('У вас нет доступа')
        return

    access_u = get_user(message.from_user.id)
    if not check_reg(message.from_user.id):
        await message.answer('Вы не зарегистрированы.\n'
                             'Для регистрации: /reg\n'
                             'Меню: /cancel')
        return

    users = get_users_by_cur_date()

    if len(users) < 1:
        mes = "В ближайшее время нет именинников!\n\n" \
              "Меню: /cancel"
        await message.answer(mes, parse_mode=types.ParseMode.HTML)
        return
    else:

        flag_check_permission = (access_u[2] == 'admin' or access_u[2] == 's_admin')
        if len(users) == 1:
            mes = "Именинник:\n\n".upper()
        else:
            mes = "Именинники: \n\n".upper()
        # await message.answer(mes, parse_mode=types.ParseMode.HTML)

        for user in users:
            date = user[6].split("-")
            mes += f"<b>{date[2]}.{date[1]} - "
            mes += user[1]
            mes += "</b>\n"
            if flag_check_permission:
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
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


def register_handlers_birthday(dp: Dispatcher):
    dp.register_message_handler(birthday_start, commands=["birthday"], state="*")
