import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import lang, uconfig


class userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="user-info",description="Info about user")
    async def user_info(self, interaction:discord.Interaction, member:discord.User):
        logging.debug(member.display_avatar.key)
        embed = discord.Embed(title="Info about", color=discord.Color.blurple())
        embed.set_thumbnail(url=member.display_avatar.url)
        ulang = uconfig.get(interaction.user.id,"Appearance","language")

        embed.add_field(
            name=lang.get(ulang,"UserInfo","username"),
            value=member.name,
            inline=True,
        )

        embed.add_field(
            name=lang.get(ulang,"UserInfo","display_name"),
            value=member.display_name,
            inline=True,
        )

        embed.add_field(
            name=lang.get(ulang,"UserInfo","id"),
            value=member.id,
            inline=True,
        )

        embed.add_field(
            name=lang.get(ulang,"UserInfo","joined_dsc"),
            value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            inline=True,
        )

        embed.add_field(
            name=lang.get(ulang,"UserInfo","joined_guild"),
            value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            inline=True,
        )

        embed.add_field(
            name=lang.get(ulang,"UserInfo","roles"),
            value=", ".join([role.name for role in member.roles]),
            inline=False,
        )
async def setup(bot:commands.Bot):
    await bot.add_cog(userinfo(bot))

    @app_commands.context_menu(name="User Info")
    async def user_info(interaction: discord.Interaction, member:discord.User):
        logging.debug(member.display_avatar.key)
        embed = discord.Embed(title="Info about", color=discord.Color.blurple())
        embed.set_thumbnail(url=member.display_avatar.url)
        ulang = uconfig.get(interaction.user.id,"Appearance","language")

        embed.add_field(
            name=lang.get(ulang,"UserInfo","username"),
            value=member.name,
            inline=True,
        )

        embed.add_field(
            name=lang.get(ulang,"UserInfo","display_name"),
            value=member.display_name,
            inline=True,
        )

        embed.add_field(
            name=lang.get(ulang,"UserInfo","id"),
            value=member.id,
            inline=True,
        )

        embed.add_field(
            name=lang.get(ulang,"UserInfo","joined_dsc"),
            value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            inline=True,
        )

        embed.add_field(
            name=lang.get(ulang,"UserInfo","joined_guild"),
            value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            inline=True,
        )

        embed.add_field(
            name=lang.get(ulang,"UserInfo","roles"),
            value=", ".join([role.name for role in member.roles]),
            inline=False,
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )
    bot.tree.add_command(user_info)
