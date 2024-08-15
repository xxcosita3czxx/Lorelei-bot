import discord
from discord import app_commands
from discord.ext import commands

import config


class BugReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="echo",description="Echoes message in embed")
    async def bugreport(self,interaction: discord.Interaction,channel:discord.channel.TextChannel, title:str="", text:str=""):  # noqa: E501
        if config.bugreport:
            pass

async def setup(bot:commands.Bot):
    cog = BugReport(bot=bot)
    await bot.add_cog(cog)
