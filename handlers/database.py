import asyncio

async def ban(chatid, channelid, cur, con):
    cur.execute('SELECT * FROM channel WHERE chat_id = ?', (chatid,))
    data_chat = cur.fetchone()
    if data_chat is None:
        cur.execute('INSERT INTO channel (chat_id, channel_id) VALUES(?, ?)', (chatid, channelid))
        con.commit()
    else:
        cur.execute('UPDATE channel set block = 1, channel_id = ? WHERE chat_id = ?', (channelid, chatid))
        con.commit()

async def unban(chatid, channelid, cur, con):
    cur.execute('SELECT * FROM channel WHERE chat_id = ?', (chatid,))
    data_chat = cur.fetchone()
    if data_chat is not None:
        cur.execute('UPDATE channel set block = 0 WHERE chat_id = ?', (chatid, ))
        con.commit()
    else:
        cur.execute('INSERT INTO channel (chat_id, channel_id, block) VALUES(?, ?, ?)', (chatid, channelid, '0'))
        con.commit()
