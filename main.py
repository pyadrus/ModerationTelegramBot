import asyncio
import logging
import sqlite3
import sys

from aiogram import types
from aiogram.filters import Command
from aiogram.utils.markdown import hlink
from loguru import logger

from handlers.database import ban, unban
from keyboards.keyboards import link_to_channel
from settings.settings import time_delete_messages
from system.dispatcher import dp, bot, router


@router.message(Command(commands=["block"]))
async def block_cmd(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вызвал команду '/block' в чате {chat_id}")

    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    logger.info(chat_member)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(chat_id, "Команда доступна только для администраторов.", parse_mode="html")
        await message.delete()  # Удаляем сообщение с командой /block
        return
    try:
        ban(chatid=message.chat.id, channelid=message.text.split("@")[1])
        await message.answer("<b>Обязательная подписка на канал для чата включена!</b>", parse_mode="html")
    except IndexError:
        await message.answer("<b>Не указан ID канала. Используйте /block @channel</b>", parse_mode="html")

@router.message(Command(commands=["unblock"]))
async def unblock_cmd(message: types.Message):
    """_summary_

    Args:
        message (types.Message): _description_
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вызвал команду '/unblock' в чате {chat_id}")
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    logger.info(chat_member)
    if chat_member.status not in ["administrator", "creator"]:
    # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(chat_id, "Команда доступна только для администраторов.", parse_mode="html")
        await message.delete()  # Удаляем сообщение с командой /unblock
        return
    try:
        unban(chatid=message.chat.id, channelid=message.text.split("@")[1], )
        await message.answer(f"<b>Обязательная подписка на канал для чата выключена!</b>", parse_mode="html")
    except IndexError:
        await message.answer("<b>Не указан ID канала. Используйте /unblock @channel</b>", parse_mode="html")

async def delete_message(message: types.Message, delay: int):
    """_summary_

    Args:
        message (types.Message): _description_
        delay (int): _description_
    """
    await asyncio.sleep(delay)
    await message.delete()


@router.message()
async def check_to_block(message: types.Message):
    """_summary_

    Args:
        message (types.Message): _description_
    """
    # Получаем список админов чата
    chat_admins = await bot.get_chat_administrators(chat_id=message.chat.id)
    # Получаем ID админа
    admin_id = next(
        (
            admin.user.id
            for admin in chat_admins
            if admin.status == "creator" or admin.status == "administrator"
        ),
        None,
    )

    # Если отправитель сообщения не является админом чата или канал не подписан, просим подписаться
    if message.from_user.id != admin_id:
        # Подключение к базе данных SQLite3
        con = sqlite3.connect("data/db.db")
        # Создание курсора для выполнения запросов
        cursor = con.cursor()

        # Создание таблицы 'channel', если её не существует
        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS channel (
                        chat_id INTEGER PRIMARY KEY,
                        channel_id INTEGER,
                        block INTEGER DEFAULT 0
                    )
                ''')
            print("Таблица 'channel' проверена/создана успешно.")
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")

        cursor.execute("SELECT * FROM channel WHERE chat_id = ?", (message.chat.id,))
        info = cursor.fetchone()
        if info is not None:
            channel_id = info[1]  # ID канала
            block = info[2]  # Значение поля block

            # Проверяем, включен ли блок (должно быть block == 1)
            if block == 1:
                user_channel_status = await bot.get_chat_member(chat_id=f"@{channel_id}", user_id=message.from_user.id)
                if user_channel_status.status == "left":
                    # Код для вывода сообщения пользователю, который не подписан на канал
                    admin_link = hlink("админу", f"tg://user?id={457407212}")
                    await message.delete()
                    deleted_message = await message.answer(
                        f"<b>@{message.from_user.first_name}, приветствую "
                        f"вас.</b>\n"
                        f"<b>Чтобы писать в данном чате необходимо подписаться на канал.</b>"
                        f"\n<b>По вопросом рекламы в данной группе и многих других обращаться к {admin_link}</b>",
                        reply_markup=link_to_channel(info[1]),
                    parse_mode="html")
                    # удаляем сообщение через 1 минуту
                    asyncio.create_task(delete_message(deleted_message, time_delete_messages))


async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
