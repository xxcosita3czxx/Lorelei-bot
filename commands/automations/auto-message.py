import json
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.configmanager import gconfig


class AutoMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_message_task.start()

    @tasks.loop(minutes=1)
    async def auto_message_task(self):
        """Background task to send the auto messages based on their intervals."""
        now = datetime.now().timestamp() 
        
    @auto_message_task.before_loop
    async def before_auto_message_task(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
#    cog = AutoMessages(bot)
#    await bot.add_cog(cog)
    pass
