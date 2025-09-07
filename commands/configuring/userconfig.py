import logging  # noqa: F401

import discord
from discord import app_commands
from discord.ext import commands

from commands.configuring.guildconfig import CategoryView
from utils.configmanager import lang, uconfig  # noqa: F401
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
        config_session = GuildConfig()
        config_session.set_config_set("user")
        embed = discord.Embed(
            title="Configuration Categories",
            description="Select a category to configure",
        )
        logger.debug(config_session.Configs)
        filtered_settings_by_category = {}
        filtered_categories = []
        is_nsfw = hasattr(interaction.channel, "is_nsfw") and interaction.channel.is_nsfw()  # noqa: E501
        for category, settings_dict in config_session.Configs.items():
            filtered_settings = [
                s for s, data in settings_dict.items()
                if not data.get("nsfw", False) or is_nsfw
            ]
            if filtered_settings:
                embed.add_field(name=category, value=f"Configure {category}", inline=False)  # noqa: E501
                filtered_categories.append(category)
                filtered_settings_by_category[category] = filtered_settings
        if not filtered_categories:
            embed.description = "No categories available."
        await interaction.response.send_message(
            embed=embed,
            view=CategoryView(filtered_categories, filtered_settings_by_category, config_session, config_manager=uconfig),  # noqa: E501
            ephemeral=True,
        )

async def setup(bot:commands.Bot):
    cog = UserConfigCommands(bot)
    await bot.add_cog(cog)
    # Get language options from data/langs directory
    # Use configmanager's lang instance to get language options
    language_options = []
    for code, lang_data in lang.config.items():
        name = lang_data.get("LANGUAGE", {}).get("name", code)
        language_options.append(name)

    configman = GuildConfig()
    configman-set_config_set("user")
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
