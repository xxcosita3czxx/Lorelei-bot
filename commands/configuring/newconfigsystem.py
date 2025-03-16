# RECREATING THE WHOLE CONFIG SYSTEM FROM SCRATCH TO BE MORE MODULAR

import logging  # noqa: F401
import os

import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import gconfig, lang, uconfig

__PRIORITY__ = 10

#TODO System will be able to still have commands like guildconfig export, import and reset  # noqa: E501
#TODO Yet it will have new option named guildconfig configure
#TODO Possibility of having display in help menu (gotta recreate that also)
#
# There will be command named "/guildconfig configure"
# in there will be options of categories that will be listed in embed with
# descriptions
# Inside those there will be options for commands
#
# The config system will work like this:
# config_session = GuildConfig(gconfig)
# configs = config_session.new_setting("class (for instance SECURITY)","name")
# configs.new_option("name","description","type (int, str bool....)")  # noqa: E501

def _ClassEmbed(title):
    return discord.Embed(
        title=title,
        description=f"What do you want to configure in category {title}",
    )
# Example usage:
# config_session = GuildConfig()
# security_category = config_session.new_category("SECURITY")
# setting = security_category.new_setting("max_login_attempts")
# setting.new_option("attempts", "Maximum number of login attempts", int)

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

        def new_option(self, option_name, description, option_type):
            self.category[self.name][option_name] = {
                "type": option_type,
                "description": description,
                "variable": None,
            }

class _GuildConfigCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.default_permissions(
        administrator=True,
    )
    class configure(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "newguildconfig"
            self.description = "Config for server"

        @app_commands.command(
            name="reset",
            description="Resets the config. NO TAKIES BACKSIES, AS IT GETS DELETED PERMANENTLY, BREAKS ANY VERIFY SYSTEM",  # noqa: E501
        )
        async def reset_config(
            self,
            interaction: discord.Interaction,
        ):
            try:
                os.remove(f"data/guilds/{interaction.guild.id}.toml")
                gconfig._load_all_configs()
                await interaction.response.send_message(
                    content=lang.get(uconfig.get(interaction.user.id,"APPEARANCE","language"),"Responds","config_reset"),
                    ephemeral=True,
                )
            except FileNotFoundError:
                await interaction.response.send_message(
                    content="No config generated yet! Try configuring the server",
                    ephemeral=True,
                )
            except PermissionError:
                await interaction.response.send_message(
                    content="Permission Error! Ensure I have permissions for the file. If you're an administrator using Lorelei-bot, report this to Cosita Development!",  # noqa: E501
                    ephemeral=True,
                )

        @app_commands.command(
            name="export",
            description="Exports config",  # noqa: E501
        )
        async def export(self,interaction:discord.Interaction):
            try:
                file = "data/guilds"+ str(interaction.guild.id) + ".toml"
                interaction.response.send_message(
                    content="Here is exported content that bot has saved. Remember that exports of message id dependent functions will not be ported over.",  # noqa: E501
                    file=file,
                    ephemeral=True,
                )
            except PermissionError:
                await interaction.response.send_message(
                    content="Permission Error! Ensure I have permissions for the file. If you're an administrator using Lorelei-bot, report this to Cosita Development!",  # noqa: E501
                    ephemeral=True,
                )
            except FileNotFoundError:
                await interaction.response.send_message(
                    content="No config generated yet! Try configuring the server",
                    ephemeral=True,
                )
        @app_commands.command(
            name="import",
            description="Imports config",  # noqa: E501
        )
        async def import_config(self,interaction:discord.Interaction):  # noqa: E501
            try:
                if not interaction.data['attachments']:
                    await interaction.response.send_message(
                        content="No file uploaded. Please upload a config file.",
                        ephemeral=True,
                    )
                    return
                attachment = interaction.data['attachments'][0]
                file_content = await attachment.read()
                with open("data/guilds"+ str(interaction.guild.id) + ".toml", "w") as f:  # noqa: E501
                    f.write(file_content)
                await interaction.response.send_message(
                    content="Config imported successfully.",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Error: {e}",
                    ephemeral=True,
                )
        @app_commands.command(
            name="configure",
            description="Configure the bot",  # noqa: E501
        )
        async def configure(self,interaction:discord.Interaction):
            config_session = GuildConfig()
            embed = discord.Embed(
                title="Configuration Categories",
                description="Select a category to configure",
            )
            for category in config_session.Configs:
                embed.add_field(name=category, value=f"Configure {category}", inline=False)  # noqa: E501
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot:commands.Bot):
#    cog = _GuildConfigCommands(bot)
#    await bot.add_cog(cog)
#    bot.tree.add_command(cog.configure())
    pass
# Aint doing it yet and i will do mostly commands, as functionalities are needed more  # noqa: E501
