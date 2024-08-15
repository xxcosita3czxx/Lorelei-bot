#############################
#    By Cosita              #
#############################
#TODO Welcome system not working on channels
#TODO Giveaway logic
#TODO more verify modes
#TODO AntiLinks block all messages
#TODO Embeds and translations of strings
#TODO some more commands on helper

import asyncio
import logging
import os
import socket
import sys
import threading

import coloredlogs
import discord
import discord.ext
import discord.ext.commands

import config
from utils.configmanager import lang

############################### Logging ############################################

coloredlogs.install(
    level=config.loglevel,
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
conflang=config.language

logger = logging.getLogger(__name__)
logging.getLogger('discord.client').setLevel(logging.ERROR)

############################### Functions ##########################################

async def load_cogs(directory,bot):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                cog_path = os.path.relpath(os.path.join(root, file), directory)
                module_name = cog_path.replace(os.sep, '.').replace('.py', '')
                try:
                    await bot.load_extension(f'{directory}.{module_name}')
                    logger.info(lang.get(config.language,"Bot","cog_load").format(module_name=module_name))
                except Exception as e:
                    logger.error(lang.get(conflang,"Bot","cog_fail").format(module_name=module_name,error=e))


async def unload_cogs(bot):
    for extension in list(bot.extensions):
        try:
            await bot.unload_extension(extension)
            logger.info(lang.get(config.language, "Bot", "cog_unload").format(module_name=extension))  # noqa: E501
        except Exception as e:
            logger.error(lang.get(config.language, "Bot", "cog_fail_unload").format(module_name=extension, error=e))  # noqa: E501
#################################### Helper ########################################

def start_socket_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', int(config.helperport) ))  # Bind to port 9920
    server.listen(1)
    logger.info(f"Helper listener running on port {config.helperport}...")

    while True:
        client, _ = server.accept()
        with client:
            command = client.recv(1024).decode('utf-8').strip()
            if command:
                response = asyncio.run(handle_command(command))
                client.sendall(response.encode('utf-8'))

async def handle_command(command):

    if command.startswith('reload_all'):
        try:
            unload_cogs(bot=bot)
            bot.tree.sync()
            load_cogs(directory="commands", bot=bot)
            bot.tree.sync()
        except Exception as e:
            return f'Failed to reload. Error: {e}'

    elif command.startswith("kill"):
        logger.info("Killing from helper")
        sys.exit()

    else:
        return 'Unknown command.'
#################################### Status ########################################

async def change_status() -> None:
    while True:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="Some Chords...",
            ),
            status=config.status,
        )
        logging.debug(lang.get(conflang,"Bot","debug_status_chng"))
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"On {len(bot.guilds)} servers",
            ),
            status=config.status,
        )
        logging.debug(lang.get(conflang,"Bot","debug_status_chng"))
        await asyncio.sleep(5)
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/info",
            ),
            status=config.status,
        )
        logging.debug(lang.get(conflang,"Bot","debug_status_chng"))
        await asyncio.sleep(5)

#########################################################################################

class aclient(discord.ext.commands.AutoShardedBot):

    '''
    Main Client proccess

    This connects the bot to discord
    '''

    def __init__(self,shard_count) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix = ".",intents = intents)
        self.synced = False
        self.shard_count = shard_count

    async def on_ready(self) -> None:

        await self.wait_until_ready()

        if not self.synced:
            # Not sure if it should be also on start?
            await bot.tree.sync()
            await load_cogs(bot=self,directory="commands")
            await bot.tree.sync()
            logger.info(lang.get(config.language,"Bot","command_sync"))
            self.synced = True

        logger.info(lang.get(conflang,"Bot","info_logged").format(user=self.user))
        if config.helper:
            threading.Thread(target=start_socket_listener, daemon=True).start()
        await change_status()

bot = aclient(shard_count=config.shards)
tree = bot.tree

# just to be sure bcs context commands with this version of client also works
# so no .help
tree.remove_command("help")

########################## Main Runner #############################################

if __name__=="__main__":
    with open(".secret.key") as key:
        token = key.read()
    bot.run(token=token)
