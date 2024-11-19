import asyncio
import logging
import sqlite3
import sys

from aiogram import types
from aiogram.filters import Command
from aiogram.utils.markdown import hlink
from loguru import logger

from handlers import ban, unban
from keyboards import link_to_channel
from settings.settings import time_delete_messages
from system.dispatcher import dp, bot, router


@router.message(Command(commands=["block"]))
async def block_cmd(message: types.Message):
    # Получаем ID текущего чата и пользователя, который вызвал команду
    chat_id = message.chat.id
    user_id = message.from_user.id
    # Логируем информацию о пользователе, который вызвал команду
    logger.info(f"Пользователь {user_id} вызвал команду '/block' в чате {chat_id}")

    # Проверяем, является ли пользователь администратором или создателем чата
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    logger.info(chat_member)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не администратор, отправляем сообщение с предупреждением
        await bot.send_message(chat_id, "Команда доступна только для администраторов.", parse_mode="html")
        # Удаляем сообщение пользователя с командой /block
        await message.delete()
        return  # Завершаем выполнение команды, если пользователь не администратор

    try:
        # Пытаемся получить ID канала из команды пользователя
        # message.text.split("@")[1] предполагает, что канал указывается в формате "@channel"
        ban(chatid=message.chat.id, channelid=message.text.split("@")[1])
        # Если операция прошла успешно, отправляем сообщение о включении обязательной подписки
        await message.answer("<b>Обязательная подписка на канал для чата включена!</b>", parse_mode="html")
    except IndexError:
        # Если возникла ошибка из-за отсутствия указанного ID канала, отправляем сообщение с подсказкой
        await message.answer("<b>Не указан ID канала. Используйте /block @channel</b>", parse_mode="html")


@router.message(Command(commands=["unblock"]))
async def unblock_cmd(message: types.Message):
    """
    Обработчик команды '/unblock'. Деактивирует обязательную подписку на канал для текущего чата.

    Args:
        message (types.Message): Объект сообщения, содержащий команду и дополнительные данные.
    """
    # Получаем ID текущего чата и пользователя, который вызвал команду
    chat_id = message.chat.id
    user_id = message.from_user.id
    # Логируем информацию о пользователе, который вызвал команду
    logger.info(f"Пользователь {user_id} вызвал команду '/unblock' в чате {chat_id}")

    # Проверяем, является ли пользователь администратором или создателем чата
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    logger.info(chat_member)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не администратор, отправляем сообщение с предупреждением
        await bot.send_message(chat_id, "Команда доступна только для администраторов.", parse_mode="html")
        # Удаляем сообщение пользователя с командой /unblock
        await message.delete()
        return  # Завершаем выполнение команды, если пользователь не администратор

    try:
        # Пытаемся получить ID канала из команды пользователя
        # message.text.split("@")[1] предполагает, что канал указывается в формате "@channel"
        unban(chatid=message.chat.id, channelid=message.text.split("@")[1])
        # Если операция прошла успешно, отправляем сообщение о выключении обязательной подписки
        await message.answer(f"<b>Обязательная подписка на канал для чата выключена!</b>", parse_mode="html")
    except IndexError:
        # Если возникла ошибка из-за отсутствия указанного ID канала, отправляем сообщение с подсказкой
        await message.answer("<b>Не указан ID канала. Используйте /unblock @channel</b>", parse_mode="html")


async def delete_message(message: types.Message, delay: int):
    """
    Асинхронная функция для удаления сообщения через определённое количество времени.

    Args:
        message (types.Message): Объект сообщения, которое необходимо удалить.
        delay (int): Время задержки в секундах перед удалением сообщения.
    """
    # Ждём указанное количество времени перед удалением сообщения
    await asyncio.sleep(delay)
    # Удаляем сообщение после задержки
    await message.delete()


@router.message()
async def check_to_block(message: types.Message):
    """
    Обработчик сообщения, проверяющий подписку пользователя на указанный канал.
    Если пользователь не подписан, сообщение будет удалено, и отправлено уведомление с просьбой подписаться.

    Args:
        message (types.Message): Объект сообщения, которое нужно обработать.
    """
    # Получаем список администраторов текущего чата
    chat_admins = await bot.get_chat_administrators(chat_id=message.chat.id)
    # Получаем ID создателя или админа чата
    admin_id = next(
        (
            admin.user.id
            for admin in chat_admins
            if admin.status == "creator" or admin.status == "administrator"
        ),
        None,  # Если нет админов, возвращает None
    )

    # Проверяем, что отправитель сообщения не является администратором чата
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

        # Проверяем, есть ли запись о текущем чате в базе данных
        cursor.execute("SELECT * FROM channel WHERE chat_id = ?", (message.chat.id,))
        info = cursor.fetchone()

        if info is not None:
            channel_id = info[1]  # ID канала
            block = info[2]  # Значение поля block (1 — блок включен, 0 — блок выключен)

            # Проверяем, включен ли блок (если block == 1)
            if block == 1:
                # Проверяем статус пользователя в канале
                user_channel_status = await bot.get_chat_member(chat_id=f"@{channel_id}", user_id=message.from_user.id)
                if user_channel_status.status == "left":
                    # Если пользователь не подписан, удаляем его сообщение и отправляем уведомление
                    admin_link = hlink("админу", f"tg://user?id={457407212}")  # Ссылка на администратора
                    await message.delete()  # Удаляем сообщение пользователя
                    deleted_message = await message.answer(
                        f"<b>@{message.from_user.first_name}, приветствую вас.</b>\n"
                        f"<b>Чтобы писать в данном чате необходимо подписаться на канал.</b>"
                        f"\n<b>По вопросам рекламы в данной группе и многих других обращаться к {admin_link}</b>",
                        reply_markup=link_to_channel(info[1]),  # Кнопка для перехода к каналу
                        parse_mode="html"
                    )
                    # Удаляем уведомление через 1 минуту
                    asyncio.create_task(delete_message(deleted_message, time_delete_messages))


async def main() -> None:
    """
    Основная асинхронная функция для запуска бота.
    Настраивает логирование и запускает поллинг для получения сообщений.

    """
    # Настраиваем базовое логирование
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    try:
        # Запускаем поллинг, чтобы бот начал прослушивать новые сообщения
        await dp.start_polling(bot)
    except Exception as e:
        # Логируем любую ошибку, которая возникла во время выполнения поллинга
        logger.error(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
