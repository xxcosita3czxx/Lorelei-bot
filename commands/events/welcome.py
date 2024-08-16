
import logging
from string import Template

import discord
from discord.ext import commands

from utils.configmanager import gconfig


def format_string(template, **kwargs):
    # Create a Template object
    tmpl = Template(template)
    # Perform safe substitution
    return tmpl.safe_substitute(**kwargs)


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def on_join(self,member:discord.Member):
        try:
            if gconfig.get(member.guild.id,"MEMBERS","welcome-enabled"):
                placeholders = {
                    "mention":member.mention,
                    "user":member.name,
                    "display":member.display_name,
                    "jointime":member.joined_at,
                    "owner":member.guild.owner.name,
                }
                formated = format_string(gconfig.get(member.guild.id,"MEMBERS","welcome-text"),**placeholders)  # noqa: E501
                logging.debug(formated)
                if gconfig.get(member.guild.id,"MEMBERS","welcome-in_dms"):
                    logging.debug("welcome-indms triggered")
                    if gconfig.get(member.guild.id,"MEMBERS","welcome-rich"):
                        logging.debug("welcome rich triggered")
                        embed = discord.Embed(
                            title=formated,
                        )
                        if member:
                            await member.send(embed=embed)
                        else:
                            logging.error("Member is none")
                    else:
                        if member:
                            await member.send(content=formated)
                        else:
                            logging.error("Member is none")
                channel_id = gconfig.get(member.guild.id,"MEMBERS","welcome-channel")  # noqa: E501
                logging.debug(channel_id)
                channel = member.guild.get_channel(channel_id)
                logging.debug(channel)
                if gconfig.get(member.guild.id,"MEMBERS","welcome-rich"):
                    embed = discord.Embed(
                        title=formated,
                    )
                    if channel:
                        await channel.send(embed=embed)
                    else:
                        logging.error("Channel is none")
                else:
                    if channel:
                        await channel.send(formated)
                    else:
                        logging.error("Channel is none")
        except Exception as e:
            logging.error(f"Unknow error in Welcome: \n{e}")
async def setup(bot:commands.Bot):
    await bot.add_cog(Welcome(bot))