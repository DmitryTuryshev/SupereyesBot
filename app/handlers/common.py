from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from app.guard.check import check_access, check, check_reg


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()

    if not check_access(message.from_user.id):
        await message.answer('У вас нет доступа')
        return
    if not check_reg(message.from_user.id):
        await message.answer('Вы не зарегистрированы.\n\n'
                             'Зарегистрироваться (/reg)',  reply_markup=types.ReplyKeyboardRemove())
        return

    menu = "Задайте вопрос боту:\n\n" \
           "1. Книги (/book)\n" \
           "2. Ближайший ДР (/birthday)\n"
    if not check(message.from_user.id):
        menu += "3. Управление (/admin)\n"
    await message.answer(
        menu,
        reply_markup=types.ReplyKeyboardRemove()
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start", "cancel"], state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
