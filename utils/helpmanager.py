import logging

import discord

logger = logging.getLogger("helpmanager")


class HelpManager:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.help_pages = {}  # Initialize the dictionary once
            logger.info("HelpManager initialized.")
        return cls._instance

    class new_help:
        def __init__(self, group_name: str, command_name: str, description: str):  # noqa: E501
            self.group_name = group_name
            self.command_name = command_name
            self.description = description
            self._instance = HelpManager._instance

        def set_help_page(self, page: int, title: str, description: str):  # noqa: E501
            """Adds a help page (embed) for a command inside a group."""
            if self.group_name not in HelpManager._instance.help_pages:
                self._instance.help_pages[self.group_name] = {}
            if self.command_name not in self._instance.help_pages[self.group_name]:  # noqa: E501
                self._instance.help_pages[self.group_name][self.command_name] = {}  # noqa: E501
            self._instance.help_pages[self.group_name][self.command_name][page] = {  # noqa: E501
                "title": title,
                "description": description,
            }

    def get_help_page(self, group_name: str, command_name: str, page:int) -> discord.Embed:  # noqa: E501
        """Retrieves the help embed for a command inside a group."""
        if group_name not in self.help_pages:
            raise ValueError(f"Group '{group_name}' does not exist.")
        if command_name not in self.help_pages[group_name]:
            raise ValueError(f"Command '{command_name}' does not exist in group '{group_name}'.")  # noqa: E501
        if page not in self.help_pages[group_name][command_name]:
            raise ValueError(f"Page '{page}' does not exist in command '{command_name}'.")  # noqa: E501
        return self.help_pages[group_name][command_name][page]

    def list_groups(self) -> list:
        """Returns a list of all help groups."""
        return list(self.help_pages.keys())

    def list_commands(self, group_name: str) -> list:
        """Lists all commands in a given group."""
        if group_name not in self.help_pages:
            raise ValueError(f"Group '{group_name}' does not exist.")
        return list(self.help_pages[group_name].keys())

    def list_all_commands(self) -> list:
        """Returns a list of all groups with their commands as strings."""
        all_commands = []
        for group, commands in self.help_pages.items():
            for command in commands:
                all_commands.append(f"Group: {group}, Command: {command}")
        return all_commands

    def list_pages(self, group_name: str,command_name: str) -> list:
        """Lists all commands in a given group."""
        if group_name not in self.help_pages:
            raise ValueError(f"Group '{group_name}' does not exist.")
        if command_name not in self.help_pages[group_name]:
            raise ValueError(f"Group '{command_name}' does not exist.")
        return list(self.help_pages[group_name][command_name].keys())
