import aiosqlite as sqlite3
import asyncio
import warnings
import clientholder
import discord
import time

conn: sqlite3.Connection = None # type: ignore
c: sqlite3.Cursor = None # type: ignore

def conncheckwrapper(func):
    def wrapper(*args, **kwargs):
        if conn is None:
            raise RuntimeError('Database connection not initialized')
        
        return func(*args, **kwargs)
    return wrapper

async def init():
    global conn, c
    conn = sqlite3.connect('data.db')
    await conn.__aenter__() 
    if conn is None:
        raise RuntimeError('Failed to connect to database')

async def get_author_username(UID: int) -> str:
    if not isinstance(UID, int):
        raise TypeError('UID must be an integer')
    
    # use discord.py to get the username
    user: discord.User = await clientholder.client.fetch_user(UID)
    return user.global_name or "Unknown"

async def get_author_display_name(UID: int) -> str:
    if not isinstance(UID, int):
        raise TypeError('UID must be an integer')
    
    # use discord.py to get the display name
    user: discord.User = await clientholder.client.fetch_user(UID)
    return user.display_name



@conncheckwrapper
async def log_new_author(UID: int, username: str, display_name: str):
    if not isinstance(UID, int):
        raise TypeError('UID must be an integer')
    if not isinstance(username, str):
        raise TypeError('username must be a string')
    if not isinstance(display_name, str):
        raise TypeError('display_name must be a string')
    
    await conn.execute('INSERT INTO authors (UID, username, display_name) VALUES (?, ?, ?)', (UID, username, display_name))
    await conn.commit()

@conncheckwrapper
async def log_new_message(MID: int, content: str, author_UID: int, is_reply: bool, author_level: int, reply_to: int = -1):
    if not isinstance(content, str):
        raise TypeError('content must be a string')
    if not isinstance(author_UID, int):
        raise TypeError('author_UID must be an integer')
    if not isinstance(is_reply, bool):
        raise TypeError('is_reply must be a boolean')
    if not isinstance(author_level, int):
        raise TypeError('author_level must be an integer')
    if not isinstance(reply_to, int):
        raise TypeError('reply_to must be an integer')
    if not isinstance(MID, int):
        raise TypeError('MID must be an integer')
    
    
    
    check_author_exists = await conn.execute('SELECT * FROM authors WHERE UID = ?', (author_UID,))
    check_author_exists = await check_author_exists.fetchall()
    if len(check_author_exists) == 0:
        username = await get_author_username(author_UID)
        display_name = await get_author_display_name(author_UID)
        await log_new_author(author_UID, username, display_name)
        await conn.commit()
    
    if is_reply:
        if not isinstance(reply_to, int):
            raise TypeError('reply_to must be an integer')
        if reply_to == -1:
            raise ValueError('reply_to must be an integer')
        
        await conn.execute('INSERT INTO messages (MID, content, UID, is_reply, author_level, reply_to, time_sent) VALUES (?, ?, ?, ?, ?, ?, ?)', (MID, content, author_UID, 1, author_level, reply_to, time.time()))
    else:
        await conn.execute('INSERT INTO messages (MID, content, UID, is_reply, author_level, time_sent) VALUES (?, ?, ?, ?, ?, ?)', (MID, content, author_UID,  0, author_level, time.time()))
    await conn.commit()

@conncheckwrapper
async def get_total_messages():
    result = await conn.execute('SELECT COUNT(*) FROM messages')
    result = await result.fetchone()
    return result[0]

@conncheckwrapper
async def get_total_authors():
    result = await conn.execute('SELECT COUNT(*) FROM authors')
    result = await result.fetchone()
    return result[0]

@conncheckwrapper
async def get_total_messages_from_author(UID: int):
    result = await conn.execute('SELECT COUNT(*) FROM messages WHERE UID = ?', (UID,))
    result = await result.fetchone()
    return result[0]
