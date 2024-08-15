import logging

import discord
from discord.ext import commands

from utils.configmanager import gconfig


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self,member:discord.Member):
        try:
            logging.debug("on_member_join was triggered!")
            logging.debug(str(member.guild) + " / " + str(member.guild.id))
            if gconfig.get(str(member.guild.id),"MEMBERS","autorole-enabled") is True:  # noqa: E501
                role_id = gconfig.get(str(member.guild.id),"MEMBERS","autorole-role")  # noqa: E501
                logging.debug("Role_id:"+str(role_id))
                role = member.guild.get_role(role_id)
                await member.add_roles(role)
        except Exception as e:
            logging.warn(f"Unknown error in Auto-role: \n{e}")
async def setup(bot:commands.Bot):
    await bot.add_cog(AutoRole(bot))
