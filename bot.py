import discord
import json
import time
from clientholder import client, intent
import db_interface

prefix = '~~'


class Function_Timer:
    def __init__(self):
        self.lastTimes = []
        self.timesCalled = 0
    
    def time(self, func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter_ns()
            result = func(*args, **kwargs)
            end = time.perf_counter_ns()
            self.lastTimes.append(end - start)
            self.timesCalled += 1
            if self.timesCalled > 10:
                self.lastTimes.pop(0)
            
            if self.timesCalled % 10 == 0:
                print(f'Average time: {self.ns_to_ms(self.get_average())}ms')

            return result
        
        return wrapper
    
    def get_average(self):
        return sum(self.lastTimes) / len(self.lastTimes)
    
    def ns_to_ms(self, ns: int):
        return ns / 1_000_000
    
timer = Function_Timer()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@timer.time
@client.event
async def on_message(message: discord.Message):
    global prefix
    if message.author.id == 380882157868154880: # my user ID
        if message.content == prefix + 'ping':
            await message.channel.send('pong')
        elif message.content == prefix + 'shutdown':
            await client.close()
            return
        elif message.content == prefix + 'test':
            await message.channel.send('Test successful')
        elif message.content == prefix + "change prefix":
            await message.channel.send("What would you like the new prefix to be?")
            new_prefix = await client.wait_for('message')
            if new_prefix.author.id == message.author.id:
                prefix = new_prefix.content
                await message.channel.send(f"Prefix changed to {prefix}")
            else:
                await message.channel.send("You are not the person who initiated the command. Please try again in a private channel.")
        elif message.content == prefix + 'total:sent':
            await message.channel.send(f"Total messages sent: {await db_interface.get_total_messages()}")
        elif message.content == prefix + 'total:authors':
            await message.channel.send(f"Total authors: {await db_interface.get_total_authors()}")
        elif message.content == prefix + 'total:sentFromAuthor':
            await message.channel.send("Please provide the UID of the author you would like to get the total messages sent from.")
            author_id = await client.wait_for('message')
            await message.channel.send(f"Total messages sent by author {author_id}: {await db_interface.get_total_messages_from_author(author_id)}")
            
            
        
        
        
        
    if isinstance(message.author, discord.User):
        if message.reference is None:
            await db_interface.log_new_message(message.id, message.content, message.author.id, False, 0)
        else:
            await db_interface.log_new_message(message.id, message.content, message.author.id, True, 0, message.reference.message_id)
    else:
        if message.reference is None:
            await db_interface.log_new_message(message.id, message.content, message.author.id, False, get_author_level(message.author))
        else:
            await db_interface.log_new_message(message.id, message.content, message.author.id, True, get_author_level(message.author), message.reference.message_id)
    
def get_author_level(Member: discord.Member) -> int:
    roles = Member.roles
    roles_containing_level = [role for role in roles if role.name.startswith('Level ')]
    if len(roles_containing_level) == 0:
        return 0
    else:
        # remove all non-numeric characters from the role name
        return int(''.join([char for char in roles_containing_level[0].name if char.isnumeric()]))


