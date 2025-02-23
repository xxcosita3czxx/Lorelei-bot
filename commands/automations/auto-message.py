import json
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.configmanager import gconfig


class AutoMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_messages = {}
        self.load_config()
        self.auto_message_task.start()

    def load_config(self):
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            self.auto_messages[guild_id] = {}
            for channel in guild.text_channels:
                channel_id = str(channel.id)
                config_key = f"{guild_id}.automessages-{channel_id}"
                self.auto_messages[guild_id][channel_id] = {
                    "message": gconfig.get(config_key, "message"),
                    "interval": gconfig.get(config_key, "interval"),
                    "timestamp": gconfig.get(config_key, "timestamp")
                }

    def save_config(self, guild_id, channel_id):
        config_key = f"{guild_id}.automessages-{channel_id}"
        gconfig.set(config_key, "message", self.auto_messages[guild_id][channel_id]["message"])
        gconfig.set(config_key, "interval", self.auto_messages[guild_id][channel_id]["interval"])
        gconfig.set(config_key, "timestamp", self.auto_messages[guild_id][channel_id]["timestamp"])

    @app_commands.command(name="set_message", description="Set an auto message, interval, and channel")
    async def set_message(self, interaction: discord.Interaction, message: str, interval: int, channel: discord.TextChannel):
        """Set an auto message, interval, and channel.

        Args:
            interaction (discord.Interaction): The interaction object.
            message (str): The message to send.
            interval (int): The interval in minutes for sending the message.
            channel (discord.TextChannel): The channel to send the message in.
        """
        guild_id = str(interaction.guild_id)
        channel_id = str(channel.id)
        timestamp = (datetime.now() + timedelta(minutes=interval)).timestamp()
        if guild_id not in self.auto_messages:
            self.auto_messages[guild_id] = {}
        self.auto_messages[guild_id][channel_id] = {
            "message": message,
            "interval": interval,
            "timestamp": timestamp
        }
        self.save_config(guild_id, channel_id)
        await interaction.response.send_message(f"Auto message set to '{message}' with interval '{interval}' minutes in channel {channel.mention}")

    @tasks.loop(minutes=1)
    async def auto_message_task(self):
        """Background task to send the auto messages based on their intervals."""
        now = datetime.now().timestamp()
        for guild_id, channels in self.auto_messages.items():
            for channel_id, auto_message in channels.items():
                if auto_message["message"] and auto_message["timestamp"] and auto_message["interval"]:
                    if now >= auto_message["timestamp"]:
                        channel = self.bot.get_channel(int(channel_id))
                        if channel:
                            await channel.send(auto_message["message"])
                            auto_message["timestamp"] = (datetime.now() + timedelta(minutes=auto_message["interval"])).timestamp()
                            self.save_config(guild_id, channel_id)

    @auto_message_task.before_loop
    async def before_auto_message_task(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
#    cog = AutoMessages(bot)
#    await bot.add_cog(cog)
    pass