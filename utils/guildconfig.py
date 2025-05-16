# There will be command named "/guildconfig configure"
# in there will be options of categories that will be listed in embed with
# descriptions
# Inside those there will be options for commands
#
# The config system will work like this:
# config_session = GuildConfig(gconfig)
# configs = config_session.new_setting("class (for instance SECURITY)","name")
# configs.new_option("name","description","type (int, str bool....)")  # noqa: E501


class GuildConfig:
    _instance = None  # Singleton instance

    def __init__(self):
        self.Configs = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def new_category(self, name):
        if name not in self.Configs:
            self.Configs[name] = {}
        return self.Category(name, self.Configs)

    class Category:
        def __init__(self, name, configs):
            self.name = name
            self.configs = configs

        def new_setting(self, name):
            return GuildConfig.Setting(name, self.configs[self.name])

    class Setting:
        def __init__(self, name, category):
            self.name = name
            self.category = category
            self.category[name] = {}
        # type should be str, bool or list
        def new_option(self, option_name, description, option_type):
            self.category[self.name][option_name] = {
                "type": option_type,
                "description": description,
                "variable": None,
            }

