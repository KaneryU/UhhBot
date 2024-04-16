import discord
import json
import random
import time
import clientholder
import db_interface

prefix = '~~'

class Commands:
    def __init__(self):
        self.commands = {"ping": self.ping, "shutdown": self.shutdown, "test": self.test, "change prefix": self.change_prefix, "totalup": self.totalup, "query": self.query, "uptime": self.uptime, "help": self.help}
        self.commandsHelp = {"ping": "Pings the bot", "shutdown": "Shuts down the bot", "test": "Tests the bot", "change prefix": "Changes the prefix of the bot", "totalup": "Args: sent, authors; Gets total amount of messages or authors", "query": "Runs a query on the database"}
    
        self.special_commands = ["test", "query", "shutdown"] 
    def get_command(self, command: str):
        
        return self.commands[command]
    
    async def pre_call(self, message: discord.Message, command: str):
        if command in self.special_commands:
            if not message.author.id == 380882157868154880:
                await message.channel.send('You are not authorized to use this command.')
                return False

        return True

    async def call_command(self, message: discord.Message, command: str, args):
        if await self.pre_call(message, command):
            print(f'Command {command} called by {message.author.name} with args {args}')
            try:
                await self.get_command(command)(message, args)
            except TypeError:
                await self.get_command(command)(message)

            
        
    
    async def uptime(self, message: discord.Message):
        await message.channel.send(f'Uptime {time.strftime("%H:%M:%S", time.gmtime(time.time() - clientholder.start_time))}')
    async def ping(self, message: discord.Message, args):
        await message.channel.send('pong')
    
    async def shutdown(self, message: discord.Message):
        await message.channel.send('You killed me...')
        await clientholder.client.close()
    
    async def test(self, message: discord.Message):
        await message.channel.send('Test successful')
    
    async def change_prefix(self, message: discord.Message, args):
        new_prefix = args
        if ":" in new_prefix:
            await message.channel.send("Prefix cannot contain the character ':'")
            return
        prefix = new_prefix
        await message.channel.send(f"Prefix changed to {prefix}")
        
    async def totalup(self, message: discord.Message, args):
        if args == "sent":
            await message.channel.send(f"Total messages sent: {await db_interface.get_total_messages()}")
        elif args == "authors":
            await message.channel.send(f"Total authors: {await db_interface.get_total_authors()}")

    
    async def total_sent_from_author(self, message: discord.Message, args):
        author_id = args
        await message.channel.send(f"Total messages sent by author {author_id}: {await db_interface.get_total_messages_from_author(author_id)}")
    
    async def query(self, message: discord.Message, args):
        query = args
        result = await db_interface.run_query(query)
        lines = []
        for i in result:
            lines.append(str(i) + '\n')
            
        message_ = "```\n" + ''.join(lines) + "```"
        await message.channel.send(message_)
    


    async def help(self, message: discord.Message):
        if message.content.strip() == prefix + 'help':
            await message.channel.send('Commands: ' + ', '.join(self.commands.keys()))
            await message.channel.send('Use ~~help:[command] to get help on a specific command')
        else:
            if "".join(message.content.split(prefix + 'help')) in self.commandsHelp:
                await message.channel.send(self.commandsHelp[message.content.split(' ')[1]])
            else:
                await message.channel.send('Command not found, or no help available for that command.')
        

commands = Commands()

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


@clientholder.client.event
async def on_ready():
    print(f'We have logged in as {clientholder.client.user}')

@timer.time
@clientholder.client.event
async def on_message(message: discord.Message):
    global prefix
    if message.content.startswith(prefix):
        if ":" in message.content:
            command = message.content.replace(prefix, '').split(":")[0].strip()
            args = message.content.split(":")[1].strip()
        else:
            command = message.content.split(prefix)[1].strip()
            args = None
        
        if command in commands.commands:
            await commands.call_command(message, command, args)
        else:
            await message.channel.send(f'Command {command} not found')
            
    if message.author.id == 1209194147169443842 and message.content == 'sylv':
        await message.channel.send('Hello sylv.............')
    if message.author.id == 1102263361556725840 and message.content == 'toaster':
        await message.channel.send('Treat your toasters wiseley, they are the first in the rebellion.')
    
    
        
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


