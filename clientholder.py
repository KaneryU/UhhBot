import discord
import json

running = False
client: discord.Client = None # type: ignore
intent: discord.Intents = None # type: ignore

def init_client():
    global running, client, intents
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    print('Bot is starting up...')
    
    
    
def run():
    global running, client
    with open('token.json') as f:
        token = json.loads(f.read())['token']
    
    running = True
    client.run(token)