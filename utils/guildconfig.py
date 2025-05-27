import logging

logger = logging.getLogger("guildconfig-manager")

class GuildConfig:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GuildConfig, cls).__new__(cls)  # noqa: UP008
            logger.info("GuildConfig initialized")
        return cls._instance

    def __init__(self):
        if not self.__class__._initialized:
            self.categories = {}
            self.Configs = self.categories  # Backward compatibility
            self.__class__._initialized = True

    def add_setting(self, category_name, setting_name, description):
        if category_name not in self.categories:
            self.categories[category_name] = {}
        # Overwrite the setting and reset options if it already exists
        self.categories[category_name][setting_name] = {
            "options": {},
            "description": description,
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
        """
        Add an option to a setting.
        Args:
            category_name: str
            setting_name: str
            name: str (option name)
            option_type: str (e.g. 'bool', 'int', 'str')
            button_title: str (title for UI button)
            config_title: str (title for config storage)
            config_key: str (key for config storage)
            description: str (description for UI)
        """
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
