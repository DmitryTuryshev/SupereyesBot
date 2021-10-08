from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from app.database.db_work import get_users, block_user, get_books_by_user, get_users_by_cur_date, get_user, get_book, \
    change_status_book_by_id, get_books_by_user_all, add_book, remove_book_by_id, change_name, change_author_book, \
    change_priority_book, change_per, get_users_by_notification, change_notification
from app.guard.check import check
import configparser

birtday_day = 31


class BlockUser(StatesGroup):
    waiting_for_book_user_number = State()
    waiting_for_un_ban_user_number = State()


class StatusBook(StatesGroup):
    waiting_for_user_number = State()
    waiting_for_book_user_number = State()
    waiting_for_status_number = State()


class Permission(StatesGroup):
    waiting_for_user_number_for_give = State()
    waiting_for_user_number_for_take = State()


class Notification(StatesGroup):
    waiting_for_user_number_for_add = State()
    waiting_for_user_number_for_rem = State()


class DayNot(StatesGroup):
    waiting_for_count_day=State()


async def cmd_admin(message: types.Message, state: FSMContext):
    await state.finish()
    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return
    menu = "Админ панель:\n\n"
    menu += "1. Пользователи (/users)\n" \
            "2. Книги пользователей(/adm_book)\n" \
            "3. Управление правами (/adm_per)\n" \
            "4. Управление рассылкой (/adm_notif)\n\n" \
            "Меню: /cancel\n"

    await message.answer(
        menu
    )


async def cmd_users(message: types.Message, state: FSMContext):
    await state.finish()
    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return
    menu = "1. Список пользователей (/list_users)\n" \
           "2. Блокировка пользователей(/ban)\n" \
           "3. Разблокировка пользователей(/un_ban)\n\n" \
           "Меню: /cancel\n" \
           "Панель админа: /admin\n"
    await message.answer(menu)


async def cmd_list_users(message: types.Message, state: FSMContext):
    await state.finish()
    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    users = get_users()
    if not users or users is None:
        menu = "Нет пользователей\n\n"
    else:
        menu = "Пользователи:\n\n"
        for index, user in enumerate(users):
            menu += f"<b>{index + 1}. {user[1]}</b>\n"
    menu += "\n1. Панель админа: /admin\n" \
            "2. Меню: /cancel\n" \
            "3. Блокировка пользователей(/ban)\n" \
            "4. Разблокировка пользователей(/un_ban)\n\n"
    await message.answer(menu, parse_mode=types.ParseMode.HTML)


async def cmd_ban_user(message: types.Message, state: FSMContext):
    await state.finish()
    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    users = get_users()
    users_numbers = []
    if not users or users is None:
        menu = "Нет пользователей\n\n"
    else:
        menu = "Пользователи:\n\n"
        for index, user in enumerate(users):
            menu += f"{index + 1}. {user[1]}\n"
            users_numbers.append(user[0])
    menu += "\nПанель админа: /admin\n" \
            "Меню: /cancel\n\n" \
            "Выберите номер пользователя для блокировки:\n"
    await state.update_data(users_numbers=users_numbers)
    await message.answer(menu)
    await BlockUser.waiting_for_book_user_number.set()


async def ban_user(message: types.Message, state: FSMContext):
    try:
        index = int(message.text) - 1

        data = await state.get_data()
        id = data["users_numbers"][index]
    except:
        await message.answer("Нет пользователя под таким номером\n"
                             "Выберите другого\n"
                             "Для отмены /cancel ")
        return

    block_user(id)

    await message.answer("Пользователь заблакирован!\n"
                         "Пользователи: /users\n"
                         "Админ панель: /admin\n"
                         "Меню: /cancel")

    await state.finish()


async def cmd_un_ban_user(message: types.Message, state: FSMContext):
    await state.finish()
    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    users = get_users(0)
    users_numbers = []
    if not users or users is None:
        menu = "Нет заблакированых пользователей\n\n"
        menu += "\nПользователи: /users\n" \
                "Заблакировать пользователей: /ban\n" \
                "Панель админа: /admin\n" \
                "Меню: /cancel\n\n"
        await message.answer(menu)
        return
    else:
        menu = "Заблакированые пользователи:\n\n"
        for index, user in enumerate(users):
            menu += f"{index + 1}. {user[1]}\n"
            users_numbers.append(user[0])
    menu += "\nПользователи: /users\n" \
            "Панель админа: /admin\n" \
            "Меню: /cancel\n\n" \
            "Выберите номер пользователя для разблокировки:\n"
    await state.update_data(users_numbers=users_numbers)
    await message.answer(menu)
    await BlockUser.waiting_for_un_ban_user_number.set()


