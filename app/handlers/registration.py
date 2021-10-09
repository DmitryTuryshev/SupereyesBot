from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import datetime
from app.database.db_work import add_user,get_user
from app.guard.check import check_access

class RegUser(StatesGroup):
    waiting_for_user_name = State()
    waiting_for_user_birthday = State()


async def reg_start(message: types.Message, state: FSMContext):
    await state.finish()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("/cancel")

    user=get_user(message.from_user.id)

    if user is not None:
        if not check_access(message.from_user.id):
            await message.answer("У вас нет доступа", reply_markup=keyboard)
        else:
            await message.answer("Вы уже зарегистрировались /cancel", reply_markup=keyboard)
        return

    await message.answer("Введите ФИО:", reply_markup=keyboard)
    await RegUser.waiting_for_user_name.set()


async def reg_name(message: types.Message, state: FSMContext):
    if len(message.text) < 4:
        await message.answer("ФИО слишком короткое, используете больше знаков:")
        return
    await state.update_data(user_name=message.text)

    await RegUser.next()
    await message.answer("Введите дату рождения в формате:\n"
                         "дд.мм.гггг")


async def reg_birthday(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        "/cancel"
    ]
    keyboard.add(*buttons)
    try:
        t=datetime.datetime.strptime(message.text.lower(), '%d.%m.%Y')

        dates=t.date()
        date = t.strftime('%d.%m.%Y')
    except:
        await message.answer("Некорректо введена дата.\n"
                             "Введите дату рождения в формате:\n"
                             "    дд.мм.гггг",reply_markup=keyboard)
        return


    data=await state.get_data()
    add_user(message.from_user.id, data['user_name'], dates)
    await message.answer(f"Вы успешно зарегистрировались!\n\n"
                         f"Ваше ФИО:  {data['user_name']}\n"
                         f"Ваша дата рождения:  {date}\n\n"
                         f"Меню: /cancel",
                         reply_markup=keyboard)
    await state.finish()


def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(reg_start, commands=["reg"], state="*")
    dp.register_message_handler(reg_name, state=RegUser.waiting_for_user_name)
    dp.register_message_handler(reg_birthday, state=RegUser.waiting_for_user_birthday)
