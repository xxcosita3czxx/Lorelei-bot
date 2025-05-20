# RECREATING THE WHOLE CONFIG SYSTEM FROM SCRATCH TO BE MORE MODULAR

import logging  # noqa: F401
import os

import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import gconfig, lang, uconfig
from utils.guildconfig import GuildConfig

__PRIORITY__ = 10

logger = logging.getLogger("guildconfig")

def category():
    pass

class DropdownView(discord.ui.View):
    def __init__(self, options):
        super().__init__()
        # Add the dropdown to the view
        class DynamicDropdown(discord.ui.Select):
            def __init__(self, options):
                # Create the dropdown options dynamically from the external list
                select_options = [
                    discord.SelectOption(label=option, value=option) for option in options  # noqa: E501
                ]
                logger.info(f"Options: {select_options}")  # noqa: E501
                if not select_options:
                    select_options.append(discord.SelectOption(label="No options available", value="none")) # noqa: E501
                super().__init__(
                    placeholder="Choose an option...",
                    options=select_options,
                )

            async def callback(self, interaction: discord.Interaction):
                # Handle the user's selection
                selected_option = self.values[0]
                logger.debug(f"Selected option: {selected_option}")

                embed = discord.Embed(
                    title="Selected Option",
                    description=f"You selected: {selected_option}",
                )
                await interaction.response.edit_message(embed=embed, view=None)  # type: ignore

        self.add_item(DynamicDropdown(options))


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
            self.description = "Config for server, PLEASE DO NOT USE YET"

        @app_commands.command(
            name="configure",
            description="Configure the bot",  # noqa: E501
        )
        async def configure(self,interaction:discord.Interaction):
            config_session = GuildConfig()  # noqa: F841
            embed = discord.Embed(
                title="Configuration Categories",
                description="Select a category to configure",
            )
            for category in config_session.Configs:
                embed.add_field(name=category, value=f"Configure {category}", inline=False)  # noqa: E501
            config_session = GuildConfig()  # noqa: F841
            categories = config_session.get_categories  # Assuming Configs is a dictionary  # noqa: E501
            await interaction.response.send_message(
                embed=embed,
                view=DropdownView(categories),
                ephemeral=True,
            )  # noqa: E501



        @app_commands.command(
            name="reset",
            description="Resets the config. NO TAKIES BACKSIES, AS IT GETS DELETED PERMANENTLY, BREAKS ANY VERIFY SYSTEM",  # noqa: E501
        )
        async def reset_config(
            self,
            interaction: discord.Interaction,
        ):
            try:
                os.remove(f"data/guilds/{interaction.guild.id}.toml") # type: ignore
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
                file = f"data/guilds/{str(interaction.guild.id)}.toml" # type: ignore
                await interaction.response.send_message(
                    content="Here is exported content that bot has saved. Remember that exports of message id dependent functions will not be ported over.",  # noqa: E501
                    file=file, # type: ignore
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
                if not interaction.data['attachments']: # type: ignore
                    await interaction.response.send_message(
                        content="No file uploaded. Please upload a config file.",
                        ephemeral=True,
                    )
                    return
                attachment = interaction.data['attachments'][0] # type: ignore
                file_content = await attachment.read()
                with open("data/guilds"+ str(interaction.guild.id) + ".toml", "w") as f:  # type: ignore # noqa: E501
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

async def setup(bot:commands.Bot):
    cog = _GuildConfigCommands(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.configure())
# Aint doing it yet and i will do mostly commands, as functionalities are needed more  # noqa: E501