async def un_ban_user(message: types.Message, state: FSMContext):
    try:
        index = int(message.text) - 1

        data = await state.get_data()
        id = data["users_numbers"][index]
    except:
        await message.answer("Нет пользователя под таким номером\n"
                             "Выберите другого\n"
                             "Для отмены /cancel ")
        return

    block_user(id, 1)

    await message.answer("Пользователь разблакирован!\n"
                         "Пользователи: /users\n"
                         "Админ панель: /admin\n"
                         "Меню: /cancel")

    await state.finish()


async def cmd_adm_book(message: types.Message, state: FSMContext):
    await state.finish()
    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    menu = "Книги польщователей:\n\n" \
           "1. Ближайший ДР: (/adm_birthday)\n" \
           "2. Изменить статус книги: (/adm_status)\n\n" \
           "Панель админа: /admin\n" \
           "Меню: /cancel\n\n"
    await message.answer(menu)


async def cmd_adm_birthday(message: types.Message, state: FSMContext):
    await state.finish()

    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    users = get_users_by_cur_date(birtday_day)

    if len(users) < 1:
        mes = "В ближайшее время нет именинников!\n"
        mes += "Книги пользователей (/adm_book)\n"
        mes += "Админ панель (/admin)\n"
        mes += "Меню (/cancel)"
        await message.answer(mes, parse_mode=types.ParseMode.HTML)
        return
    else:
        if len(users) == 1:
            mes = "Именинник:\n\n".upper()
        else:
            mes = "Именинники: \n\n".upper()
        users_ch_status = []
        for i, user in enumerate(users):
            date = user[6].split("-")
            mes += f"<b>{i + 1}. "
            mes += user[1]
            mes += f" - {date[2]}.{date[1]}"
            mes += "</b>\n"

            users_ch_status.append(user[0])
            books = get_books_by_user_all(user[0])
            if not books or books is None:
                mes += "    Нет ни одной книги\n\n"
            else:
                for index, book in enumerate(books):
                    if index > 3:
                        break
                    mes += f"    Название:  <i>{book[1]}</i>\n"
                    mes += f"    Автор:  <i>{book[2]}</i>\n"
                    mes += f"    Приоритет:  <i>{book[4]}</i>\n"
                    if book[3] == "active":
                        mes += f"    Статус:  <i>активна</i>\n\n"
                    else:
                        mes += f"    Статус:  <i>подарена</i>\n\n"

    mes += "\nменю: /cancel\n\n"
    mes += "Выберите номер пользователя:"
    await state.update_data(users_ch_status=users_ch_status)
    await StatusBook.waiting_for_user_number.set()
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def user_number(message: types.Message, state: FSMContext):
    try:
        index = int(message.text) - 1

        data = await state.get_data()
        id = data["users_ch_status"][index]
    except:
        await message.answer("Нет пользователя под таким номером\n"
                             "Выберите другого\n"
                             "Для отмены /cancel ")
        return
    user = get_user(id)
    mes = ""
    date = user[6].split("-")
    mes += f"<b>{date[2]}.{date[1]} - "
    mes += user[1]
    mes += "</b>\n"
    books = get_books_by_user_all(user[0])
    if not books or books is None:
        mes += "\nНет ни одной книги\n"
        mes += "Книги пользователей (/adm_book)\n"
        mes += "Админ панель (/admin)\n"
        mes += "Меню (/cancel)\n"
        await message.answer(mes)
        await state.finish()
        return
    else:
        books_ch_st = []
        for index, book in enumerate(books):
            if index > 3:
                break
            mes += f"    Название:  <i>{book[1]}</i>\n"
            mes += f"    Автор:  <i>{book[2]}</i>\n"
            mes += f"    Приоритет:  <i>{book[4]}</i>\n"
            if book[3] == "active":
                mes += f"    Статус:  <i>активна</i>\n\n"
            else:
                mes += f"    Статус:  <i>подарена</i>\n\n"
            books_ch_st.append(book[0])

    mes += "Книги пользователей (/adm_book)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n"
    mes += "Выберите номер книги:"
    await message.answer(mes, parse_mode=types.ParseMode.HTML)
    await StatusBook.next()
    await state.update_data(books_ch_st=books_ch_st)


