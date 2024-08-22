import logging

import discord
from discord.ext import commands

from utils.configmanager import gconfig


class AntiAlts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def anti_alts(self, member:discord.Member):
        if gconfig.get(id=member.guild.id,title="SECURITY",key="antialts-enabled"):  # noqa: SIM102
            if member.created_at < gconfig.get(id=member.guild.id,title="SECURITY",key="antialts-time"):  # noqa: E501
                logging.warning("Account under time specified")

async def setup(bot:commands.Bot):
    await bot.add_cog(AntiAlts(bot))
