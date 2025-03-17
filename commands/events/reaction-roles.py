import discord  # noqa: F401
from discord import app_commands  # noqa: F401
from discord.ext import commands


#TODO add reaction roles
#TODO pls its really importante
class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot:commands.Bot):
    cog = ReactionRoles(bot)
    await bot.add_cog(cog)