async def book_st_number(message: types.Message, state: FSMContext):
    try:
        index = int(message.text) - 1
        data = await state.get_data()
        id = data["books_ch_st"][index]
    except:
        mes = ""
        mes += "Книги пользователей (/adm_book)\n"
        mes += "Админ панель (/admin)\n"
        mes += "Меню (/cancel)\n"
        mes += "Нет книги под таким номером"
        await message.answer(mes)
        return
    book = get_book(id)
    mes = "Книга\n\n"
    mes += f"    Название:  <i>{book[1]}</i>\n"
    mes += f"    Автор:  <i>{book[2]}</i>\n"
    mes += f"    Приоритет:  <i>{book[4]}</i>\n\n"

    mes += "Книги пользователей (/adm_book)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n"
    mes += "Выберите статуса для книги\n"
    mes += "1 - активна\n"
    mes += "2 - подарена"
    await message.answer(mes, parse_mode=types.ParseMode.HTML)
    await StatusBook.next()
    await state.update_data(books_ch_id=id)


async def change_status_book(message: types.Message, state: FSMContext):
    try:
        index = int(message.text)

        if index != 1 and index != 2:
            mes = ""
            mes += "Книги пользователей (/adm_book)\n"
            mes += "Админ панель (/admin)\n"
            mes += "Меню (/cancel)\n\n"
            mes += "Нет такого действия"
            await message.answer(mes)
            return
    except:
        mes = ""
        mes += "Книги пользователей (/adm_book)\n"
        mes += "Админ панель (/admin)\n"
        mes += "Меню (/cancel)\n\n"
        mes += "Нет такого действия"
        await message.answer(mes)
        return
    print(index)
    data = await state.get_data()
    print(data)
    if index == 1:
        change_status_book_by_id(data['books_ch_id'], "active")
    else:
        change_status_book_by_id(data['books_ch_id'])

    mes = "Статус книги успешно изменен!\n\n"
    mes += "Книги пользователей (/adm_book)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)"
    await message.answer(mes)
    await state.finish()
    return


