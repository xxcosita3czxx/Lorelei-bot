import logging
from datetime import datetime

import discord
from discord.ext import commands, tasks

from utils.configmanager import gconfig

#TODO add support for cron style
#TODO pls finish

logger = logging

class AutoMessages(commands.Cog):
    def __init__(self, bot):
        self.bot:discord.AutoShardedClient = bot
        self.auto_message_task.start()

    @tasks.loop(seconds=10)
    async def auto_message_task(self):
        """Background task to send the auto messages based on their intervals."""
        now = datetime.now().timestamp()
        for guild_id, guild_data in gconfig.config.items():
            logger.debug(f"Processing guild_id: {guild_id}, guild_data: {guild_data}")  # noqa: E501
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.warning(f"Guild {guild_id} not found or bot is not a member.")  # noqa: E501
                continue
            for key, value in guild_data.items():
                if key.startswith("automessages-"):
                    # Process the auto message
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
                        embed = discord.Embed(color=discord.Color.random(),description=message)  # noqa: E501
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
    cog = AutoMessages(bot)
    await bot.add_cog(cog)
