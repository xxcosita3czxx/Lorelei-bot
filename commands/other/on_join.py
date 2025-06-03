import logging

import discord
from discord.ext import commands

logger = logging.getLogger("on_join")


class OnJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Try system channel first
        channel = guild.system_channel
        if not (channel and channel.permissions_for(guild.me).send_messages):
            # Try to find a channel with "welcome" or "general" in the name
            candidates = [
                c for c in guild.text_channels
                if c.permissions_for(guild.me).send_messages
            ]
            preferred = [c for c in candidates if "welcome" in c.name.lower() or "general" in c.name.lower()]  # noqa: E501
            if preferred:
                channel = preferred[0]
            elif candidates:
                channel = candidates[0]
            else:
                channel = None
        if channel:
            embed = discord.Embed(
                title="Thank you for adding me!",
                description="I'm here to help you manage your server. Use `/help` to see what I can do, or start right by using `/guildconfig configure.\nHope you like it.\n\n(Bot is in constant development, if you find any bug or want anything to change, feel free to do /bugreport)",  # noqa: E501
                color=discord.Color.blurple(),
            )
            await channel.send(embed=embed)
        else:
            logger.debug(f"No channel found to send welcome at {guild.id}")


async def setup(bot):
    await bot.add_cog(OnJoin(bot))