async def cmd_adm_status(message: types.Message, state: FSMContext):
    await state.finish()

    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    users = get_users()

    if len(users) < 1:
        mes = "Нет пользователей!\n"
        mes += "Книги пользователей (/adm_book)\n"
        mes += "Админ панель (/admin)\n"
        mes += "Меню (/cancel)"
        await message.answer(mes, parse_mode=types.ParseMode.HTML)
        return
    else:
        mes = "Пользователи: \n\n".upper()
        users_ch_status = []
        for i, user in enumerate(users):
            date = user[6].split("-")
            mes += f"<b>{i + 1}. "
            mes += user[1]
            mes += f" - {date[2]}.{date[1]}"
            mes += "</b>\n"
            users_ch_status.append(user[0])

    mes += "\nКниги пользователей (/adm_book)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n"
    mes += "Выберите номер пользователя:"
    await state.update_data(users_ch_status=users_ch_status)
    await StatusBook.waiting_for_user_number.set()
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def cmd_adm_per(message: types.Message, state: FSMContext):
    await state.finish()

    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return
    mes = "Управление правами:\n\n"
    mes += "1. Наделить правами администратора (/adm_give)\n"
    mes += "2. Забрать права администратора (/adm_take)\n\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)"
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def cmd_adm_give(message: types.Message, state: FSMContext):
    await state.finish()

    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    users = get_users()

    if len(users) < 1:
        mes = "Нет пользователей!\n"
        mes += "Управление правами(/adm_per)"
        mes += "Админ панель (/admin)\n"
        mes += "Меню (/cancel)"
        await message.answer(mes, parse_mode=types.ParseMode.HTML)
        return
    else:
        mes = "Ты хочешь поделиться этой властью?: \n\n"
        users_change_per = []
        for i, user in enumerate(users):
            date = user[6].split("-")
            mes += f"<b>{i + 1}. "
            mes += user[1]
            mes += f" - {date[2]}.{date[1]}"
            mes += "</b>\n"
            users_change_per.append(user[0])

    mes += "\nУправление правами (/adm_per)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n\n"
    mes += "Выберите номер пользователя:"
    await state.update_data(users_change_per=users_change_per)
    await Permission.waiting_for_user_number_for_give.set()
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def per_to_give(message: types.Message, state: FSMContext):
    try:
        index = int(message.text) - 1

        data = await state.get_data()
        id = data["users_change_per"][index]
    except:
        await message.answer("Нет пользователя под таким номером\n"
                             "Выберите другого\n"
                             "Для отмены /cancel ")
        return
    change_per(id, "admin")
    mes="Пользователь наделен властью!\n"
    mes += "\nУправление правами (/adm_per)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n\n"
    await state.finish()
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def cmd_adm_take(message: types.Message, state: FSMContext):
    await state.finish()

    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    users = get_users()

    if len(users) < 1:
        mes = "Нет пользователей!\n"
        mes += "Управление правами(/adm_per)"
        mes += "Админ панель (/admin)\n"
        mes += "Меню (/cancel)"
        await message.answer(mes, parse_mode=types.ParseMode.HTML)
        return
    else:
        mes = "Забрать власть: \n\n"
        users_change_per = []
        for i, user in enumerate(users):
            date = user[6].split("-")
            mes += f"<b>{i + 1}. "
            mes += user[1]
            mes += f" - {date[2]}.{date[1]}"
            mes += "</b>\n"
            users_change_per.append(user[0])

    mes += "\nУправление правами (/adm_per)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n\n"
    mes += "Выберите номер пользователя:"
    await state.update_data(users_change_per=users_change_per)
    await Permission.waiting_for_user_number_for_take.set()
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def per_take_up(message: types.Message, state: FSMContext):
    try:
        index = int(message.text) - 1

        data = await state.get_data()
        id = data["users_change_per"][index]
    except:
        await message.answer("Нет пользователя под таким номером\n"
                             "Выберите другого\n"
                             "Для отмены /cancel ")
        return
    change_per(id)
    mes="Пользователь понижен в должности!\n"
    mes += "\nУправление правами (/adm_per)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n\n"
    await state.finish()
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def cmd_adm_notif(message: types.Message, state: FSMContext):
    await state.finish()

    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    config=configparser.ConfigParser()
    config.read("config/bot.ini")
    day=config["notification"]["before"]
    mes ="Управление рассылкой:\n\n"
    mes += "1. Получатели (/adm_rec)\n"
    mes += "2. За сколько дней уведомлять? (/adm_day)\n"
    mes += f"    Сейчас это {day} д.\n\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n\n"
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def cmd_adm_rec(message: types.Message, state: FSMContext):
    await state.finish()

    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    users=get_users_by_notification()
    if len(users) < 1:
        mes = "Нет получателей\n\n"
    else:
        mes = "Получатели: \n\n"
        for i, user in enumerate(users):
            date = user[6].split("-")
            mes += f"<b>"
            mes += user[1]
            mes += "</b>\n"

    mes += "\n1. Добавить в рассылку (/adm_add_user_n)\n"
    mes += "2. Убрать с рассылки (/adm_rem_user_n)\n\n"
    mes += "Управление рассылкой (/adm_notif)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n\n"
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def cmd_adm_add_user_n(message: types.Message, state: FSMContext):
    await state.finish()

    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    users = get_users()

    if len(users) < 1:
        mes = "Нет пользователей!\n"
        mes += "Управление правами(/adm_per)"
        mes += "Админ панель (/admin)\n"
        mes += "Меню (/cancel)"
        await message.answer(mes)
        return
    else:
        mes = "Добавить пользователя в рассылку: \n\n"
        users_add_notification = []
        for i, user in enumerate(users):
            date = user[6].split("-")
            mes += f"<b>{i + 1}. "
            mes += user[1]
            mes += "</b>\n"
            users_add_notification.append(user[0])


    mes += "\nУправление рассылкой (/adm_notif)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n\n"
    mes += "Выберите номер пользователя:"
    await message.answer(mes, parse_mode=types.ParseMode.HTML)
    await state.update_data(users_add_notification=users_add_notification)
    await Notification.waiting_for_user_number_for_add.set()


async def add_notification_to_user(message: types.Message, state: FSMContext):
    try:
        index = int(message.text) - 1

        data = await state.get_data()
        id = data["users_add_notification"][index]
    except:
        await message.answer("Нет пользователя под таким номером\n"
                             "Выберите другого\n\n"
                             "Для отмены /cancel")
        return

    change_notification(id)
    mes="Пользователь успешно добавлен в рассылку!\n\n"
    mes += "Управление рассылкой (/adm_notif)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n"

    await state.finish()
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def cmd_adm_rem_user_n(message: types.Message, state: FSMContext):
    await state.finish()

    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return

    users = get_users_by_notification()

    if len(users) < 1:
        mes = "Нет пользователей!\n"
        mes += "Управление правами(/adm_per)"
        mes += "Админ панель (/admin)\n"
        mes += "Меню (/cancel)"
        await message.answer(mes)
        return
    else:
        mes = "Убрать пользователя с рассылки: \n\n"
        users_add_notification = []
        for i, user in enumerate(users):
            date = user[6].split("-")
            mes += f"<b>{i + 1}. "
            mes += user[1]
            mes += "</b>\n"
            users_add_notification.append(user[0])

    mes += "\nУправление рассылкой (/adm_notif)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n\n"
    mes += "Выберите номер пользователя:"
    await message.answer(mes, parse_mode=types.ParseMode.HTML)
    await state.update_data(users_add_notification=users_add_notification)
    await Notification.waiting_for_user_number_for_rem.set()


