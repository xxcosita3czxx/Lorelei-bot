import discord
from discord import app_commands
from discord.ext import commands


class Welcome_test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="welcometest", description="testinks")
    async def welcome_test(self,interaction:discord.Interaction):
        welcome_emeb = discord.Embed(title="Hello!", description=f"Welcome {interaction.user.name}!")  # noqa: E501
        await interaction.response.send_message(embed=welcome_emeb)

async def setup(bot:commands.Bot):
#    cog = Welcome_test(bot)
#    await bot.add_cog(cog)
    pass
