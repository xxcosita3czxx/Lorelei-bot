import re

import discord
from discord import app_commands

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

discord_time = ["60s", "1m", "1h", "1d","1w"]  # Discord's time format for timeouts
discord_time_s = {"60s": 60, "1m": 60, "1h": 3600, "1d": 86400, "1w": 604800}  # Discord's time format for timeouts in seconds  # noqa: E501

class TimeConverter(app_commands.Transformer):

    async def transform(self, interaction: discord.Interaction, argument:str):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0

        for key, value in matches:

            try:
                time += time_dict[value] * float(key)

            except KeyError:
                raise app_commands.BadArgument(  # noqa: B904 # type: ignore
                    f"{value} is an invalid time key! h|m|s|d are valid arguments",
                )

            except ValueError:
                raise app_commands.BadArgument(f"{key} is not a number!")  # type: ignore # noqa: B904
        return int(time)