async def rem_notification_to_user(message: types.Message, state: FSMContext):
    try:
        index = int(message.text) - 1

        data = await state.get_data()
        id = data["users_add_notification"][index]
    except:
        await message.answer("Нет пользователя под таким номером\n"
                             "Выберите другого\n\n"
                             "Для отмены /cancel")
        return

    change_notification(id, 0)
    mes="Пользователь успешно убран с рассылки!\n\n"
    mes += "Управление рассылкой (/adm_notif)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n"

    await state.finish()
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def cmd_adm_day(message: types.Message, state: FSMContext):
    await state.finish()

    if check(message.from_user.id):
        await message.answer(check(message.from_user.id))
        return
    mes=""
    mes += "Управление рассылкой (/adm_notif)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n\n"
    mes+="За сколько дней до др уведомлять?:"

    await DayNot.waiting_for_count_day.set()
    await message.answer(mes, parse_mode=types.ParseMode.HTML)


async def set_day_for_notification(message: types.Message, state: FSMContext):
    try:
        index = int(message.text)
        if index<0:
            await message.answer("Введите число\n"
                                 "Выберите другого\n\n"
                                 "Для отмены /cancel")
            return
    except:
        await message.answer("Введите число\n"
                             "Выберите другого\n\n"
                             "Для отмены /cancel")
        return

    config=configparser.ConfigParser()
    config.read("config/bot.ini")
    config.set("notification", "before", str(index))
    with open("config/bot.ini", "w") as config_file:
        config.write(config_file)
    mes="Я запомнил;)\n\n"
    mes += "Управление рассылкой (/adm_notif)\n"
    mes += "Админ панель (/admin)\n"
    mes += "Меню (/cancel)\n\n"
    await message.answer(mes, parse_mode=types.ParseMode.HTML)
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cmd_admin, commands=["admin"], state="*")

    dp.register_message_handler(cmd_users, commands=["users"], state="*")
    dp.register_message_handler(cmd_list_users, commands=["list_users"], state="*")

    dp.register_message_handler(cmd_ban_user, commands=["ban"], state="*")
    dp.register_message_handler(ban_user, state=BlockUser.waiting_for_book_user_number)
    dp.register_message_handler(cmd_un_ban_user, commands=["un_ban"], state="*")
    dp.register_message_handler(un_ban_user, state=BlockUser.waiting_for_un_ban_user_number)

    dp.register_message_handler(cmd_adm_book, commands=["adm_book"], state="*")
    dp.register_message_handler(cmd_adm_birthday, commands=["adm_birthday"], state="*")
    dp.register_message_handler(user_number, state=StatusBook.waiting_for_user_number)
    dp.register_message_handler(book_st_number, state=StatusBook.waiting_for_book_user_number)
    dp.register_message_handler(change_status_book, state=StatusBook.waiting_for_status_number)

    dp.register_message_handler(cmd_adm_status, commands=["adm_status"], state="*")

    dp.register_message_handler(cmd_adm_per, commands=["adm_per"], state="*")
    dp.register_message_handler(cmd_adm_give, commands=["adm_give"], state="*")
    dp.register_message_handler(per_to_give, state=Permission.waiting_for_user_number_for_give)
    dp.register_message_handler(cmd_adm_take, commands=["adm_take"], state="*")
    dp.register_message_handler(per_take_up, state=Permission.waiting_for_user_number_for_take)

    dp.register_message_handler(cmd_adm_notif, commands=["adm_notif"], state="*")
    dp.register_message_handler(cmd_adm_rec, commands=["adm_rec"], state="*")
    dp.register_message_handler(cmd_adm_add_user_n, commands=["adm_add_user_n"], state="*")
    dp.register_message_handler(add_notification_to_user, state=Notification.waiting_for_user_number_for_add)
    dp.register_message_handler(cmd_adm_rem_user_n, commands=["adm_rem_user_n"], state="*")
    dp.register_message_handler(rem_notification_to_user, state=Notification.waiting_for_user_number_for_rem)

    dp.register_message_handler(cmd_adm_day, commands=["adm_day"], state="*")
    dp.register_message_handler(set_day_for_notification, state=DayNot.waiting_for_count_day)

