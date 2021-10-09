from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from app.database.db_work import get_books_by_user_all, get_books_by_user, add_book, remove_book_by_id, change_name, change_author_book, change_priority_book
from app.guard.check import check_access


class AddBook(StatesGroup):
    waiting_for_book_name = State()
    waiting_for_book_author = State()
    waiting_for_book_priority = State()


class RemoveBook(StatesGroup):
    waiting_for_book_number = State()


class ChangeBook(StatesGroup):
    waiting_for_book_ch_number = State()
    waiting_for_book_ch_action = State()
    waiting_for_book_ch_name = State()
    waiting_for_book_ch_author = State()
    waiting_for_book_ch_priority = State()


async def cmd_book(message: types.Message, state: FSMContext):
    await state.finish()

    if not check_access(message.from_user.id):
        await message.answer('У вас нет доступа')
        return

    books = get_books_by_user_all(message.from_user.id)
    if not books or books is None:
        menu = "У вас нет сохраненных книг.\n\n"
    else:
        menu = "Ваши книги:\n\n"
        for index, book in enumerate(books):
            menu += f"    Название📖:  <i>{book[1]}</i>\n"
            menu += f"    Автор✍🏻:  <i>{book[2]}</i>\n"
            menu += f"    Приоритет❤:  <i>{book[4]}</i>\n"
            if book[3] == "active":
                menu += f"    Статус🔄:  <i>активна</i>\n\n"
            else:
                menu += f"    Статус🔄:  <i>подарена</i>\n\n"

    menu += "1. Добавить книгу (/add_b)\n" \
            "2. Изменить название, автора или приоритет книги (/ch_b)\n" \
            "3. Удалить книгу (/del_b)\n\n"\
            "Меню: /cancel\n"

    await message.answer(
        menu,
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode=types.ParseMode.HTML
    )


async def start_add_book(message: types.Message):
    if not check_access(message.from_user.id):
        await message.answer('У вас нет доступа.')
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("/cancel")

    await message.answer("Название книги:", reply_markup=keyboard)
    await AddBook.waiting_for_book_name.set()


async def book_name(message: types.Message, state: FSMContext):
    if len(message.text) < 3:
        await message.answer("Название книги слишком короткое, используете больше знаков:")
        return
    await state.update_data(book_name=message.text)

    await AddBook.next()
    await message.answer("Автор этой книги:")


async def book_author(message: types.Message, state: FSMContext):
    if len(message.text) < 3:
        await message.answer("Используете больше знаков:")
        return
    await state.update_data(book_author=message.text)

    await AddBook.next()
    await message.answer("Приорите этой книги от 1 до 10, где:\n\n"
                         "1 - хочу получить эту книгу следущей.\n"
                         "10 - дарить в последнию очередь.")


async def book_priority(message: types.Message, state: FSMContext):
    try:
        priority = int(message.text)
        if priority < 0 or priority > 11:
            await message.answer("Это должно быть число от 1 до 10:")
            return
    except:
        await message.answer("Это должно быть число от 1 до 10:")
        return

    data = await state.get_data()

    add_book(message.from_user.id, data["book_name"], data["book_author"], priority)

    await message.answer("Книга успешно добавлена!\n\n"
                         "Книги: /book\n"
                         "Меню: /cancel")
    await state.finish()


async def cmd_remove_book(message: types.Message, state: FSMContext):
    await state.finish()

    if not check_access(message.from_user.id):
        await message.answer('У вас нет доступа.')
        return

    books = get_books_by_user(message.from_user.id)
    if not books or books is None:
        menu = "У вас нет сохраненных книг.\n\n" \
               "Добавить книгу: /add_b\n"
        await message.answer(menu)
        return
    else:
        book_numbers = []
        menu = "Ваши книги:\n\n"
        for index, book in enumerate(books):
            menu += f"{index+1}.  Название📖:  <i>{book[1]}</i>\n"
            menu += f"    Автор✍🏻:  <i>{book[2]}</i>\n"
            menu += f"    Приоритет❤:  <i>{book[4]}</i>\n\n"
            book_numbers.append(book[0])
    menu += "Выберите номер книги для удаления:"

    await state.update_data(book_numbers=book_numbers)
    await message.answer(menu, parse_mode=types.ParseMode.HTML)
    await RemoveBook.waiting_for_book_number.set()


async def book_number_for_remove(message: types.Message, state: FSMContext):
    try:
        index = int(message.text) - 1

        data = await state.get_data()
        id = data["book_numbers"][index]
    except:
        await message.answer("Нет книги под таким номером\n\n"
                             "Выберите другую.\n"
                             "Для отмены /cancel ")
        return

    remove_book_by_id(id)

    await message.answer("Книга удалена!\n\n"
                         "Книги: /book\n"
                         "Меню: /cancel")

    await state.finish()


