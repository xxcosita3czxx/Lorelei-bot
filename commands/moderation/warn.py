from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import gconfig, lang, userlang

from ..moderation.ban import ban_member
from .kick import kick_member

#TODO Automatic bans and timeouts on warns
#TODO Add automations to configs
#TODO posibility for more custom punishments

async def add_warns(guild_id, user:discord.Member,interaction:discord.Interaction):
# Add or update the user's warn count
    user_id = user.id
    reason = lang.get(userlang(user.id),"Responds","too_many_warns")
    if gconfig.get(guild_id, "warns", user_id,default=None) is not None:
        gconfig.set(guild_id, "warns", user_id, gconfig.get(guild_id, "warns", user_id) + 1)  # noqa: E501
    else:
        gconfig.set(guild_id, "warns", user_id, 1)
    if gconfig.get(guild_id, "warns", user_id) >= gconfig.get(guild_id,"warns-settings","ban",10):  # noqa: E501
        await ban_member(user, reason, interaction) # type: ignore
    elif gconfig.get(guild_id, "warns", user_id) == gconfig.get(guild_id,"warns-settings","kick",5):  # noqa: E501, SIM114
        await kick_member(user, reason, interaction)
    elif gconfig.get(guild_id, "warns", user_id) == gconfig.get(guild_id,"warns-settings","timeout",3):  # type: ignore # noqa: E501
        user.timeout(reason=reason, until=gconfig.get(guild_id,"warns-settings","timeout_duration",timedelta(hours=5)))  # type: ignore # noqa: E501


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warns a user.")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):  # noqa: E501
        await add_warns(interaction.guild.id, user,interaction)
        await interaction.response.send_message(f"{user.mention} has been warned for: {reason}. They now have {gconfig.get(interaction.guild.id,'warns',user.id)} warns.")  # noqa: E501

    @app_commands.command(name="unwarn", description="Removes a warn from a user.")
    @app_commands.default_permissions(moderate_members=True)
    async def unwarn(self, interaction: discord.Interaction, user: discord.Member):  # noqa: E501
        if gconfig.get(interaction.guild.id, "warns", user.id, default=0) > 0:
            gconfig.set(interaction.guild.id, "warns", user.id, gconfig.get(interaction.guild.id, "warns", user.id) - 1)  # noqa: E501
            await interaction.response.send_message(f"{user.mention} has had a warn removed. Now they have {gconfig.get(interaction.guild.id, 'warns', user.id)} warns.", ephemeral=True)  # noqa: E501

    @app_commands.command(name="clear-warns", description="Clears all warns for a user.")  # noqa: E501
    @app_commands.default_permissions(moderate_members=True)
    async def clear_warns(self, interaction: discord.Interaction, user: discord.Member):  # noqa: E501
        gconfig.set(interaction.guild.id, "warns", user.id, 0)  # type: ignore
        await interaction.response.send_message(f"{user.mention} has had their warns cleared.", ephemeral=True)  # noqa: E501

    @app_commands.command(name="warns", description="Shows the number of warns a user has.")  # noqa: E501
    @app_commands.default_permissions(moderate_members=True)
    async def warns(self, interaction: discord.Interaction, user: discord.Member):  # noqa: E501
        warns = gconfig.get(interaction.guild.id, "warns", user.id, default=0)  # type: ignore
        await interaction.response.send_message(f"{user.mention} has {warns} warns.", ephemeral=True)  # noqa: E501

async def setup(bot:commands.Bot):
#    cog = Warn(bot)
#    await bot.add_cog(cog)

    @app_commands.context_menu(name="Warn")
    @app_commands.default_permissions(kick_members=True)
    async def warn_context(interaction:discord.Interaction,member:discord.Member):
        add_warns(interaction.guild.id, member.id,interaction) # type: ignore

    @app_commands.context_menu(name="Unwarn")
    @app_commands.default_permissions(kick_members=True)
    async def unwarn_context(interaction:discord.Interaction,member:discord.Member):
        if gconfig.get(interaction.guild.id, "warns", member.id, default=0) > 0:
            gconfig.set(interaction.guild.id, "warns", member.id, gconfig.get(interaction.guild.id, "warns", member.id) - 1)  # noqa: E501
            await interaction.response.send_message(f"{member.mention} has had a warn removed. Now they have {gconfig.get(interaction.guild.id, 'warns', member.id)} warns.", ephemeral=True)  # noqa: E501

    #bot.tree.add_command(unwarn_context)
    #bot.tree.add_command(warn_context)
