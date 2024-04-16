import discord
import json
import time

running = False
client: discord.Client = None # type: ignore
intent: discord.Intents = None # type: ignore
start_time = None
def init_client():
    global running, client, intents
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    print('Bot is starting up...')
    
    
    
def run():
    global running, client, start_time
    with open('token.json') as f:
        token = json.loads(f.read())['token']
    
    running = True
    start_time = time.time()
    client.run(token)
    