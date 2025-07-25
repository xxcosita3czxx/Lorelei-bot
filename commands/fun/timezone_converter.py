import discord
from discord import app_commands
from discord.ext import commands


class TimezoneConverter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="convert_timezone", description="Converts time between timezones")  # noqa: E501
    async def convert_timezone(self, interaction: discord.Interaction, time: str, from_tz: str, to_tz: str):  # noqa: E501
        # Placeholder for actual timezone conversion logic
        await interaction.response.send_message(f"Converting {time} from {from_tz} to {to_tz}...")  # noqa: E501

async def setup(bot: commands.Bot):
#    cog = TimezoneConverter(bot)
#    await bot.add_cog(cog)
    pass
