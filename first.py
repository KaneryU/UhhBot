import sqlite3
import asyncio
import os
import discord
import db_interface
import clientholder


def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    with open('schema.sqlite') as f:
        c.executescript(f.read())

    conn.commit()
    conn.close()
    


if __name__ == '__main__':
    if not os.path.exists('data.db'):
        init_db()
        
    asyncio.run(db_interface.init())

    clientholder.init_client()
    import bot
    clientholder.run()
    
