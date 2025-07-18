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
    if gconfig.get(guild_id, "warns", user_id) >= gconfig.get(guild_id,"warns-settings","timeout",3):  # type: ignore # noqa: E501
        user.timeout(reason=reason, until=gconfig.get(guild_id,"warns-settings","timeout_duration",timedelta(hours=5)))  # type: ignore # noqa: E501
    elif gconfig.get(guild_id, "warns", user_id) >= gconfig.get(guild_id,"warns-settings","kick",5):  # noqa: E501, SIM114
        await kick_member(user, reason, interaction)
    elif gconfig.get(guild_id, "warns", user_id) >= gconfig.get(guild_id,"warns-settings","ban",10):  # noqa: E501
        await ban_member(user, reason, interaction) # type: ignore


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warns a user.")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):  # noqa: E501
        guild_id = interaction.guild.id # type: ignore
        user_id = user.id

        await add_warns(guild_id, user,interaction)

        await interaction.response.send_message(f"{user.mention} has been warned for: {reason}. They now have {gconfig.get(guild_id,'warns',user_id)} warns.")  # noqa: E501

async def setup(bot:commands.Bot):
#    cog = Warn(bot)
#    await bot.add_cog(cog)

    @app_commands.context_menu(name="Warn")
    @app_commands.default_permissions(kick_members=True)
    async def warn_context(interaction:discord.Interaction,member:discord.Member):
        add_warns(interaction.guild.id, member.id,interaction) # type: ignore
    #bot.tree.add_command(warn_context)