async def cmd_change_book(message: types.Message, state: FSMContext):
    await state.finish()

    if not check_access(message.from_user.id):
        await message.answer('У вас нет доступа.')
        return

    books = get_books_by_user(message.from_user.id)
    if not books or books is None:
        menu = "У вас нет сохраненных книг.\n\n" \
               "Добавить книгу: /add_b\n"
        await message.answer(menu)
        return
    else:
        book_numbers = []
        menu = "Ваши книги:\n\n"
        for index, book in enumerate(books):
            menu += f"{index+1}.  Название📖:  <i>{book[1]}</i>\n"
            menu += f"    Автор✍🏻:  <i>{book[2]}</i>\n"
            menu += f"    Приоритет❤:  <i>{book[4]}</i>\n"
            book_numbers.append(book[0])
    menu += "Выберите номер книги для изменения:"

    await state.update_data(book_numbers_ch=book_numbers)
    await message.answer(menu, parse_mode=types.ParseMode.HTML)
    await ChangeBook.waiting_for_book_ch_number.set()


async def book_number_for_change(message: types.Message, state: FSMContext):
    try:
        index = int(message.text) - 1

        data = await state.get_data()
        id = data["book_numbers_ch"][index]
    except:
        await message.answer("Нет книги под таким номером.\n\n"
                             "Выберите другую.\n"
                             "Для отмены /cancel ")
        return

    await state.update_data(id_book=id)

    await message.answer("Выберите цифру действия:\n\n"
                         "1. Изменить название\n"
                         "2. Изменить автора\n"
                         "3. Изменить приоритет\n\n"
                         "Меню: /cancel\n"
                         "Книги: /book")

    await ChangeBook.next()


async def book_change_action(message: types.Message, state: FSMContext):
    try:
        index = int(message.text)
        if not index in [1, 2, 3]:
            await message.answer("Нет такого действия.\n\n"
                                 "Для отмены /cancel ")
            return
    except:
        await message.answer("Нет такого действия.\n\n"
                             "Для отмены /cancel ")
        return
    ans="--"
    if index==1:
        ans="Введите название книги:"
        await ChangeBook.waiting_for_book_ch_name.set()
    elif index==2:
        ans="Введите автора книги:"
        await ChangeBook.waiting_for_book_ch_author.set()
    if index==3:
        ans="Введите приоритет книги:"
        await ChangeBook.waiting_for_book_ch_priority.set()
    await message.answer(ans)


async def book_change_name(message: types.Message, state: FSMContext):
    if len(message.text) < 3:
        await message.answer("Название книги слишком короткое, используете больше знаков:")
        return
    data = await state.get_data()
    id = data["id_book"]
    change_name(id, message.text)
    await state.finish()
    await message.answer("Название книги успешно изменено!\n\n"
                         "Книги: /book ")


async def book_change_author(message: types.Message, state: FSMContext):
    if len(message.text) < 3:
        await message.answer("Имя автора слишком короткое, используете больше знаков:")
        return
    data = await state.get_data()
    id = data["id_book"]
    change_author_book(id, message.text)
    await state.finish()
    await message.answer("Автор книги успешно изменен!\n\n"
                         "Книги: /book ")


async def book_change_priority(message: types.Message, state: FSMContext):
    try:
        priority = int(message.text)
        if priority < 0 or priority > 11:
            await message.answer("Это должно быть число от 1 до 10:")
            return
    except:
        await message.answer("Это должно быть число от 1 до 10:")
        return

    data = await state.get_data()
    id = data["id_book"]
    change_priority_book(id, priority)
    await state.finish()
    await message.answer("Приоритет книги успешно изменен!\n\n"
                         "Книги: /book ")


def register_handlers_book(dp: Dispatcher):
    dp.register_message_handler(cmd_book, commands=["book"], state="*")

    dp.register_message_handler(start_add_book, commands=["add_b"], state="*")
    dp.register_message_handler(book_name, state=AddBook.waiting_for_book_name)
    dp.register_message_handler(book_author, state=AddBook.waiting_for_book_author)
    dp.register_message_handler(book_priority, state=AddBook.waiting_for_book_priority)

    dp.register_message_handler(cmd_remove_book, commands=["del_b"], state="*")
    dp.register_message_handler(book_number_for_remove, state=RemoveBook.waiting_for_book_number)

    dp.register_message_handler(cmd_change_book, commands=["ch_b"], state="*")
    dp.register_message_handler(book_number_for_change, state=ChangeBook.waiting_for_book_ch_number)
    dp.register_message_handler(book_change_action, state=ChangeBook.waiting_for_book_ch_action)
    dp.register_message_handler(book_change_name, state=ChangeBook.waiting_for_book_ch_name)
    dp.register_message_handler(book_change_author, state=ChangeBook.waiting_for_book_ch_author)
    dp.register_message_handler(book_change_priority, state=ChangeBook.waiting_for_book_ch_priority)
