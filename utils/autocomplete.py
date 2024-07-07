import logging
import os
from typing import List

import discord
import requests
from discord import app_commands


async def fetch_tags(query):
    headers = {
        'User-Agent': 'Lorelei-bot/1.0 (by cosita3cz on e621)',
    }
    response = requests.get(f'https://e621.net/tags.json?search[name_matches]={query}*&search[order]=count&limit=20',timeout=60,headers=headers)
    if response.status_code == 200:  # noqa: PLR2004
        return [tag['name'] for tag in response.json()]
    return []

async def autocomplete_color(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:  # noqa: E501
    colors = ['Blurple', 'Red', 'Green', 'Blue', 'Yellow',"Purple","White"]
    return [app_commands.Choice(name=color, value=color) for color in colors if current.lower() in color.lower()]  # noqa: E501

async def autocomplete_verify_modes(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:  # noqa: E501
    colors = ["captcha","button","emoji"]
    return [app_commands.Choice(name=color, value=color) for color in colors if current.lower() in color.lower()]  # noqa: E501

async def autocomplete_lang(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:  # noqa: E501
    directory = "data/lang"
    def get_toml_files(directory: str) -> List[str]:
        toml_files = []
        for f in os.listdir(directory):
            if f.endswith('.toml'):
                filename_without_extension = f[:-5]
                toml_files.append(filename_without_extension)
        return toml_files
    toml_files = get_toml_files(directory)
    return [
        app_commands.Choice(
            name=language,
            value=language,
        ) for language in toml_files if current.lower() in language.lower()
    ]  # noqa: E501

async def autocomplete_tags(interaction: discord.Interaction, current: str):
    try:
        *previous_words, last_word = current.split() if current else [""]
        tags = await fetch_tags(last_word)
        choices = []

        for tag in tags:
            if last_word.lower() in tag.lower():
                full_completion = " ".join(previous_words + [tag])
                choices.append(
                    app_commands.Choice(
                        name=full_completion,
                        value=full_completion,
                    ),
                )
        return choices
    except Exception as e:
        logging.warning(f"Autocomplete tags failed! {e}")
        return [ "autocomplete failed!" ]

#    if current == "":
#        tags = await fetch_tags(current)
#    else:
#        last_word = current.split()[-1]
#        tags = await fetch_tags(last_word)
#    return [
#        app_commands.Choice(
#            name=tag,
#            value=tag,
#        ) for tag in tags if last_word.lower() in tag.lower()
#    ]
