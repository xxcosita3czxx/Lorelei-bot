
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
        if gconfig.get(member.guild.id,"MEMBERS","welcome-enabled"):
            placeholders = {
                "mention":member.mention,
                "user":member.name,
                "display":member.display_name,
                "jointime":member.joined_at,
                "owner":member.guild.owner.name,
            }
            formated = format_string(gconfig.get(member.guild.id,"MEMBERS","welcome-text"),**placeholders)  # noqa: E501
            if gconfig.get(member.guild.id,"MEMBERS","welcome-in_dms"):
                if gconfig.get(member.guild.id,"MEMBERS","welcome-rich"):
                    embed = discord.Embed(
                        title=formated,
                    )
                    member.send(embed=embed)
                else:
                    member.send(content=formated)
            channel_id = gconfig.get(member.guild.id,"MEMBERS","welcome-channel")
            channel = member.guild.get_channel(channel_id)
            if gconfig.get(member.guild.id,"MEMBERS","welcome-rich"):
                embed = discord.Embed(
                    title=formated,
                )
                channel.send(embed=embed)
            else:
                channel.send(formated)

async def setup(bot:commands.Bot):
    await bot.add_cog(Welcome(bot))
