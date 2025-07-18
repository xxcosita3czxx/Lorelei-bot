# RECREATING THE WHOLE CONFIG SYSTEM FROM SCRATCH TO BE MORE MODULAR

import logging  # noqa: F401
import os

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select

from utils.configmanager import gconfig, lang, uconfig, userlang
from utils.guildconfig import GuildConfig
from utils.timeconverter import discord_time_s

#TODO Fix text input trough modal
#TODO Somehow give a time button to specify time
#TODO Cleanup commands an modules so its better sorted in categories

__PRIORITY__ = 10

logger = logging.getLogger("guildconfig")

class SettingView(discord.ui.View):
    def __init__(self, settings, config_session: GuildConfig, category_name: str,cconfig):  # noqa: C901, E501
        super().__init__()

        class BoolOptionButton(discord.ui.Button):
            def __init__(self, option_name,config_title,config_key, value=True):  # noqa: E501
                label = f"{option_name}: {'True' if value else 'False'}"
                style = discord.ButtonStyle.success if value else discord.ButtonStyle.danger  # noqa: E501
                super().__init__(label=label, style=style)
                self.option_name = option_name
                self.value = value
                self.config_title = config_title
                self.config_key = config_key

            async def callback(self, interaction: discord.Interaction):
                self.value = not self.value
                config_id = interaction.user.id if cconfig is uconfig else interaction.guild.id  # type: ignore  # noqa: E501
                cconfig.set(
                    config_id,
                    self.config_title,
                    self.config_key,
                    self.value,  # type: ignore
                )  # type: ignore
                self.label = f"{self.option_name}: {'True' if self.value else 'False'}"  # noqa: E501
                self.style = discord.ButtonStyle.success if self.value else discord.ButtonStyle.danger  # noqa: E501
                await interaction.response.edit_message(view=self.view)
        class ListSelectMenu(Select):
            def __init__(self, interaction, name, config_title, config_key, options_list):  # noqa: E501
                options = [
                    discord.SelectOption(label=opt, value=opt) for opt in options_list  # noqa: E501
                ]
                super().__init__(
                    placeholder="Select option...",
                    options=options,
                    custom_id=f"list_select_{name}",
                )
                self.config_title = config_title
                self.config_key = config_key

            async def callback(self, interaction: discord.Interaction):
                selected_option = self.values[0]
                config_id = interaction.user.id if cconfig is uconfig else interaction.guild.id  # type: ignore  # noqa: E501
                cconfig.set(
                    config_id,
                    self.config_title,
                    self.config_key,
                    selected_option,  # type: ignore
                )
                await interaction.response.defer(ephemeral=True)
        class TimeSelectMenu(Select):
            def __init__(self, interaction, name, config_title, config_key):
                options = [
                    discord.SelectOption(label=opt, value=opt) for opt in discord_time_s  # noqa: E501
                ]
                super().__init__(
                    placeholder="Select time...",
                    options=options,
                    custom_id=f"time_select_{name}",
                )
                self.config_title = config_title
                self.config_key = config_key

            async def callback(self, interaction: discord.Interaction):
                selected_time = self.values[0]
                config_id = interaction.user.id if cconfig is uconfig else interaction.guild.id  # type: ignore # noqa: E501
                cconfig.set(
                    config_id,
                    self.config_title,
                    self.config_key,
                    discord_time_s[selected_time],  # type: ignore
                )  # type: ignore
        class TextModal(discord.ui.Modal):
            def __init__(self, title, placeholder, config_title, config_key):
                super().__init__(title=title)
                self.text_input = discord.ui.TextInput(
                    label=title,
                    placeholder=placeholder,
                    style=discord.TextStyle.paragraph,
                )
                self.add_item(self.text_input)
                self.config_title = config_title
                self.config_key = config_key

            async def on_submit(self, interaction: discord.Interaction):
                config_id = interaction.user.id if cconfig is uconfig else interaction.guild.id # type: ignore # noqa: E501
                cconfig.set(
                    config_id,
                    self.config_title,
                    self.config_key,
                    self.text_input.value,
                )
                await interaction.response.defer(ephemeral=True)
        class TextChannelSelectMenu(Select):
            def __init__(self, interaction, name, config_title, config_key):
                options = [
                    discord.SelectOption(label=channel.name, value=str(channel.id))
                    for channel in interaction.guild.channels if isinstance(channel, discord.TextChannel)  # noqa: E501
                ]
                super().__init__(
                    placeholder="Select channel...",
                    options=options,
                    custom_id=f"channel_select_{name}",
                )
                self.config_title = config_title
                self.config_key = config_key

            async def callback(self, interaction: discord.Interaction):
                selected_channel_id = int(self.values[0])
                config_id = interaction.user.id if cconfig is uconfig else interaction.guild.id  # type: ignore  # noqa: E501
                cconfig.set(
                    config_id,
                    self.config_title,
                    self.config_key,
                    selected_channel_id,  # type: ignore
                )
                # gconfig.save(interaction.guild.id, self.config_title, self.config_key, selected_channel_id)  # noqa: E501
                await interaction.response.defer(ephemeral=True)

        class CategorySelectMenu(Select):
            def __init__(self, interaction:discord.Interaction, name, config_title, config_key):  # noqa: E501
                options = [
                    discord.SelectOption(label=category.name, value=str(category.id))  # noqa: E501
                    for category in interaction.guild.categories if isinstance(category,discord.CategoryChannel) # type: ignore  # noqa: E501
                ]
                super().__init__(
                    placeholder="Select category...",
                    options=options,
                    custom_id=f"category_select_{name}",
                )
                self.config_title = config_title
                self.config_key = config_key

            async def callback(self, interaction: discord.Interaction):
                selected_category_id = int(self.values[0])
                config_id = interaction.user.id if cconfig is uconfig else interaction.guild.id  # type: ignore  # noqa: E501
                cconfig.set(
                    config_id,
                    self.config_title,
                    self.config_key,
                    selected_category_id,
                )
                await interaction.response.defer(ephemeral=True)

        class RoleSelectMenu(Select):
            def __init__(self, interaction, name, config_title, config_key):
                options = [
                    discord.SelectOption(label=role.name, value=str(role.id))
                    for role in interaction.guild.roles if role.name != "everyone"
                ]
                super().__init__(
                    placeholder="Select role...",
                    options=options,
                    custom_id=f"role_select_{name}",
                )
                self.config_title = config_title
                self.config_key = config_key

            async def callback(self, interaction: discord.Interaction):
                selected_role_id = int(self.values[0])
                config_id = interaction.user.id if cconfig is uconfig else interaction.guild.id  # type: ignore  # noqa: E501
                cconfig.set(
                    config_id,
                    self.config_title,
                    self.config_key,
                    selected_role_id,  # type: ignore
                )  # type: ignore
                # gconfig.save(interaction.guild.id, self.config_title, self.config_key, selected_role_id)  # noqa: E501
                await interaction.response.defer(ephemeral=True)
        class SettingDropdown(discord.ui.Select):
            def __init__(self, settings):
                select_options = [
                    discord.SelectOption(label=s, value=s) for s in settings
                ] or [discord.SelectOption(label="No settings available", value="none")]  # noqa: E501

                super().__init__(
                    placeholder="Choose a setting...",
                    options=select_options,
                )

            async def callback(self, interaction: discord.Interaction):  # noqa: C901
                selected = self.values[0]
                options = config_session.get_options(category_name, selected)
                embed = discord.Embed(
                    title=f"Options for {selected}",
                    description="Here are the options for this setting:" if options else lang.get(userlang(interaction.user.id),"Responds","no_options"),  # noqa: E501
                )
                view = discord.ui.View()
                for option in options:
                    option_data = config_session.get_option(category_name, selected, option)  # noqa: E501
                    desc = option_data.get("description", "No description")
                    conf_title = option_data.get("config_title", option)
                    conf_key = option_data.get("config_key", option)
                    opt_type = option_data.get("type", "str")
                    if opt_type == "bool":
                        # Get the current value from config
                        config_id = interaction.user.id if cconfig is uconfig else interaction.guild.id  # type: ignore  # noqa: E501
                        current_value = cconfig.get(config_id,conf_title, conf_key,False) # type: ignore  # noqa: E501
                        view.add_item(BoolOptionButton(option,config_title=conf_title,config_key=conf_key, value=current_value))  # noqa: E501
                    elif opt_type == "textchannel":
                        view.add_item(
                            TextChannelSelectMenu(interaction=interaction, name=option, config_title=conf_title, config_key=conf_key),  # noqa: E501
                        )
                    elif opt_type == "role":
                        view.add_item(
                            RoleSelectMenu(interaction=interaction, name=option, config_title=conf_title, config_key=conf_key),  # noqa: E501
                        )
                    elif opt_type == "text":
                        # Replace the button with one that opens a TextModal
                        async def button_callback(interaction, option=option, conf_title=conf_title, conf_key=conf_key):  # noqa: E501
                            modal = TextModal(
                                title=f"Set {option}",
                                placeholder=f"Enter value for {option}",
                                config_title=conf_title,
                                config_key=conf_key,
                            )
                            await interaction.response.send_modal(modal)
                        btn = discord.ui.Button(
                            label=option,
                            style=discord.ButtonStyle.primary,
                            custom_id=f"text_modal_{option}",
                        )
                        btn.callback = button_callback
                        view.add_item(btn)
                    elif opt_type == "category":
                        view.add_item(
                            CategorySelectMenu(interaction=interaction,name=option, config_title=conf_title,config_key=conf_key),  # noqa: E501
                        )
                    elif opt_type == "time":
                        view.add_item(
                            TimeSelectMenu(
                                interaction=interaction,
                                name=option,
                                config_title=conf_title,
                                config_key=conf_key,
                            ),  # noqa: E501
                        )
                    elif opt_type == "list":
                        options_list = option_data.get("options", [])
                        if options_list:
                            view.add_item(
                                ListSelectMenu(
                                    interaction=interaction,
                                    name=option,
                                    config_title=conf_title,
                                    config_key=conf_key,
                                    options_list=options_list,
                                ),
                            )
                        else:
                            embed.add_field(name=option, value="No options available", inline=False)  # noqa: E501
                    else:
                        embed.add_field(name=option, value=desc, inline=False)
                await interaction.response.edit_message(
                    embed=embed,
                    view=view if len(view.children) > 0 else None,
                )

        self.add_item(SettingDropdown(settings))


