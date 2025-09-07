import discord
from discord import app_commands
from discord.ext import commands


class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="welcome-embed-test", description="Greets")
    async def hello(interaction:discord.Interaction):
        welcome_emeb = discord.Embed(title="Hello!", description=f"Hello {interaction.user.name}!")  # noqa: E501
        await interaction.response.send_message(embed=welcome_emeb)

async def setup(bot:commands.Bot):
    cog = Hello(bot)
    await bot.add_cog(cog)
