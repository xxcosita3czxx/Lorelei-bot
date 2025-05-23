import logging

import discord
from discord.ext import commands

from utils.configmanager import gconfig
from utils.helpmanager import HelpManager

logger = logging.getLogger("autorole")
class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self,member:discord.Member):
        try:
            logger.debug("on_member_join was triggered!")
            logger.debug(str(member.guild) + " / " + str(member.guild.id))
            if gconfig.get(str(member.guild.id),"MEMBERS","autorole-enabled") is True:  # noqa: E501
                role_id = gconfig.get(str(member.guild.id),"MEMBERS","autorole-role")  # noqa: E501
                logger.debug("Role_id:"+str(role_id))
                role = member.guild.get_role(int(role_id))
                await member.add_roles(role) # type: ignore
        except discord.Forbidden:
            await member.send("Autorole failed, tell administrator to check permissions")  # noqa: E501
            logger.info("Autorole failed due to permissions")
        except discord.HTTPException:
            logger.warning("Autorole adding failed, HTTPException")
        except Exception as e:
            logger.warning(f"Unknown error in Auto-role: \n{e}")

async def setup(bot:commands.Bot):
    await bot.add_cog(AutoRole(bot))
    hm = HelpManager()
    hmhelp = hm.new_help("members","autorole","Automatically assigns a role to new members")  # noqa: E501
    hmhelp.set_help_page(1,"AutoRole","Automatically assigns a role to new members. Useful for default role or permissions that doesnt use everyone")  # noqa: E501