class CategoryView(discord.ui.View):
    def __init__(self, options, config_session: GuildConfig, config_manager):
        super().__init__()

        class CategoryDropdown(discord.ui.Select):
            def __init__(self, options):
                select_options = [
                    discord.SelectOption(label=option, value=option) for option in options  # noqa: E501
                ] or [discord.SelectOption(label="No options available", value="none")]  # noqa: E501
                super().__init__(
                    placeholder="Choose a category...",
                    options=select_options,
                )


            async def callback(self, interaction: discord.Interaction):
                selected_category = self.values[0]
                logger.debug(f"Selected category: {selected_category}")

                settings = config_session.Configs.get(selected_category, {}).keys()
                if not settings:
                    settings = ["No settings available"]

                embed = discord.Embed(
                    title=f"Settings in {selected_category}",
                    description="Choose a setting to modify",
                )
                for setting in settings:
                    embed.add_field(name=setting, value="Modify this setting", inline=False)  # noqa: E501
                logger.debug("CAT_VIEW: "+str(config_manager))
                await interaction.response.edit_message(
                    embed=embed,
                    view=SettingView(settings, config_session, selected_category, config_manager),  # noqa: E501
                )

        self.add_item(CategoryDropdown(options))


class GuildConfigCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.default_permissions(
        administrator=True,
    )
    class configure(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "guildconfig"
            self.description = "Config for server"

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
            logger.debug(config_session.Configs)
            for category in config_session.Configs:
                embed.add_field(name=category, value=f"Configure {category}", inline=False)  # noqa: E501
            categories = config_session.get_categories()  # Assuming Configs is a dictionary  # noqa: E501
            await interaction.response.send_message(
                embed=embed,
                view=CategoryView(categories, config_session, config_manager=gconfig),  # noqa: E501
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
            finally:
                gconfig._load_all_configs()

async def setup(bot:commands.Bot):
    cog = GuildConfigCommands(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.configure())
    configman = GuildConfig()
    configman.add_setting("Color", "System", "Configure color for bot responses")
    configman.add_setting("Color", "Punishments", "Color for Bans, Warns or any punishments that will come to your dms")  # noqa: E501
    configman.add_setting("System", "Show system messages","Allow people to show system messages in chat (Administrators automaticaly can override this)")  # noqa: E501

# Aint doing it yet and i will do mostly commands, as functionalities are needed more  # noqa: E501
