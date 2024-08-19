import re
from functools import lru_cache

import discord
from discord import app_commands

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

@lru_cache
async def transformer(argument):
    args = argument.lower()
    matches = re.findall(time_regex, args)
    time = 0

    for key, value in matches:

        try:
            time += time_dict[value] * float(key)

        except KeyError:
            raise app_commands.BadArgument(  # noqa: B904
                f"{value} is an invalid time key! h|m|s|d are valid arguments",
            )

        except ValueError:
            raise app_commands.BadArgument(f"{key} is not a number!")  # noqa: B904
    return round(time)

class TimeConverter(app_commands.Transformer):

    async def transform(self,interaction:discord.Interaction,argument:str) -> int:  # noqa: E501, ANN101
        transformer(argument)
