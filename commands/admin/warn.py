from datetime import timedelta

import discord
from ban import ban_member
from discord import app_commands
from discord.ext import commands
from kick import kick_member

from utils.configmanager import gconfig

#TODO Automatic bans and timeouts on warns
#TODO Add automations to configs

async def add_warns(guild_id, user:discord.Member,interaction:discord.Interaction):
    # Add or update the user's warn count
    user_id = user.id
    if gconfig.get(guild_id, "warns", user_id,default=None) is not None:
        gconfig.set(guild_id, "warns", user_id, gconfig.get(guild_id, "warns", user_id) + 1)  # noqa: E501
    else:
        gconfig.set(guild_id, "warns", user_id, 1)
    if gconfig.get(guild_id, "warns", user_id) >= gconfig.get(guild_id,"warns-settings","timeout",3):  # noqa: E501
        user.timeout(reason="Too many warns", until=gconfig.get(guild_id,"warns-settings","timeout_duration",timedelta(hours=5)), interaction=interaction)  # noqa: E501
    elif gconfig.get(guild_id, "warns", user_id) >= gconfig.get(guild_id,"warns-settings","kick",5):  # noqa: E501, SIM114
        await kick_member(user, "Too many warns", interaction)
    elif gconfig.get(guild_id, "warns", user_id) >= gconfig.get(guild_id,"warns-settings","ban",10):  # noqa: E501
        await ban_member(user, "Too many warns", interaction)


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warns a user.")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):  # noqa: E501
        guild_id = interaction.guild.id
        user_id = user.id

        await add_warns(guild_id, user,interaction)

        await interaction.response.send_message(f"{user.mention} has been warned for: {reason}. They now have {gconfig.get(guild_id,"warns",user_id)} warns.")  # noqa: E501

async def setup(bot:commands.Bot):
    cog = Warn(bot)
    await bot.add_cog(cog)
