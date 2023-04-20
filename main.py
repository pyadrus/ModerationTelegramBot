import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hlink
import asyncio
import settings
from handlers.database import ban, unban

# Установка подключение с telegram
bot = Bot(token=settings.API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# Подключение к базе данных SQLite3
con = sqlite3.connect('data/db.db')
# Создание курсора для выполнения запросов
cursor = con.cursor()


# Команда /block
@dp.message_handler(commands=['block'])
async def block_cmd(message: types.Message, state: FSMContext):
    if message.from_user.id == settings.ADMIN_ID:
        await ban(chatid=message.chat.id, channelid=message.text.split('@')[1], cur=cursor, con=con)
        await message.answer(f'<b>Обязательная подписка на канал для чата включена!</b>')


# Команда /unblock
@dp.message_handler(commands=['unblock'])
async def unblock_cmd(message: types.Message, state: FSMContext):
    if message.from_user.id == settings.ADMIN_ID:
        await unban(chatid=message.chat.id, channelid=message.text.split('@')[1], cur=cursor, con=con)
        await message.answer(f'<b>Обязательная подписка на канал для чата выключена!</b>')


async def delete_message(message: types.Message, delay: int):
    await asyncio.sleep(delay)
    await message.delete()


# Хендлер, который работает по всем сообщениям - проверяем на подписку
@dp.message_handler()
async def check_to_block(message: types.Message, state: FSMContext):
    if message.from_user.id != settings.ADMIN_ID:
        cursor.execute('SELECT * FROM channel WHERE chat_id = ?', (message.chat.id,))
        info = cursor.fetchone()
        if info is not None:
            if info[3] == 1:
                try:
                    user_channel_status = await bot.get_chat_member(chat_id=f'@{info[1]}', user_id=message.from_user.id)
                    if user_channel_status["status"] == 'left':
                        link_to_channel = InlineKeyboardMarkup().add(
                            InlineKeyboardButton('Подписаться на канал', url=f't.me/{info[1]}'))
                        # Ссылка на админа группы, генерируется с помощью ID
                        admin_link = hlink('админу', f'tg://user?id={settings.ADMIN_ID}')
                        await message.delete()
                        deleted_message = await message.answer(f'<b>@{message.from_user.first_name}, приветствую '
                                                               f'вас.</b>\n'
                                                               f'<b>Чтобы писать в данном чате необходимо подписаться на канал.</b>'
                                                               f'\n<b>По вопросом рекламы в данной группе и многих других обращаться к {admin_link}</b>',
                                                               reply_markup=link_to_channel)
                        asyncio.create_task(delete_message(deleted_message, 60))  # удаляем сообщение через 1 минуту
                except Exception as e:
                    await message.answer(f'<b>Неверный ID канала/бот в нём не админ, проверьте!</b>'
                                         f'\n<b>ID канала: @{info[1]}</b>')


# Действия при запуске бота
async def on_startup(_):
    # Оповещаем модератора в личку о том что бот запущен
    await bot.send_message(535185511, f'<b>Бот для модерирования каналов успешно запущен!</b>')


# Бесконечная работы скрипта
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
