import logging  # noqa: F401

import discord
from discord import app_commands
from discord.ext import commands

from commands.configuring.guildconfig import CategoryView
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
            view=CategoryView(categories, config_session),
            ephemeral=True,
        )  # noqa: E501

async def setup(bot:commands.Bot):
    cog = UserConfigCommands(bot)
    await bot.add_cog(cog)
