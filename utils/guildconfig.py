import logging
# There will be command named "/guildconfig configure"
# in there will be options of categories that will be listed in embed with
# descriptions
# Inside those there will be options for commands
#
# The config system will work like this:
# config_session = GuildConfig(gconfig)
# configs = config_session.new_setting("class (for instance SECURITY)","name")
# configs.new_option("name","description","type (int, str bool....)")  # noqa: E501

logger = logging.getLogger("guildconfig-manager")

class Setting:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.options = {}

    def add_option(self, name, description, option_type, title, key):
        if name in self.options:
            raise ValueError(f"Option '{name}' already exists in setting '{self.name}'.")  # noqa: E501
        self.options[name] = {
            "type": option_type,
            "description": description,
            "title": title,
            "key": key,
        }


class GuildConfig:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GuildConfig,cls).__new__(cls) # noqa: UP008
            logger.info("GuildConfig initialized")
        return cls._instance

    def __init__(self):
        if not self.__class__._initialized:
            self.categories = {}
            self.Configs = self.categories  # Backward compatibility
            self.__class__._initialized = True

    def add_setting(self, category_name, setting_name, description):
        if category_name not in self.categories:
            self.categories[category_name] = {
                "description": "",
                "settings": {},
            }
        if setting_name in self.categories[category_name]["settings"]:
            self.categories[category_name]["settings"][setting_name] = {}
        setting = Setting(setting_name, description)
        self.categories[category_name]["settings"][setting_name] = setting
        return setting

    def get_setting(self, category_name, setting_name):
        if category_name not in self.categories:
            raise ValueError(f"Category '{category_name}' does not exist.")
        if setting_name not in self.categories[category_name]["settings"]:
            raise ValueError(f"Setting '{setting_name}' does not exist in category '{category_name}'.")  # noqa: E501
        return self.categories[category_name]["settings"][setting_name]

    def get_categories(self):
        """Retrieve all categories in the guild configuration."""
        return list(self.categories.keys())

    def get_all_settings(self, category_name):
        """Retrieve all settings in a specific category."""
        if category_name not in self.categories:
            raise ValueError(f"Category '{category_name}' does not exist.")
        return list(self.categories[category_name]["settings"].keys())

    def get_options(self, category_name, setting_name):
        """Retrieve all options in a specific setting."""
        setting = self.get_setting(category_name, setting_name)
        return list(setting.options.keys())

    def get_option(self, category_name, setting_name, option_name):
        """Retrieve details of a specific option."""
        setting = self.get_setting(category_name, setting_name)
        if option_name not in setting.options:
            raise ValueError(f"Option '{option_name}' does not exist in setting '{setting_name}'.")  # noqa: E501
        return setting.options[option_name]

    def search_setting(self, setting_name):
        """Search for a setting across all categories and return the setting object."""  # noqa: E501
        for _, category_data in self.categories.items():
            if setting_name in category_data["settings"]:
                return category_data["settings"][setting_name]
        raise ValueError(f"Setting '{setting_name}' not found in any category.")
