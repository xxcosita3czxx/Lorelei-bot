#############################
#    By Cosita              #
#############################
#TODO Welcome system
#TODO Giveaway logic

import asyncio
import logging
import os

import coloredlogs
import discord
import discord.ext
import discord.ext.commands

import config
from utils.configmanager import lang

coloredlogs.install(
    level=config.loglevel,
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
conflang=config.language

logger = logging.getLogger(__name__)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)
logging.getLogger('discord.client').setLevel(logging.ERROR)
async def load_cogs(directory,bot):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                cog_path = os.path.relpath(os.path.join(root, file), directory)
                module_name = cog_path.replace(os.sep, '.').replace('.py', '')
                try:
                    await bot.load_extension(f'{directory}.{module_name}')
                    logger.info(f"Loaded {module_name}")
                except Exception as e:
                    logger.error(f'Failed to load {module_name}: {e}')

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
        super().__init__()
        self.synced = False
        self.added = False
        self.command_prefix = "."
        self.intents = intents
        self.shard_count = shard_count

    async def on_ready(self) -> None:

        await self.wait_until_ready()

        if not self.synced:
            # Not sure if it should be also on start?
            await bot.tree.sync()
            await load_cogs(bot=self,directory="commands")
            await bot.tree.sync()
            logger.info("Synced!")
            self.synced = True

        if not self.added:
            logger.info("Added views")
            self.added = True

        logger.info(lang.get(conflang,"Bot","info_logged").format(user=self.user))
        await change_status()

bot = aclient(3)
tree = bot.tree

# just to be sure bcs context commands with this version of client also works
# so no .help
tree.remove_command("help")

########################## Main Runner #############################################


if __name__=="__main__":
    with open(".secret.key") as key:
        token = key.read()
    bot.run(token=token)
