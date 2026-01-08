import logging

import discord
from discord.ext import commands

from utils.configmanager import lang

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
            preferred = [c for c in candidates if "welcome" in c.name.lower() or "general" in c.name.lower() or "chat" in c.name.lower()]  # noqa: E501
            if preferred:
                channel = preferred[0]
            elif candidates:
                channel = candidates[0]
            else:
                channel = None
        if channel:
            language = guild.preferred_locale
            if language == "zh-CN":
                language = "cn"
            elif language == "en-US" or language == "en-GB" or language not in lang.config:  # noqa: E501
                language = "en"
            embed = discord.Embed(
                title=lang.get(language,"Responds","on_join_title"),
                description=lang.get(language,"Responds","on_join_desc"),  # noqa: E501
                color=discord.Color.blurple(),
            )
            await channel.send(embed=embed)
        else:
            logger.debug(f"No channel found to send welcome at {guild.id}")


async def setup(bot):
    await bot.add_cog(OnJoin(bot))
