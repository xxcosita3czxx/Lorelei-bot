import discord
from discord import app_commands
from discord.ext import commands


class GlobalLevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="global-leaderboard")
    async def global_leaderboard(self,interaction:discord.Interaction):
        pass
async def setup(bot:commands.Bot):
    cog = GlobalLevelSystem(bot)
    await bot.add_cog(cog)
