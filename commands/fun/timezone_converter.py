from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from pytz import timezone

from utils.configmanager import uconfig
from utils.guildconfig import GuildConfig

#TODO User config for current timezone, else disable auto from user timezone to selected  # noqa: E501
#TODO Add a list of timezones to choose from, or use pytz.all_timezones
#TODO Fun thing could be from user timezone to another user timezone

class TimezoneConverter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="convert_timezone", description="Converts time between timezones")  # noqa: E501
    async def convert_timezone(self, interaction: discord.Interaction, time: str= None, from_tz: str=None, to_tz: str=None, user:discord.Member=None):  # noqa: E501
        users_timezone = uconfig.get(
            id=interaction.user.id,
            title="FUN",
            key="current-timezone",
            default=None,
        )
        if from_tz is None and users_timezone is None:
            # Show timezone selection UI (like ftsetup.py)
            embed = discord.Embed(
                title="Set Your Timezone",
                description=(
                    "You haven't set a default timezone yet. "
                    "Please select your continent and city/region."
                ),
                color=discord.Color.blurple(),
            )
            from commands.other.ftsetup import ContinentTimezoneView
            await interaction.response.send_message(
                embed=embed,
                view=ContinentTimezoneView(interaction.user, {}),
                ephemeral=True,
            )
            return
        if from_tz is None:
            from_tz = users_timezone
        if to_tz is None:
            await interaction.response.send_message(
                content="Please provide a timezone, or user with timezone to convert to.",  # noqa: E501
                ephemeral=True,
            )
            return
        try:
            from_timezone = timezone(from_tz)
            to_timezone = timezone(to_tz)
            # Assuming time is in HH:MM format
            from_time = from_timezone.localize(
                datetime.strptime(time, "%H:%M"),
            )
            to_time = from_time.astimezone(to_timezone)
            formatted_time = to_time.strftime("%H:%M %Z")
            await interaction.response.send_message(
                content=f"The time {time} in {from_tz} is {formatted_time} in {to_tz}.",  # noqa: E501
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Error converting time: {str(e)}",
                ephemeral=True,
            )
            return
async def setup(bot: commands.Bot): #TODO this is just broken man
    cog = TimezoneConverter(bot)
    await bot.add_cog(cog)
    configman = GuildConfig()
    configman.set_config_set("user")
    configman.add_setting("Fun", "Timezone Converter", "Enable or disable the timezone converter command")  # noqa: E501
    configman.add_option_bool(
        category_name="Fun",
        setting_name="Timezone Converter",
        name="Show timezone",
        button_title="Let users see your timezone",
        config_title="FUN",
        config_key="timezone-converter-enabled",
        description="Let users know your timezone and convert times between different timezones. Also shown in user info",  # noqa: E501
    )
