import json
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.configmanager import gconfig

#TODO add support for cron style
#TODO pls finish
class AutoMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_message_task.start()

    @tasks.loop(minutes=1)
    async def auto_message_task(self):
        """Background task to send the auto messages based on their intervals."""
        now = datetime.now().timestamp()
        for guild_id, guild_data in gconfig.config.items():
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            for key, value in guild_data.items():
                if key.startswith("automessages-"):
                    # Process the auto message
                    pass
                _, channelid = key.split("-")
                channel = guild.get_channel(int(channelid))
                if not channel:
                    continue
                interval = value.get("interval", 0)
                timestamp = value.get("timestamp", 0)
                message = value.get("message", "")
                if not message or not interval:
                    continue
                if gconfig.get(guild_id,f"automessages-{channelid}","embed"):
                    embed = discord.Embed(color=discord.Color.random(),description=message)
                else:
                    embed = None
                if timestamp + interval < now:
                    if embed is None:
                        await channel.send(message)
                    else:
                        await channel.send(message,embed=embed)
                    gconfig.set(guild_id,f"automessages-{channelid}","timestamp",now)

    @auto_message_task.before_loop
    async def before_auto_message_task(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
#    cog = AutoMessages(bot)
#    await bot.add_cog(cog)
    pass
