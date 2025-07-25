#############################
#    By Cosita              #
#############################
#TODO more verify modes
#TODO Level system more theme files
#TODO Level system logic for leaderboards and levels
#TODO Giveaway logic
#TODO Announcement system, that could also dm users, should ask them first
#TODO Add logging system, preferably to a channel, im not sure about logging to the bot itself, could be alot in size.  # noqa: E501
#TODO Timezone converter
#TODO Logs look doubled (CHECK IF ITS NOT A BUG)
#IDEA ids could be if num not in list then add, else continue
# Also edit could add/edit already existing
#IDEA Job to clean left guilds after a day or 12 hours,
# So it wont cry about guild not existing

import asyncio
import importlib
import logging
import os
import sys
import time

import discord
import discord.ext
import discord.ext.commands

import config
import utils.profiler as profiler
from utils.configmanager import lang

############################### Logging ############################################

conflang=config.language

# Set the logging level for specific loggers if needed
logging.getLogger('automessages')  .setLevel(config.loglevel)
logging.getLogger('welcome')       .setLevel(config.loglevel)
logging.getLogger('anti-invites')  .setLevel(config.loglevel)
logging.getLogger('nsfw.e621')     .setLevel(config.loglevel)
logging.getLogger('ban')           .setLevel(config.loglevel)
logging.getLogger('invite-logger') .setLevel(config.loglevel)
logging.getLogger('configmanager') .setLevel(config.loglevel)

logger = logging.getLogger("main")
# Set the logging format for the root logger
logging.basicConfig(
    level=config.loglevel,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


############################### Functions ##########################################

async def load_cogs(directory, bot):  # noqa: C901
    cogs = []
    # Walk through the directory and collect cogs with priority
    for root, _, files in os.walk(directory):
        logger.debug(files)
        for file in files:
            if file.endswith('.py') and file != '__init__.py' and not file.endswith(".pyc"):  # noqa: E501
                logger.debug(file)
                # Construct the module path relative to the project root
                cog_path = os.path.relpath(os.path.join(root, file), start=os.getcwd())  # noqa: E501
                module_name = cog_path.replace(os.sep, '.').replace('.py', '')

                try:
                    # Dynamically import the module to get __PRIORITY__
                    logger.debug(f"Constructed module path: {module_name}")
                    module = importlib.import_module(module_name)
                    priority = getattr(module, "__PRIORITY__", 0)

                    # Clamp priority between 0 and 10
                    if not (0 <= priority <= 10):  # noqa: PLR2004
                        logger.warning(
                            f"Cog '{module_name}' has invalid priority {priority}. Defaults to 0.",  # noqa: E501
                        )
                        priority = 0

                    cogs.append((priority, module_name))
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
    # Ensure all imported cogs inherit this logging configuration
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).setLevel(config.loglevel)
    # Apply the same format to all loggers
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).handlers.clear()
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s %(levelname)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        ))
        logging.getLogger(logger_name).addHandler(handler)
    logging.getLogger('discord.client') .setLevel(logging.ERROR)
    logging.getLogger('discord.gateway').setLevel(logging.INFO )
    logging.getLogger('discord.http')   .setLevel(logging.INFO )

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
    logger.info(lang.get(config.language,"Bot","helper_running").format(helperport=config.helperport))
    async with server:
        await server.serve_forever()

async def handle_client(reader, writer, bot):
    try:
        data = await reader.read(1024)
        command = data.decode('utf-8').strip()
        response = await handle_command(command, bot,writer)
        writer.write(response.encode('utf-8')) # type: ignore
        await writer.drain()
    except Exception as e:
        logger.error(lang.get(config.language,"Bot","err_client_handle").format(error=e))
    finally:
        writer.close()
        await writer.wait_closed()

