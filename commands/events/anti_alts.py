import datetime
import logging

import discord
from discord.ext import commands

from utils.configmanager import gconfig
from utils.guildconfig import GuildConfig  # noqa: F401

#from humanfriendly import format_timespan
logger = logging.getLogger("anti-alts")

class AntiAlts(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def anti_alts(self, member:discord.Member):
        if gconfig.get(id=member.guild.id,title="SECURITY",key="antialts-enabled"):  # noqa: SIM102

            creation_time = member.created_at
            current_time = datetime.datetime.now(datetime.UTC)
            account_age = (current_time - creation_time).total_seconds()

            if account_age <= int(gconfig.get(id=member.guild.id,title="SECURITY",key="antialts-time")):  # noqa: E501


                text = "Your account was detected to be an Alternative account, please join with your main account or wait for {time} until joining again."  # noqa: E501
                embed = discord.Embed(
                    title="ALT Account Detected!",
                    description=text,
                )
                await member.send(embed=embed)
                await member.kick(reason="[Lorelei] Alternative Account")
            else:
                logger.debug("Acc okay")
        logger.debug("antialts disabled :<")

async def setup(bot:commands.Bot):
    await bot.add_cog(AntiAlts(bot))
    configman = GuildConfig()
    configman.add_setting(
        category_name="Security",
        setting_name="Anti-Alts",
        description="Anti-Alts system to prevent alternative accounts from joining the server.",  # noqa: E501
    )
    configman.add_option_bool( # type: ignore
        category_name="Security",
        setting_name="Anti-Alts",
        name="Enabled",
        button_title="Enable",
        config_title="SECURITY",
        config_key="antialts-enabled",
        description="Enable Anti-Alts",
    )
