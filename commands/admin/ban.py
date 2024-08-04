import logging as logger

import discord
from discord import app_commands
from discord.ext import commands
from humanfriendly import format_timespan

from utils.timeconverter import TimeConverter


class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.describe(
        reason="Reason for ban",
        time="Duration of ban",
        member="User to ban",
    )
    @app_commands.default_permissions(ban_members=True)
    async def ban(interaction: discord.Interaction, member: discord.Member, reason: str , time: app_commands.Transform[str, TimeConverter]=None):  # noqa: E501

        '''
        Ban command

        Bans user and let him know why
        '''

        if member == interaction.user or member == interaction.guild.owner:
            return await interaction.response.send_message(
                "You can't ban this user",
                ephemeral=True,
            )

        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "I can't ban this user",
                ephemeral=True,
            )

        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(
                "You can't ban this user due to role hierarchy",
                ephemeral=True,
            )

        try:
            await member.send(
                embed=discord.Embed(
                    description=f"You have been banned from {interaction.guild.name} for {format_timespan(time)}\n**Reason**: {reason}",  # noqa: E501
                    color=discord.Color.blurple(),
                ),
            )

        except discord.HTTPException:
            logger.warning("UNSENT BAN MESSAGE")
            await interaction.response.send_message(
                content="UNSENT BAN MESSAGE",
                ephemeral=True,
            )
        await interaction.guild.ban(member, reason=reason)
        await interaction.response.send_message(
            f"Banned {member.mention}",
            ephemeral=True,
        )
        await interaction.followup.send(
            embed=discord.Embed(
                description=f"{member.mention} has been banned for {format_timespan(time)}\n**Reason**: {reason}",  # noqa: E501
                color=0x2f3136,
            ),
            ephemeral=False,
        )

    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.describe(member="User to unban", reason="Reason for unban")
    @app_commands.default_permissions(ban_members=True)
    async def unban(interaction: discord.Interaction, member: discord.User, reason: str):  # noqa: E501

        '''
        Unban Command

        This will unban person
        '''

        try:
            await interaction.guild.unban(member, reason=reason)

        except discord.NotFound:
            return await interaction.response.send_message(
                "This user is not banned",
                ephemeral=True,
            )

        await interaction.response.send_message(
            f"Unbanned {member.mention}",
            ephemeral=True,
        )
        embed = discord.Embed(
            description=f"{member.mention} has been unbanned\n**Reason**: {reason}",
            color=0x2f3136,
        )
        await interaction.followup.send(embed=embed, ephemeral=False)

async def setup(bot:commands.Bot):
    await bot.add_cog(Ban(bot))
