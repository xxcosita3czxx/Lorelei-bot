import discord
from discord import app_commands
from discord.ext import commands


class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot:commands.Bot):
    cog = LevelSystem(bot)
    await bot.add_cog(cog)
