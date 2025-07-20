
#TODO i though of using automod for this one, basicaly cathing automod and sending
#TODO the message censored (switchable)
#TODO Shall use the automod execution event, even tho im not sure about the limitations of the automod.  # noqa: E501
#TODO if automod is too limited, i can just be normal and use events, even tho the
#TODO automod does use discord internal functions and catches it before its sent

import discord
from discord import app_commands
from discord.ext import commands


class Censore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot:commands.Bot):
    cog = Censore(bot)
    await bot.add_cog(cog)
