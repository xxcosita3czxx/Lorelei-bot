import discord
from discord import app_commands
from discord.ext import commands

#TODO Warn system saving to server config in usable way
#TODO Automatic bans and timeouts on warns
#TODO Add automations to configs

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Greets")
    async def hello(interaction:discord.Interaction):
        await interaction.response.send_message("Hello!")

async def setup(bot:commands.Bot):
#    cog = Warn(bot)
#    await bot.add_cog(cog)
    pass
