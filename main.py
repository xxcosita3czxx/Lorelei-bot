#############################
#    By Cosita              #
#############################
#TODO Giveaway logic
#TODO more verify modes
#TODO AntiLinks block all messages (Test please)
#TODO Embeds and translations of strings
#TODO Level system more theme files
#TODO Level system logic for leaderboards and levels
#TODO Auto messages (prop cron style/discord builtin calendar)
#TODO Smart Warn system (Move to commands/admin/warn.py)
#TODO Better config system (Embed style preferences + being able to add to it from the cog)  # noqa: E501
#TODO Invite tracking

import asyncio
import importlib
import logging
import os
import sys
import time

import coloredlogs
import discord
import discord.ext
import discord.ext.commands

import config
import utils.profiler as profiler
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

async def load_cogs(directory, bot):
    cogs = []
    # Walk through the directory and collect cogs with priority
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                cog_path = os.path.relpath(os.path.join(root, file), directory)
                module_name = cog_path.replace(os.sep, '.').replace('.py', '')
                full_module_path = f'{directory}.{module_name}'

                try:
                    # Dynamically import the module to get __PRIORITY__
                    module = importlib.import_module(full_module_path)
                    priority = getattr(module, "__PRIORITY__", 0)

                    # Clamp priority between 0 and 10
                    if not (0 <= priority <= 10):  # noqa: PLR2004
                        logger.warning(
                            f"Cog '{module_name}' has invalid priority {priority}. Defaults to 0.",  # noqa: E501
                        )
                        priority = 0

                    cogs.append((priority, full_module_path))
                except Exception as e:
                    logger.error(lang.get(conflang, "Bot", "cog_fail").format(module_name=module_name, error=e))  # noqa: E501

    # Sort cogs by descending priority (highest first)
    for _, module_name in sorted(cogs, key=lambda x: x[0], reverse=True):
        try:
            if config.disabler_mode == "wl" and module_name not in config.enabled:
                logger.debug(lang.get(config.language, "Bot", "cog_skipped").format(module_name=module_name))  # noqa: E501
                continue
            if config.disabler_mode == "bl" and module_name in config.disabled:
                logger.debug(lang.get(config.language, "Bot", "cog_disabled").format(module_name=module_name))  # noqa: E501
                continue
            else:
                await bot.load_extension(module_name)
                logger.info(lang.get(config.language, "Bot", "cog_load").format(module_name=module_name))  # noqa: E501
        except Exception as e:
            logger.error(lang.get(conflang, "Bot", "cog_fail").format(module_name=module_name, error=e))  # noqa: E501

async def unload_cogs(bot):
    for extension in list(bot.extensions):
        try:
            await bot.unload_extension(extension)
            logger.info(lang.get(config.language, "Bot", "cog_unload").format(module_name=extension))  # noqa: E501
        except Exception as e:
            logger.error(lang.get(config.language, "Bot", "cog_fail_unload").format(module_name=extension, error=e))  # noqa: E501

#################################### Helper ########################################

async def socket_listener(bot):
    server = await asyncio.start_server(
        lambda reader, writer: handle_client(reader, writer, bot),
        'localhost',
        config.helperport,
    )
    logger.info(f"Helper listener running on port {config.helperport}...")
    async with server:
        await server.serve_forever()

async def handle_client(reader, writer, bot):
    try:
        data = await reader.read(1024)
        command = data.decode('utf-8').strip()
        response = await handle_command(command, bot)
        writer.write(response.encode('utf-8'))
        await writer.drain()
    except Exception as e:
        logger.error(f"Error in client handling: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def handle_command(command,bot:discord.ext.commands.bot.AutoShardedBot):  # noqa: C901

    if command.startswith('reload_all'):
        try:
            await unload_cogs(bot=bot)
            await bot.tree.sync()
            await load_cogs(directory="commands", bot=bot)
            await bot.tree.sync()
            return "Reloaded succesfully"
        except Exception as e:
            return f'Failed to reload. Error: {e}'

    elif command.startswith("unload"):
        try:
            cog = command.split(maxsplit=1)
            if cog is None or cog == "":
                return "Specify cog."
            if cog not in list(bot.extensions):
                return "Invalid cog. Ensure cog name"

            try:
                await bot.unload_extension(cog)

            except discord.ext.commands.ExtensionNotLoaded:
                return "Extension is not loaded"

            except Exception as e:
                return f"Unknown error while unloading extension: {e}"

        except Exception as e:
            return f"failed to unload: {e}"

    elif command.startswith("load"):
        try:
            _, cog = command.strip(" ")
            if cog is None or cog == "":
                return "Specify cog."

            try:
                await bot.load_extension(cog)

            except discord.ext.commands.ExtensionNotFound:
                return "Extension not found, ensure name is correct"

            except discord.ext.commands.ExtensionAlreadyLoaded:
                return "Extension already loaded!"

            except discord.ext.commands.ExtensionFailed as e:
                return f"Failed to load: {e}"

            except Exception as e:
                return f"Unknown error while loading extension: {e}"

        except Exception as e:
            return f"Failed to load: {e}"

    elif command.startswith("profiler"):
        # Handle profiler commands
        parts = command.split(" ", 1)
        if len(parts) > 1:
            action = parts[1]
            if action == "start":
                return profiler.start_profiling()
            elif action == "stop":
                return profiler.stop_profiling()
            elif action == "stats":
                return profiler.get_stats()
            else:
                return "Unknown profiler action."

    elif command.startswith("info"):
        # Handle profiler commands
        parts = command.split(" ", 1)
        if len(parts) > 1:
            action = parts[1]
            if action == "guilds":
                return len(bot.guilds)
            elif action == "lat":
                return bot.latency
            elif action == "uptime":
                rntime = time.time()
                return time.time() - (lambda start=rntime: start)()
            else:
                return "Unknown info action."
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

        asyncio.create_task(change_status())
        await self.post_ready()

    async def post_ready(self):

        if config.helper:
            logger.info("Starting helper socket listener...")
            asyncio.create_task(socket_listener(self))
            logger.info("Helper socket listener started.")

#        if config.api:
#            logger.info("Starting FastAPI server...")
#            fastapi_server = FastAPIServer(bot=bot, port=config.apiport)
#            asyncio.create_task(fastapi_server.start())
#            logger.info("FastAPI server started.")

bot = aclient(shard_count=config.shards)
tree = bot.tree

# just to be sure bcs context commands with this version of client also works
# so no .help
tree.remove_command("help")

########################## Main Runner #############################################

if __name__=="__main__":
    with open(".secret.key") as key:
        token = key.read()

    # This will run the bot, yes im too stoobid to rember
    try:
        bot.run(token=token)
    except discord.errors.PrivilegedIntentsRequired:
        logger.error("All privileged intents are required to run the bot.")
