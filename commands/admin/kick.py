import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import lang, userlang

logger = logging.getLogger("kick")

async def kick_member(member: discord.Member, reason: str, interaction: discord.Interaction):  # noqa: E501
    try:
        await member.send(
            embed=discord.Embed(
                #description=f"You have been kicked from {interaction.guild.name}\n**Reason**: {reason}",  # noqa: E501
                description=lang.get(member.id(interaction.user.id),"Responds","user_kicked_dms").format(guild=interaction.guild.name,reason=reason), # type: ignore
                color=discord.Color.red(),
            ),
        )

    except discord.HTTPException as e:
        logger.warning(f"UNSENT KICK MESSAGE: {e}")

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a user")
    @app_commands.describe(member="User to kick", reason="Reason for kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self,interaction: discord.Interaction, member: discord.Member, reason: str):  # noqa: E501

        '''
        Kick command

        Kicks user from guild and let him know why
        '''

        if member == interaction.user or member == interaction.guild.owner: # type: ignore
            return await interaction.response.send_message(
                lang.get(userlang(interaction.user.id),"Responds","you_cant_kick"), # type: ignore
                ephemeral=True,
            )

        if member.top_role >= interaction.guild.me.top_role: # type: ignore
            return await interaction.response.send_message(
                lang.get(userlang(interaction.user.id),"Responds","i_cant_kick"), # type: ignore
                ephemeral=True,
            )

        if member.top_role >= interaction.user.top_role: # type: ignore
            return await interaction.response.send_message(
                lang.get(userlang(interaction.user.id),"Responds","u_cant_kick_role_hiearhy"), # type: ignore
                ephemeral=True,
            )

        await kick_member(member, reason, interaction)

        await member.kick(reason=reason)
        await interaction.response.send_message(
            lang.get(userlang(interaction.user.id),"Responds","user_kicked").format(member=member.mention), # type: ignore
            ephemeral=True,
        )
        embed = discord.Embed(
            #description=f"{member.mention} has been kicked\n**Reason**: {reason}",
            description=lang.get(userlang(interaction.user.id),"Responds","user_kicked_embed").format(member=member.mention,reason=reason), # type: ignore
            color=0x2f3136,
        )
        await interaction.followup.send(embed=embed, ephemeral=False)

async def setup(bot:commands.Bot):
    await bot.add_cog(Kick(bot))

    @app_commands.context_menu(name="Kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick_context(interaction:discord.Interaction,member:discord.Member):
        await Kick.kick(interaction, member,lang.get(userlang(interaction.user.id),"Responds","unspecified")) # type: ignore  # noqa: E501
    bot.tree.add_command(kick_context)
