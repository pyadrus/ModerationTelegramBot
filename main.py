import asyncio
import sqlite3
from system.dispatcher import bot
from aiogram import F
from aiogram.utils.markdown import hlink
from system.dispatcher import dp
from handlers.database import ban, unban
from keyboards.keyboards import link_to_channel
from settings.settings import time_delete_messages
from aiogram import types
from system.dispatcher import router
import logging
import asyncio
import logging
import sys

from loguru import logger

# Подключение к базе данных SQLite3
con = sqlite3.connect("data/db.db")
# Создание курсора для выполнения запросов
cursor = con.cursor()


@dp.message(F.text == "/block")
async def block_cmd(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    print(f"Пользователь {user_id} вызвал команду '/block' в чате {chat_id}")
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print(chat_member)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(chat_id, "Команда доступна только для администраторов.")
        await message.delete()  # Удаляем сообщение с командой /block
        return
    await ban(
        chatid=message.chat.id,
        channelid=message.text.split("@")[1],
        cur=cursor,
        con=con,
    )
    await message.answer(f"<b>Обязательная подписка на канал для чата включена!</b>")


@dp.message(F.text == "/unblock")
async def unblock_cmd(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    print(f"Пользователь {user_id} вызвал команду '/unblock' в чате {chat_id}")
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print(chat_member)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(chat_id, "Команда доступна только для администраторов.")
        await message.delete()  # Удаляем сообщение с командой /unblock
        return
    await unban(
        chatid=message.chat.id,
        channelid=message.text.split("@")[1],
        cur=cursor,
        con=con,
    )
    await message.answer(f"<b>Обязательная подписка на канал для чата выключена!</b>")


async def delete_message(message: types.Message, delay: int):
    await asyncio.sleep(delay)
    await message.delete()


@router.message()
async def check_to_block(message: types.Message):
    try:
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
            cursor.execute(
                "SELECT * FROM channel WHERE chat_id = ?", (message.chat.id,)
            )
            info = cursor.fetchone()
            if info is not None:
                if info[3] == 1:
                    try:
                        user_channel_status = await bot.get_chat_member(
                            chat_id=f"@{info[1]}", user_id=message.from_user.id
                        )
                        if user_channel_status["status"] == "left":

                            admin_link = hlink("админу", f"tg://user?id={457407212}")
                            await message.delete()
                            deleted_message = await message.answer(
                                f"<b>@{message.from_user.first_name}, приветствую "
                                f"вас.</b>\n"
                                f"<b>Чтобы писать в данном чате необходимо подписаться на канал.</b>"
                                f"\n<b>По вопросом рекламы в данной группе и многих других обращаться к {admin_link}</b>",
                                reply_markup=link_to_channel(info),
                            )
                            # удаляем сообщение через 1 минуту
                            asyncio.create_task(
                                delete_message(deleted_message, time_delete_messages)
                            )
                    except Exception as e:
                        await message.answer(
                            f"<b>Неверный ID канала/бот в нём не админ, проверьте!</b>"
                            f"\n<b>ID канала: @{info[1]}</b>"
                        )
    except Exception as e:
        logger.error(f"Ошибка: {e}")


def register_handlers():
    """Регистрация обработчиков для бота"""
    dp.message.register(block_cmd)
    dp.message.register(unblock_cmd)
    dp.message.register(delete_message)
    dp.message.register(check_to_block)


async def main() -> None:
    try:
        await dp.start_polling(bot)
        register_handlers()  # Оплата гарантийного талона на 2 - 3 года
    except Exception as e:
        logger.error(f"Ошибка: {e}")


if __name__ == "__main__":  # Бесконечная работы скрипта
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
