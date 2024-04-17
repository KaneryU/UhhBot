import discord
import json
import random
import time
import enum
import clientholder
import db_interface

prefix = '~~'

class AuthLevel(enum.Enum):
    USER = 0
    MOD = 1
    ADMIN = 2
    OWNER = 3
class Command:
    def __init__(self, name, auth: AuthLevel = AuthLevel.USER):
        global cmdlst, cmdnamelist
        cmdlst.append(self)
        cmdnamelist.append(name)
        self.name = name
        self.auth = auth
    
    def help(self):
        return 'No help available for this command'

    def func(self, message: discord.Message, args):
        pass
    
    async def __call__(self, message: discord.Message, auth: AuthLevel, args):
        if not auth.value >= self.auth.value:
            await message.channel.send(f'You are not authorized to use this command ({auth.value} >= {self.auth.value})')
            return
        await self.func(message, args)

cmdlst: list[Command] = []
cmdnamelist: list[str] = []
class Ping(Command):
    def __init__(self):
        super().__init__('ping')
    
    def help(self):
        return 'Pings the bot'
    
    async def func(self, message: discord.Message, args):
        await message.channel.send('pong')

class Shutdown(Command):
    def __init__(self):
        super().__init__('shutdown', AuthLevel.OWNER)
    
    def help(self):
        return 'Shuts down the bot'
    
    async def func(self, message: discord.Message, args):
        await message.channel.send('You killed me...')
        await clientholder.client.close()

class Test(Command):
    def __init__(self):
        super().__init__('test', AuthLevel.OWNER)

    def help(self):
        return 'Tests the bot'
    
    async def func(self, message: discord.Message, args):
        await message.channel.send('Test successful')

class ChangePrefix(Command):
    def __init__(self):
        super().__init__('change prefix', AuthLevel.ADMIN)
    
    def help(self):
        return 'Changes the prefix of the bot'
    
    async def func(self, message: discord.Message, args):
        new_prefix = args
        if ":" in new_prefix:
            await message.channel.send("Prefix cannot contain the character ':'")
            return
        prefix = new_prefix
        await message.channel.send(f"Prefix changed to {prefix}")

class TotalUp(Command):
    def __init__(self):
        super().__init__('totalup', AuthLevel.USER)
    
    def help(self):
        return 'Args: sent, authors; Gets total amount of messages or authors'
    
    async def func(self, message: discord.Message, args):
        if args == "sent":
            await message.channel.send(f"Total messages sent: {await db_interface.get_total_messages()}")
        elif args == "authors":
            await message.channel.send(f"Total authors: {await db_interface.get_total_authors()}")
    
        
class Query(Command):
    def __init__(self):
        super().__init__('query', AuthLevel.OWNER)
    
    def help(self):
        return 'Runs a query on the database'
    
    async def func(self, message: discord.Message, args):
        query = args
        result = await db_interface.run_query(query)
        lines = []
        for i in result:
            lines.append(str(i) + '\n')
            
        message_ = "```\n" + ''.join(lines) + "```"
        await message.channel.send(message_)
    
class Uptime(Command):
    def __init__(self):
        super().__init__('uptime')
    
    def help(self):
        return 'Gets the uptime of the bot'
    
    async def func(self, message: discord.Message, args):
        await message.channel.send(f'Uptime {time.strftime("%H:%M:%S", time.gmtime(time.time() - clientholder.start_time))}')
    
class Help(Command):
    def __init__(self):
        super().__init__('help')
    
    def help(self):
        return 'Shows help for all commands'
    
    async def func(self, message: discord.Message, args):
        global cmdlst
        self.commandHelp = {cmd.name: cmd.help() for cmd in cmdlst}
        self.commandNames = cmdnamelist
        if args == '':
            await message.channel.send('Commands: ' + ', '.join(self.commandNames))
            await message.channel.send('Use ~~help:[command] to get help on a specific command')
        else:
            if args in self.commandHelp:
                await message.channel.send(self.commandHelp[args])
            else:
                await message.channel.send('Command not found, or no help available for that command.')
        
class AuthorMessageCount(Command):
    def __init__(self):
        super().__init__('author message count')
    
    def help(self):
        return 'Gets the message count for each author'
    
    async def func(self, message: discord.Message, args):
        result = await db_interface.author_message_count()
        
        message_ = "```\n" + ''.join(result) + "```"
        await message.channel.send(message_)

class GetAuthLevel(Command):
    def __init__(self):
        super().__init__('authlevel')
    
    def help(self):
        return 'Gets the authorization level of the user'
    
    async def func(self, message: discord.Message, args):
        if args == '':
            await message.channel.send(f'Your authorization level is {get_auth_level(message.author).name}')
        else:
            member = message.guild.get_member_named(args)
            if member is None:
                await message.channel.send(f'Member {args} not found')
                return
            await message.channel.send(f'The authorization level of {args} is {get_auth_level(member).name}')

class CommandAuthLevel(Command):
    def __init__(self):
        super().__init__('command authlevel')
    
    def help(self):
        return 'Gets the authorization level of a command'
    
    async def func(self, message: discord.Message, args):
        command = commands.get_command(args)
        if command is None:
            await message.channel.send(f'Command {args} not found')
            return
        await message.channel.send(f'The authorization level of command {args} is {command.auth.name}')
class Commands:
    def __init__(self):
        pass
    
    def get_command(self, command: str) -> Command:
        return cmdlst[cmdnamelist.index(command)]
    


    async def call_command(self, message: discord.Message, command: str, args, auth: AuthLevel):
        command_: Command = self.get_command(command)
        print(f'Command {command_.name} called by {message.author.name} with args {args} and auth level {auth}')
        try:
            await command_(message, auth, args)
        except TypeError:
            await command_(message, auth, args)


registercmd = [Ping(), Shutdown(), Test(), ChangePrefix(), TotalUp(), Query(), Uptime(), Help(), AuthorMessageCount(), GetAuthLevel(), CommandAuthLevel()]
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
    if message.content == "%#REGISTEREDCMDS":
        await message.channel.send(f'Commands: {", ".join(cmdnamelist)}')
    elif message.content.startswith(prefix):
        if ":" in message.content:
            command = message.content.replace(prefix, '').split(":")[0].strip().lower()
            args = message.content.split(":")[1].strip()
        else:
            command = message.content.split(prefix)[1].strip().lower()
            args = None
        
        if command in cmdnamelist:
            await commands.call_command(message, command, args, get_auth_level(message.author))
        else:
            await message.channel.send(f'Command {command} not found')
            

        
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


def get_auth_level(Member: discord.Member) -> AuthLevel:
    roles = Member.roles
    OWNER_UID = 380882157868154880
    ADMIN_ROLE = "admin"
    MOD_ROLE = "mod"
    
    if OWNER_UID == Member.id:
        return AuthLevel.OWNER
    
    if MOD_ROLE in [role.name for role in roles]:
        return AuthLevel.MOD
    
    if ADMIN_ROLE in [role.name for role in roles]:
        return AuthLevel.ADMIN

    return AuthLevel.USER
    