import time

import discord
from discord import app_commands
from discord.ext import commands

import config


class BugReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="bugreport",description="Here you can report bug")
    @app_commands.checks.cooldown(1, 45, key=lambda i: (i.guild_id, i.user.id))
    async def bugreport(self,interaction: discord.Interaction,channel:discord.channel.TextChannel, title:str="", text:str=""):  # noqa: E501
        if config.bugreport:
            try:
                with open(f"data/bug-reports/bugreport-{interaction.guild.id}-{interaction.user.id}-{time.localtime()}"):  # noqa: E501
                    pass
            except Exception as e:
                interaction.response.send_message(f"There was error while making bugreport. Please report on Support server or github. \nError: {e}",ephemeral=True)  # noqa: E501
        else:
            interaction.response.send_message("Bug reports disabled in config.", ephemeral=True)  # noqa: E501

async def setup(bot:commands.Bot):
    cog = BugReport(bot=bot)
    await bot.add_cog(cog)
