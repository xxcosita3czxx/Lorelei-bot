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

    def add_setting(self, category_name, setting_name,description):
        if category_name not in self.categories:
            self.categories[category_name] = {}
        if setting_name in self.categories[category_name]:
            raise ValueError(f"Setting '{setting_name}' already exists in category '{category_name}'.")  # noqa: E501
        self.categories[category_name][setting_name] = {description: description}

    def add_option(self, category_name, setting_name, name, description, option_type, title, key):  # noqa: E501
        setting = self.get_setting(category_name, setting_name)
        if name in setting:
            raise ValueError(f"Option '{name}' already exists in setting '{setting_name}'.")  # noqa: E501
        setting[name] = {
            "type": option_type,
            "description": description,
            "title": title,
            "key": key,
        }

    def get_setting(self, category_name, setting_name):
        if category_name not in self.categories:
            raise ValueError(f"Category '{category_name}' does not exist.")
        if setting_name not in self.categories[category_name]:
            raise ValueError(f"Setting '{setting_name}' does not exist in category '{category_name}'.")  # noqa: E501
        return self.categories[category_name][setting_name]

    def get_categories(self):
        return list(self.categories.keys())

    def get_all_settings(self, category_name):
        if category_name not in self.categories:
            raise ValueError(f"Category '{category_name}' does not exist.")
        return list(self.categories[category_name].keys())

    def get_options(self, category_name, setting_name):
        setting = self.get_setting(category_name, setting_name)
        return list(setting.keys())

    def get_option(self, category_name, setting_name, option_name):
        setting = self.get_setting(category_name, setting_name)
        if option_name not in setting:
            raise ValueError(f"Option '{option_name}' does not exist in setting '{setting_name}'.")  # noqa: E501
        return setting[option_name]

    def search_setting(self, setting_name):
        for _, settings in self.categories.items():
            if setting_name in settings:
                return settings[setting_name]
        raise ValueError(f"Setting '{setting_name}' not found in any category.")
