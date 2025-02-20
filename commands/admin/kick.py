import logging

import discord
from discord import app_commands
from discord.ext import commands


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

        if member == interaction.user or member == interaction.guild.owner:
            return await interaction.response.send_message(
                "You can't kick this user",
                ephemeral=True,
            )

        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "I can't kick this user",
                ephemeral=True,
            )

        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(
                "You can't kick this user due to role hierarchy",
                ephemeral=True,
            )

        try:
            await member.send(
                embed=discord.Embed(
                    description=f"You have been kicked from {interaction.guild.name}\n**Reason**: {reason}",  # noqa: E501
                    color=discord.Color.red(),
                ),
            )

        except discord.HTTPException as e:
            await interaction.response.send_message(
                content=f"UNSEND KICK MESSAGE: {e}",
            )
            logging.warning(f"UNSENT KICK MESSAGE: {e}")

        await member.kick(reason=reason)
        await interaction.response.send_message(
            f"Kicked {member.mention}",
            ephemeral=True,
        )
        embed = discord.Embed(
            description=f"{member.mention} has been kicked\n**Reason**: {reason}",
            color=0x2f3136,
        )
        await interaction.followup.send(embed=embed, ephemeral=False)

async def setup(bot:commands.Bot):
    await bot.add_cog(Kick(bot))

    @app_commands.context_menu(name="Kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick_context(interaction:discord.Interaction,member:discord.Member):
        await Kick.kick(interaction, member,"Unspecified")
    bot.tree.add_command(kick_context)
