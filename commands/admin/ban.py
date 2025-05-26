import logging

import discord
from discord import app_commands
from discord.ext import commands

import config
from utils.configmanager import lang, userlang
from utils.embeder import respEmbed

#from utils.timeconverter import TimeConverter
#from humanfriendly import format_timespan
logger = logging.getLogger("ban")

async def ban_member(member: discord.Member, reason: str, interaction: discord.Interaction,delete_message_days:int):  # noqa: E501
    try:
        await member.send(
            embed=discord.Embed(
                description=lang.get(userlang(interaction.user.id),"Responds","you_was_banned").format(guild=interaction.guild.name,reason=reason),  # noqa: E501 # type: ignore
                color=discord.Color.blurple(),
            ),
        )

    except discord.HTTPException:
        logger.warning(lang.get(config.language,"Responds","warn_unsent_ban"))

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.describe(
        reason=lang.get(config.language,"Descriptions","ban_reason"),
        member=lang.get(config.language,"Descriptions","ban_user"),
        delete_message_days=lang.get(config.language,"Descriptions","ban_delete_message_days"),
    )
    # time: app_commands.Transform[str, TimeConverter]=None
    @app_commands.default_permissions(ban_members=True)
    async def ban(self,interaction: discord.Interaction, member: discord.Member, reason: str="Unspecified",delete_message_days:int=0):  # noqa: E501

        '''
        Ban command

        Bans user and let him know why
        '''

        if member == interaction.user or member == interaction.guild.owner: # type: ignore
            respEmbed(
                content=lang.get(userlang(interaction.user.id),"Responds","you_cant_ban"),
                ephemeral=True,
            ) # type: ignore
            return

        if member.top_role >= interaction.guild.me.top_role: # type: ignore
            respEmbed(
                content=lang.get(userlang(interaction.user.id),"Responds","i_cant_ban"),
                ephemeral=True,
            ) # type: ignore
            return
        if member.top_role >= interaction.user.top_role: # type: ignore
            respEmbed(
                content=lang.get(userlang(interaction.user.id),"Responds","u_cant_ban_hierarchy"),
                ephemeral=True,
            ) # type: ignore
            return
        await ban_member(member, reason, interaction,delete_message_days)
        await interaction.guild.ban(member, reason=reason,delete_message_days=delete_message_days)  # type: ignore # noqa: E501
        respEmbed(
            lang.get(userlang(interaction.user.id),"Responds","user_banned").format(member=member.mention),
            ephemeral=True,
        ) # type: ignore
        await interaction.followup.send(
            embed=discord.Embed(
                description=lang.get(userlang(interaction.user.id),"Responds","user_banned_followup").format(member=member.mention,reason=reason),  # noqa: E501
                color=0x2f3136,
            ),
            ephemeral=False,
        )

    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.describe(
        member=lang.get(config.language,"Descriptions","unban_user"),
        reason=lang.get(config.language,"Descriptions","unban_reason"),
    )
    @app_commands.default_permissions(ban_members=True)
    async def unban(self,interaction: discord.Interaction, member: discord.User, reason: str="Unspecified"):  # noqa: E501

        '''
        Unban Command

        This will unban person
        '''

        try:
            await interaction.guild.unban(member, reason=reason) # type: ignore

        except discord.NotFound:
            return await interaction.response.send_message(
                lang.get(interaction.user.id,"Responds","not_banned"),
                ephemeral=True,
            )

        await interaction.response.send_message(
            lang.get(interaction.user.id,"Responds","user_unbanned").format(member=member.mention),
            ephemeral=True,
        )
        embed = discord.Embed(
            description=lang.get(interaction.user.id,"Responds","user_unbanned_followup").format(member=member.mention,reason=reason),
            color=0x2f3136,
        )
        await interaction.followup.send(embed=embed, ephemeral=False)

async def setup(bot:commands.Bot):
    await bot.add_cog(Ban(bot))
