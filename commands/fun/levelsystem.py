import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import gconfig


class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="global-leaderboard",description="Level Leaderboard")
    async def global_leaderboard(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="leaderboard",description="Server Leaderboard")
    async def leaderboard(self, interaction:discord.Interaction):
        if gconfig.get(interaction.guild.id,""):
            pass

    @app_commands.command(name="profile",description="Your profile")
    async def profile(self,interaction: discord.Interaction, minimal:bool=True):
        if minimal:
            embed = discord.Embed(title=f"Profile of {interaction.user.name}")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Not yet made", ephemeral=True)


async def setup(bot:commands.Bot):
#    cog = LevelSystem(bot)
#    await bot.add_cog(cog)
    pass
