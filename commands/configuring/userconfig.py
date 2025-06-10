import logging  # noqa: F401
import os  # <-- Add this import

import discord
from discord import app_commands
from discord.ext import commands

from commands.configuring.guildconfig import CategoryView
from utils.configmanager import uconfig  # noqa: F401
from utils.dices import dices  # Import the array from utils.dices
from utils.guildconfig import GuildConfig

logger = logging.getLogger("userconfig")

class UserConfigCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
        name="userconfig",
        description="Configure the bot",  # noqa: E501
    )
    async def configure(self,interaction:discord.Interaction):
        config_session = GuildConfig()  # noqa: F841
        config_session.set_config_set("user")
        embed = discord.Embed(
            title="Configuration Categories",
            description="Select a category to configure",
        )
        logger.debug(config_session.Configs)
        for category in config_session.Configs:
            embed.add_field(name=category, value=f"Configure {category}", inline=False)  # noqa: E501
        categories = config_session.get_categories()  # Assuming Configs is a dictionary  # noqa: E501
        await interaction.response.send_message(
            embed=embed,
            view=CategoryView(categories, config_session,config_manager=uconfig),
            ephemeral=True,
        )  # noqa: E501

async def setup(bot:commands.Bot):
    cog = UserConfigCommands(bot)
    await bot.add_cog(cog)
    # Get language options from data/langs directory
    langs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "lang")  # noqa: E501
    language_options = []
    if os.path.isdir(langs_dir):
        for fname in os.listdir(langs_dir):
            if fname.endswith(".toml"):
                language_options.append(os.path.splitext(fname)[0])

    configman = GuildConfig()
    configman.set_config_set("user")
    configman.add_setting("Appearance", "System Color", "Configure color for bot responses")  # noqa: E501
    configman.add_setting("Appearance", "Punishments Color", "Color for Bans, Warns or any punishments that will come to your dms")  # noqa: E501
    configman.add_setting("Appearance", "Override Server Color", "Please let me have my color instead of server's color (reccoment leaving this off)")  # noqa: E501
    configman.add_setting("System", "Show system messages", "Configure whether to show system messages in the chat, or only to you (server settings has priority)")  # noqa: E501
    configman.add_setting("Appearance", "Language", "Configure your appearance settings")  # noqa: E501
    configman.add_option_list(
        "Appearance",
        "Language",
        "language",
        language_options,  # Use detected language options
        "Appearance",
        "language",
        "Choose your language for the bot responses",
    )
    configman.add_setting("Fun", "Default Dice Mode", "Configure your default dice mode")  # noqa: E501
    configman.add_option_list(
        "Fun",
        "Default Dice Mode",
        "dice",
        list(dices.keys()),  # Use the imported array for dice modes
        "FUN",
        "def_dice",
        "Choose your default dice mode",
    )
