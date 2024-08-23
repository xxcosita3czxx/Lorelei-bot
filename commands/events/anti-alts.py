import logging

import discord
from discord.ext import commands

from utils.configmanager import gconfig

#from humanfriendly import format_timespan

class AntiAlts(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def anti_alts(self, member:discord.Member):
        if gconfig.get(id=member.guild.id,title="SECURITY",key="antialts-enabled"):  # noqa: SIM102
            if member.created_at < gconfig.get(id=member.guild.id,title="SECURITY",key="antialts-time"):  # noqa: E501
                text = "Your account was detected to be an Alternative account, please join with your main account or wait for {time} until joining again."  # noqa: E501
                embed = discord.Embed(
                    title="ALT Account Detected!",
                    description=text,
                )
                member.send(embed=embed)
                member.kick("Alternative Account [Lorelei]")
            else:
                logging.debug("Acc okay")
        logging.debug("antialts disabled :<")
async def setup(bot:commands.Bot):
    await bot.add_cog(AntiAlts(bot))
