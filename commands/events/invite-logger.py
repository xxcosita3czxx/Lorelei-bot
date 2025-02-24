import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_invites

logger = logging.getLogger("invite-logger")

class InviteLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}
    class Invites(app_commands.Group):
        def __init__(self):
            super().__init__(self)
            self.name="invites"
            self.description="No bots in the server"

        @app_commands.command(name="invite",description="Get info about invite")
        @app_commands.autocomplete(invite=autocomplete_invites)
        async def invite(self,interaction:discord.Interaction,invite:str):  # noqa: E501
            await interaction.response.send_message(
                content=f"Invite {invite.code} was created by {invite.inviter.name}#{invite.inviter.discriminator} and has {invite.uses} uses.",  # noqa: E501
                ephemeral=True,
            )

        @app_commands.command(name="user",description="Get all invites from a user")
        async def user(self,interaction:discord.Interaction,user:discord.User):
            invites = await interaction.guild.invites()
            user_invites = [invite for invite in invites if invite.inviter == user]
            if user_invites:
                await interaction.response.send_message(
                    content=f"{user.name}#{user.discriminator} has created {len(user_invites)} invites.",  # noqa: E501
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    content=f"{user.name}#{user.discriminator} has not created any invites.",  # noqa: E501
                    ephemeral=True,
                )

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.invites[guild.id] = await guild.invites()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        used_invite = await self.get_used_invite(member)
        if used_invite:
            inviter:discord.Member = used_invite.inviter
            logger.debug(f"{member} was invited by {inviter.name}")
    async def get_used_invite(self, member: discord.Member):
        invites_before = self.invites[member.guild.id]
        invites_after = await member.guild.invites()

        used_invite = None
        for invite in invites_before:
            if invite.uses < next((inv.uses for inv in invites_after if inv.code == invite.code), invite.uses):  # noqa: E501
                used_invite = invite
                break

        self.invites[member.guild.id] = invites_after
        return used_invite

async def setup(bot: commands.Bot):
#    await bot.add_cog(InviteLogger(bot))
#    bot.tree.add_command(InviteLogger.Invites())
    pass
