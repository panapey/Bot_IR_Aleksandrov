import logging

import pyodbc
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

logging.basicConfig(level=logging.INFO)

bot = Bot(token='TOKEN')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

server = 'SERVER'
database = 'DATABASE'
cnxn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';Trusted_Connection=yes;')
cursor = cnxn.cursor()


class Form(StatesGroup):
    category = State()
    auth = State()


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message, state: FSMContext):
    await state.set_state(Form.category)
    await message.answer("Выберите категорию: 1 - Клиент, 2 - Менеджер, 3 - Программист")


@dp.message_handler(state=Form.category)
async def handle_category(message: types.Message, state: FSMContext):
    text = message.text
    if text == '1':
        # обработка выбора категории "Клиент"
        await message.answer('Вы выбрали категорию "Клиент"')
        await state.finish()
    elif text == '2':
        # обработка выбора категории "Менеджер"
        await message.answer('Вы выбрали категорию "Менеджер"')
        await state.update_data(category='manager')
        await Form.next()
        await message.answer('Введите логин и пароль')
    elif text == '3':
        # обработка выбора категории "Программист"
        await message.answer('Вы выбрали категорию "Программист"')
        await state.update_data(category='programmer')
        await Form.next()
        await message.answer('Введите логин и пароль')
    else:
        await message.answer('Неправильный выбор категории')

@dp.message_handler(state=Form.auth)
async def handle_auth(message: types.Message, state: FSMContext):
    text = message.text.split()
    if len(text) < 2:
        await message.answer('Пожалуйста, отправьте логин и пароль в формате: логин пароль')
    else:
        cursor.execute("SELECT * FROM Users WHERE login=? AND password=?", (text[0], text[1]))
        row = cursor.fetchone()
        if row is None:
            await message.answer('Неправильный логин или пароль')
        else:
            role = row[3]
            data = await state.get_data()
            category = data.get('category')
            if role != category:
                await message.answer(f'Вы не можете авторизоваться как {category}')
            else:
                await message.answer(f'Успешная авторизация как {category}!')
            await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp)
