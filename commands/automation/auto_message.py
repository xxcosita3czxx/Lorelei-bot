import logging
from datetime import datetime

import discord
from discord.ext import commands, tasks

from utils.configmanager import gconfig
from utils.guildconfig import GuildConfig

logger = logging

class AutoMessages(commands.Cog):
    def __init__(self, bot):
        self.bot:discord.AutoShardedClient = bot
        self.auto_message_task.start()

    @tasks.loop(seconds=60)  # Increased interval to reduce intensity
    async def auto_message_task(self):
        """Background task to send the auto messages based on their intervals."""
        now = datetime.now().timestamp()
        for guild_id, guild_data in gconfig.config.items():
            logger.debug(f"Processing guild_id: {guild_id}, guild_data: {guild_data}")  # noqa: E501
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                # Shouldnt care if the bot left the guild, but maybe ill do job to clean those  # noqa: E501
                logger.debug(f"Guild {guild_id} not found or bot is not a member.")  # noqa: E501
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
                            await channel.send(message) # type: ignore
                        else:
                            await channel.send(message,embed=embed) # type: ignore
                        # Synchronize to the next full interval (e.g., next minute)
                        next_time = ((int(now) // interval) + 1) * interval
                        gconfig.set(guild_id,f"automessages-{channelid}","timestamp",next_time)

    @auto_message_task.before_loop
    async def before_auto_message_task(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    cog = AutoMessages(bot)
    await bot.add_cog(cog)
    configman = GuildConfig()
    configman.add_setting("Automation", "Auto Message", "Configure automatic messages sent to channels at regular intervals.")  # noqa: E501
#                gconfig.set(guild_id,f"automessages-{channel_id}", "embed", embed)
#                gconfig.set(guild_id,f"automessages-{channel_id}", "message", message)  # noqa: E501
#                gconfig.set(guild_id,f"automessages-{channel_id}", "interval", interval)  # noqa: E501
#                gconfig.set(guild_id,f"automessages-{channel_id}", "timestamp", timestamp)  # noqa: E501
# need to make a id list type config / selector
#    configman.add_custom_setting("Automation","Auto Message Example",discord.Embed(title="Auto Message Example",description="This is an example of an automatic message sent to a channel at regular intervals.",color=discord.Color.blue()),"An example of an automatic message sent to a channel at regular intervals.")  # noqa: E501

#TODO need a way to get interaction here, like the channel id of the channel where configuring happens  # noqa: E501
