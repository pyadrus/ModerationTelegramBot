import sqlite3

def ban(chatid, channelid):
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

    cursor.execute('SELECT * FROM channel WHERE chat_id = ?', (chatid,))
    data_chat = cursor.fetchone()
    if data_chat is None:
        cursor.execute('INSERT INTO channel (chat_id, channel_id) VALUES(?, ?)', (chatid, channelid))
        con.commit()
    else:
        cursor.execute('UPDATE channel set block = 1, channel_id = ? WHERE chat_id = ?', (channelid, chatid))
        con.commit()


def unban(chatid, channelid):
    con = sqlite3.connect("data/db.db")
    cursor = con.cursor()

    cursor.execute('SELECT * FROM channel WHERE chat_id = ?', (chatid,))
    data_chat = cursor.fetchone()
    if data_chat is not None:
        cursor.execute('UPDATE channel set block = 0 WHERE chat_id = ?', (chatid,))
        con.commit()
    else:
        cursor.execute('INSERT INTO channel (chat_id, channel_id, block) VALUES(?, ?, ?)', (chatid, channelid, '0'))
        con.commit()
