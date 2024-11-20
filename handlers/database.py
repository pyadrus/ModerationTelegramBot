import sqlite3
from loguru import logger

def ban(chatid, channelid):
    """
    Функция для блокировки обязательной подписки на канал в указанном чате.
    Если записи для чата нет, она создается с блокировкой.
    Если запись для чата существует, она обновляется, устанавливая блокировку в 1.

    Args:
        chatid (int): ID чата, где выполняется блокировка.
        channelid (int): ID канала, на который нужно подписаться.
    """
    try:
        # Подключение к базе данных SQLite3
        con = sqlite3.connect("data/db.db")
        # Создание курсора для выполнения запросов
        cursor = con.cursor()

        # Создание таблицы 'channel', если её не существует
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel (
                chat_id INTEGER PRIMARY KEY,  
                channel_id INTEGER,  
                block INTEGER DEFAULT 0
            )
        ''')

        # Проверка, существует ли запись для данного чата в таблице 'channel'
        cursor.execute('SELECT * FROM channel WHERE chat_id = ?', (chatid,))
        data_chat = cursor.fetchone()

        if data_chat is None:
            # Если записи для данного чата нет, создаём новую запись с блокировкой
            cursor.execute('INSERT INTO channel (chat_id, channel_id) VALUES(?, ?)', (chatid, channelid))
            con.commit()
        else:
            # Если запись существует, обновляем её, устанавливая блокировку (block = 1)
            cursor.execute('UPDATE channel SET block = 1, channel_id = ? WHERE chat_id = ?', (channelid, chatid))
            con.commit()

        # Закрытие соединения с базой данных
        con.close()
    except Exception as e:
        logger.exception(e)


def unban(chatid, channelid):
    """
    Функция для разблокировки обязательной подписки на канал в указанном чате.
    Если запись для чата уже существует, она обновляется, устанавливая блокировку в 0.
    Если записи для чата нет, создаётся новая запись с указанием чата и канала.

    Args:
        chatid (int): ID чата, где выполняется разблокировка.
        channelid (int): ID канала, связанного с этим чатом.
    """
    try:
        # Подключение к базе данных SQLite3
        con = sqlite3.connect("data/db.db")
        # Создание курсора для выполнения запросов
        cursor = con.cursor()

        # Проверяем, существует ли запись для данного чата в таблице 'channel'
        cursor.execute('SELECT * FROM channel WHERE chat_id = ?', (chatid,))
        data_chat = cursor.fetchone()

        if data_chat is not None:
            # Если запись уже существует, обновляем её, устанавливая block = 0 (разблокировка)
            cursor.execute('UPDATE channel set block = 0 WHERE chat_id = ?', (chatid,))
            con.commit()
        else:
            # Если записи для данного чата нет, создаём новую запись
            cursor.execute('INSERT INTO channel (chat_id, channel_id, block) VALUES(?, ?, ?)', (chatid, channelid, '0'))
            con.commit()

        # Закрываем соединение с базой данных
        con.close()

    except Exception as e:
        logger.exception(e)