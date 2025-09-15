import logging

import discord

logger = logging.getLogger("guildconfig-manager")

class GuildConfig:
    # Shared across all instances
    _config_sets = {"default": {}}

    def __init__(self):
        self.config_set = "default"  # Each instance tracks its own active set

    @property
    def categories(self):
        return self._config_sets[self.config_set]

    @property
    def Configs(self):
        return self.categories  # Backward compatibility

    def set_config_set(self, name: str = "default"):
        """Switch to a different config set. If it doesn't exist, create it."""
        if name not in self._config_sets:
            self._config_sets[name] = {}
        self.config_set = name

    def get_config_set(self):
        return self.config_set

    def add_setting(self, category_name, setting_name, description, nsfw=False):
        if category_name not in self.categories:
            self.categories[category_name] = {}
        # Overwrite the setting and reset options if it already exists
        self.categories[category_name][setting_name] = {
            "options": {},
            "description": description,
            "nsfw":nsfw
        }

    def add_custom_setting(self,category_name,setting_name,embed,description,nsfw=False):
        if category_name not in self.categories:
            self.categories[category_name] = {}
        if embed is None or embed is not isinstance(embed,discord.Embed):
            raise AttributeError("add_custom_setting: embed should be of instance discord.Embed")
        # Overwrite the setting and reset options if it already exists
        self.categories[category_name][setting_name] = {
            "embed":embed,
            "description": description,
            "nsfw":nsfw
        }

    def add_option_bool(
        self,
        category_name,
        setting_name,
        name,
        button_title,
        config_title,
        config_key,
        description,
    ):
        setting = self.get_setting(category_name, setting_name)
        options = setting["options"]
        if name in options:
            raise ValueError(
                f"Option '{name}' already exists in setting "
                f"'{setting_name}'.",
            )
        options[name] = {
            "type": "bool",
            "button_title": button_title,
            "config_title": config_title,
            "config_key": config_key,
            "description": description,
        }

    def add_option_textchannel(
        self,
        category_name,
        setting_name,
        name,
        config_title,
        config_key,
        description,
    ):
        setting = self.get_setting(category_name, setting_name)
        options = setting["options"]
        if name in options:
            raise ValueError(
                f"Option '{name}' already exists in setting '{setting_name}'.",
            )
        options[name] = {
            "type": "textchannel",
            "config_title": config_title,
            "config_key": config_key,
            "description": description,
        }

    def add_option_role(
        self,
        category_name,
        setting_name,
        name,
        config_title,
        config_key,
        description,
    ):
        setting = self.get_setting(category_name, setting_name)
        options = setting["options"]
        if name in options:
            raise ValueError(
                f"Option '{name}' already exists in setting '{setting_name}'.",
            )
        options[name] = {
            "type": "role",
            "config_title": config_title,
            "config_key": config_key,
            "description": description,
        }
    def add_option_list(
        self,
        category_name,
        setting_name,
        name,
        options_list,
        config_title,
        config_key,
        description,
    ):
        setting = self.get_setting(category_name, setting_name)
        options = setting["options"]
        if name in options:
            raise ValueError(
                f"Option '{name}' already exists in setting '{setting_name}'.",
            )
        options[name] = {
            "type": "list",
            "options": options_list,
            "config_title": config_title,
            "config_key": config_key,
            "description": description,
        }
    def add_option_text(
        self,
        category_name,
        setting_name,
        name,
        config_title,
        config_key,
        description,
    ):
        setting = self.get_setting(category_name, setting_name)
        options = setting["options"]
        if name in options:
            raise ValueError(
                f"Option '{name}' already exists in setting '{setting_name}'.",
            )
        options[name] = {
            "type": "text",
            "config_title": config_title,
            "config_key": config_key,
            "description": description,
        }
    def add_option_time_low(
        self,
        category_name,
        setting_name,
        name,
        config_title,
        config_key,
        description,
    ):
        """Time usually used for punishments, from 1 minute to 1 week."""
        setting = self.get_setting(category_name, setting_name)
        options = setting["options"]
        if name in options:
            raise ValueError(
                f"Option '{name}' already exists in setting '{setting_name}'.",
            )
        options[name] = {
            "type": "time",
            "config_title": config_title,
            "config_key": config_key,
            "description": description,
        }

    def add_option_time_high(
        self,
        category_name,
        setting_name,
        name,
        config_title,
        config_key,
        description,
    ):
        """Time usually used time checks, from 1 week to 1 year."""
        setting = self.get_setting(category_name, setting_name)
        options = setting["options"]
        if name in options:
            raise ValueError(
                f"Option '{name}' already exists in setting '{setting_name}'.",
            )
        options[name] = {
            "type": "time",
            "config_title": config_title,
            "config_key": config_key,
            "description": description,
        }
    def get_setting(self, category_name, setting_name):
        if category_name not in self.categories:
            raise ValueError(f"Category '{category_name}' does not exist.")
        if setting_name not in self.categories[category_name]:
            raise ValueError(
                f"Setting '{setting_name}' does not exist in category "
                f"'{category_name}'.",
            )
        return self.categories[category_name][setting_name]

    def get_categories(self):
        return list(self.categories.keys())

    def get_all_settings(self, category_name):
        if category_name not in self.categories:
            raise ValueError(f"Category '{category_name}' does not exist.")
        return list(self.categories[category_name].keys())

    def get_options(self, category_name, setting_name):
        setting = self.get_setting(category_name, setting_name)
        return list(setting["options"].keys())

    def get_option(self, category_name, setting_name, option_name):
        setting = self.get_setting(category_name, setting_name)
        options = setting["options"]
        if option_name not in options:
            raise ValueError(
                f"Option '{option_name}' does not exist in setting "
                f"'{setting_name}'.",
            )
        return options[option_name]

    def search_setting(self, setting_name):
        for _, settings in self.categories.items():
            if setting_name in settings:
                return settings[setting_name]
        raise ValueError(f"Setting '{setting_name}' not found in any category.")
