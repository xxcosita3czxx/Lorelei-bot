import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import gconfig

#TODO Automatic bans and timeouts on warns
#TODO Add automations to configs

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warns a user.")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):  # noqa: E501
        guild_id = interaction.guild.id
        user_id = user.id

        # Add or update the user's warn count
        if gconfig.get(guild_id, "warns", user_id,default=None) is not None:
            gconfig.set(guild_id, "warns", user_id, gconfig.get(guild_id, "warns", user_id) + 1)  # noqa: E501
        else:
            gconfig.set(guild_id, "warns", user_id, 1)

        await interaction.response.send_message(f"{user.mention} has been warned for: {reason}. They now have {gconfig.get(guild_id,"warns",user_id)} warns.")  # noqa: E501

async def setup(bot:commands.Bot):
    cog = Warn(bot)
    await bot.add_cog(cog)
