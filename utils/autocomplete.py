import logging
import os
from typing import List  # noqa: UP035

import discord
import requests
from discord import app_commands

from utils.dices import dices
from utils.helpmanager import HelpManager

colors = {
        "Blurple": "#5865F2",
        "Red": "#ED4245",
        "Green": "#57F287",
        "Blue": "#0096CF",  # Adding blue just in case
        "Yellow": "#FEE75C",
        "Purple": "#5865F2",  # Discord's purple is often Blurple
        "White": "#FFFFFF",
    }

logger = logging.getLogger("autocomplete")

async def fetch_tags(query):
    headers = {
        'User-Agent': 'Lorelei-bot/1.0 (by cosita3cz on e621)',
    }
    response = requests.get(f'https://e621.net/tags.json?search[name_matches]={query}*&search[order]=count&limit=20',timeout=60,headers=headers)
    if response.status_code == 200:  # noqa: PLR2004
        return [tag['name'] for tag in response.json()]
    return []


async def autocomplete_color(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:  # noqa: E501, UP006
    global colors

    return [
        app_commands.Choice(name=f"{color} ({hex_value})", value=hex_value)
        for color, hex_value in colors.items()
        if current.lower() in hex_value.lower() or current.lower() in color.lower()
    ]
async def autocomplete_dice_modes(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:  # noqa: E501, UP006
    colors = dices.keys()
    return [app_commands.Choice(name=color, value=color) for color in colors if current.lower() in color.lower()]  # noqa: E501

async def autocomplete_verify_modes(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:  # noqa: E501, UP006
    colors = ["captcha","button","emoji","teams"]
    return [app_commands.Choice(name=color, value=color) for color in colors if current.lower() in color.lower()]  # noqa: E501

async def autocomplete_lang(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:  # noqa: E501, UP006
    directory = "data/lang"
    def get_toml_files(directory: str) -> List[str]:  # noqa: UP006
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
        # Split current input into words
        *previous_words, last_word = current.split() if current else [""]

        # Handle the dash in last_word
        last_word_cleaned = last_word.lstrip('-').strip()

        # Fetch tags based on cleaned last_word
        tags = await fetch_tags(last_word_cleaned)
        choices = []

        for tag in tags:
            # Check if cleaned last_word is in the tag
            if last_word_cleaned.lower() in tag.lower():
                # Re-include the dash if it was part of the original input
                if last_word.startswith('-'):
                    full_completion = " ".join(previous_words + ['-' + tag])
                else:
                    full_completion = " ".join(previous_words + [tag])

                choices.append(
                    app_commands.Choice(
                        name=full_completion,
                        value=full_completion,
                    ),
                )

        return choices
    except Exception as e:
        logger.warning(f"Autocomplete tags failed! {e}")
        return [
            app_commands.Choice(name="autocomplete failed!", value="autocomplete failed!"),  # noqa: E501
            app_commands.Choice(name="autocomplete failed!", value="autocomplete failed!"),  # noqa: E501
            app_commands.Choice(name="autocomplete failed!", value="autocomplete failed!"),  # noqa: E501
        ]

async def autocomplete_invites(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:  # noqa: E501, UP006
    guild = interaction.guild
    if guild is None:
        return []

    invites = await guild.invites()
    invite_codes = [invite.code for invite in invites]

    return [
        app_commands.Choice(name=f"discord.gg/{code}", value=f"discord.gg/{code}")
        for code in invite_codes
        if current.lower() in code.lower()
    ]

async def autocomplete_help_groups(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:  # noqa: E501, UP006
    help_manager = HelpManager()
    groups = help_manager.list_groups()
    return [
        app_commands.Choice(name=group, value=group)
        for group in groups
        if current.lower() in group.lower()
    ]  # noqa: E501

async def autocomplete_help_commands(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:  # noqa: E501, UP006
    group = interaction.namespace.group
    if group is None or not isinstance(group, str):
        help_manager = HelpManager()
        all_commands = help_manager.list_all_commands()
        if group is None or not isinstance(group, str):
            help_manager = HelpManager()
            all_commands = help_manager.list_all_commands()
            unique_commands = {(command.split()[0], group) for command, group in all_commands if isinstance(command, str)}  # noqa: E501
            return [
                app_commands.Choice(name=f"{command} (Group: {group})", value=command)  # noqa: E501
                for command, group in unique_commands
                if current.lower() in command.lower()
            ]
    help_manager = HelpManager()
    commands = help_manager.list_commands(group)
    return [
        app_commands.Choice(name=command, value=command)
        for command in commands
        if isinstance(command, str) and current.lower() in command.lower()
    ]  # noqa: E501

async def autocomplete_help_pages(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:  # noqa: E501, UP006
    group = interaction.namespace.group
    command = interaction.namespace.command
    if group is None or command is None:
        return [app_commands.Choice(name="No command selected", value="No command selected")]  # noqa: E501
    help_manager = HelpManager()
    pages = help_manager.list_pages(group, command)
    return [
        app_commands.Choice(name=str(page), value=str(page))
        for page in pages
        if current.lower() in str(page).lower()
    ]  # noqa: E501
