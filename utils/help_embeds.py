from discord import Embed

help_user = [
    Embed(
        title="/userconfig appearance color",
        description="Usage: color(string): Color that will be used, hex or Provided colors in autocomplete.", # noqa: E501
    ),
    Embed(
        title="/userconfig appearance language",
        description="Usage: language(string): Language that will bot respond to you. Use only autocomplete ones as they are linked to language files", # noqa: E501
    ),
]
help_admin = [
    Embed(
        title="/kick",
        description="Usage: member(Discord Member): Member to kick, reason(string): Reason why", # noqa: E501
    ),
    Embed(
        title="/ban",
        description="Usage: member(Discord Member): Member to ban, reason(string): Reason why, time(Time): Time to ban for (1m, 5d, 6w etc..)", # noqa: E501
    ),
    Embed(
        title="/unban",
        description="Usage: member(Discord Member): Member to unban, reason(string): Reason why", # noqa: E501
    ),
]
