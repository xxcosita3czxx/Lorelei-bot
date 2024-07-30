import discord
from discord import app_commands
from discord.ext import commands
from humanfriendly import format_timespan

from utils.configmanager import lang, uconfig
from utils.timeconverter import TimeConverter


class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="slowmode", description="Set slowmode for the channel")  # noqa: E501
    @app_commands.describe(time="Slowmod Time")
    @app_commands.default_permissions(manage_channels = True)
    async def slowmode(self, interaction: discord.Interaction,time: app_commands.Transform[str, TimeConverter]=None):  # noqa: E501

        max_time = 21600
        if time <= 0:
            await interaction.channel.edit(slowmode_delay=0)
            await interaction.response.send_message(
                content="Slowmode has been disabled",
                ephemeral=True,
            )
            await interaction.channel.send(
                embed=discord.Embed(
                    description=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","slowmode_disable").format(interaction.channel.mention),  # noqa: E501
                    color=discord.Color.green(),
                ),
            )

        elif time > max_time:
            await interaction.response.send_message(
                content=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","slowmode_max_reach"),
                ephemeral=True,
            )

        else:
            await interaction.channel.edit(slowmode_delay=time)
            await interaction.response.send_message(
                f"Slowmode has been set to {format_timespan(time)} seconds",
                ephemeral=True,
            )
            await interaction.channel.send(
                embed=discord.Embed(
                    description=f"Slow mode has been set to {format_timespan(time)} to {interaction.channel.mention}",  # noqa: E501
                    color=discord.Color.green(),
                ),
            )

async def setup(bot:commands.Bot):
    await bot.add_cog(Slowmode(bot))