async def handle_command(command,bot:discord.ext.commands.bot.AutoShardedBot,writer):  # noqa: C901, E501
    if command.startswith('help'):
        return (
            'Available commands: '
            'extensions reload_all | '
            'extensions reload <cog> | '
            'extensions unload <cog> | '
            'extensions load <cog> | '
            'extensions list | '
            'reload_util <module> | '
            'profiler [start|stop|stats] | '
            'info [guilds|lat|uptime] | '
            'kill | '
            'update | '
            'reload_lang | '
            'lang-reload | '
            'bugreports [index]'
        )

    if command.startswith('extensions'):
        parts = command.split(" ", 1)
        if len(parts) < 2:  # noqa: PLR2004
            return "Invalid extensions command. Use 'extensions reload_all', 'extensions unload <cog>', or 'extensions load <cog>'."  # noqa: E501
        _, command = parts
        if command.startswith('reload_all'):
            try:
                # --- RELOAD ALL UTILS FIRST ---
                def list_utils_modules():
                    modules = []
                    utils_dir = "utils"
                    for filename in os.listdir(utils_dir):
                        if filename.endswith(".py") and filename != "__init__.py":
                            modules.append(f"{utils_dir}.{filename[:-3]}")
                    return modules

                utils_modules = list_utils_modules()
                for mod in utils_modules:
                    if mod in sys.modules:
                        importlib.reload(sys.modules[mod])

                # --- THEN RELOAD ALL COGS ---
                await unload_cogs(bot=bot)
                await bot.tree.sync()
                await load_cogs(directory="commands", bot=bot)
                await bot.tree.sync()
                return lang.config(config.language,"Bot","reload_success") # type: ignore
            except Exception as e:
                return f'Failed to reload. Error: {e}'

        elif command.startswith("unload"):
            try:
                cog = command.split(maxsplit=1)[1]
                if cog is None or cog == "":
                    return "Specify cog."
                if cog not in list(bot.extensions):
                    return "Invalid cog. Ensure cog name"
                try:
                    await bot.unload_extension(cog)
                    await bot.tree.sync()
                    return f"Unloaded {cog} successfully."
                except discord.ext.commands.ExtensionNotLoaded:
                    return "Extension is not loaded"

                except Exception as e:
                    return f"Unknown error while unloading extension: {e}"

            except Exception as e:
                return f"failed to unload: {e}"

        elif command.startswith("load"):
            try:
                _, cog = command.split(maxsplit=1)
                if cog is None or cog == "":
                    return "Specify cog."
                try:
                    await bot.load_extension(cog)
                    await bot.tree.sync()
                    return f"Loaded {cog} successfully."
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
        elif command.startswith("reload"):
            try:
                cog = command.split(maxsplit=1)[1]
                if cog is None or cog == "":
                    return "Specify cog."
                if cog not in list(bot.extensions):
                    return "Invalid cog. Ensure cog name"
                try:
                    await bot.reload_extension(cog)
                    await bot.tree.sync()
                    return f"Reloaded {cog} successfully."
                except discord.ext.commands.ExtensionNotLoaded:
                    return "Extension is not loaded"
                except discord.ext.commands.ExtensionNotFound:
                    return "Extension not found, ensure name is correct"
                except discord.ext.commands.ExtensionFailed as e:
                    return f"Failed to reload: {e}"
                except Exception as e:
                    return f"Unknown error while reloading extension: {e}"
            except Exception as e:
                return f"Failed to reload: {e}"
        elif command.startswith("list"):
            return "\n".join(list(bot.extensions))
        else:
            return "Unknown extensions command."  # noqa: E501
    elif command.startswith("reload_util"):
        try:
            parts = command.split(" ", 1)
            if len(parts) < 2:  # noqa: PLR2004
                return "Usage: reload_util <module_name> (e.g. utils.guildconfig)"
            mod = parts[1].strip()
            if mod in sys.modules:
                importlib.reload(sys.modules[mod])
                return f"Reloaded util module: {mod}"
            else:
                return f"Module {mod} not loaded."
        except Exception as e:
            return f"Failed to reload util: {e}"
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
                return str(len(bot.guilds))
            elif action == "lat":
                return str(bot.latency)
            elif action == "uptime":
                rntime = time.time()
                return str(time.time() - (lambda start=rntime: start)())
            else:
                return "Unknown info action."
    elif command.startswith("kill"):
        logger.info("Killing from helper")
        writer.write(b"Killing bot.")
        await bot.close()
        sys.exit(0)
    elif command.startswith("reload_lang"):
        try:
            lang._load_all_configs()
            return "Language files reloaded successfully."
        except Exception as e:
            return f"Failed to reload language files: {e}"

    elif command.startswith("update"):
        try:
            os.system("git pull")  # noqa: S605
            return "Updated succesfully"
        except Exception as e:
            return f'Failed to update. Error: {e}'

    elif command.startswith("lang-reload"):
        lang._load_all_configs()
        return "Reloaded language files."
    elif command.startswith("bugreports"):
        parts = command.split(" ", 1)
        if os.path.exists("data/bug-reports") and os.listdir("data/bug-reports"):
            bug_reports = os.listdir("data/bug-reports")
            if len(parts) > 1:
                index = int(parts[1])
                if 0 <= index < len(bug_reports):
                    with open(os.path.join("data/bug-reports", bug_reports[index])) as file:  # noqa: E501
                        return "\n" + file.read()
                else:
                    return "Invalid index. Please provide a valid bug report index."
            else:
                return "All reports:\n"+"\n".join([f"{i}: {report}" for i, report in enumerate(bug_reports)])  # noqa: E501
        else:
            return "Bug reports directory is empty."
    else:
        return 'Unknown command.'
#################################### Status ########################################
# language: python
async def change_status() -> None:
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name="Some Chords...",
                ),
                status=config.status,
            )
            logger.debug(lang.get(conflang, "Bot", "debug_status_chng"))

            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"On {len(bot.guilds)} servers",
                ),
                status=config.status,
            )
            logger.debug(lang.get(conflang, "Bot", "debug_status_chng"))
            await asyncio.sleep(5)

            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name="/help",
                ),
                status=config.status,
            )
            logger.debug(lang.get(conflang, "Bot", "debug_status_chng"))
            await asyncio.sleep(5)

            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name=f"Version: v{os.popen('git rev-list --count HEAD').read().strip()}",  # noqa: E501, S605
                ),
                status=config.status,
            )
            logger.debug(lang.get(conflang, "Bot", "debug_status_chng"))
            await asyncio.sleep(5)

            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name=f"Commit: {os.popen('git rev-parse HEAD').read().strip()[:7]}",  # noqa: E501, S605
                ),
                status=config.status,
            )
            logger.debug(lang.get(conflang, "Bot", "debug_status_chng"))
            await asyncio.sleep(5)

        except Exception as e:
            logger.warning(f"[STATUS LOOP] Caught exception: {e}")
            await asyncio.sleep(10)  # pause before retrying

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
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name="Loading bot...",
                ),
                status=discord.Status.idle,
            )
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
