# RECREATING THE WHOLE CONFIG SYSTEM FROM SCRATCH TO BE MORE MODULAR

import logging  # noqa: F401
import os

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select

from utils.configmanager import gconfig, lang, uconfig, userlang
from utils.guildconfig import GuildConfig
from utils.timeconverter import discord_time_h, discord_time_l

#TODO Add nsfw tag to exclude nsfw from safe channels

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
        class TimeSelectMenuLow(Select):
            def __init__(self, interaction, name, config_title, config_key):  # noqa: E501
                options = [
                        discord.SelectOption(label=opt, value=opt) for opt in discord_time_l  # noqa: E501
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
                    discord_time_l[selected_time],  # type: ignore
                )  # type: ignore
                await interaction.response.defer(ephemeral=True)
        class TimeSelectMenuHigh(Select):
            def __init__(self, interaction, name, config_title, config_key):  # noqa: E501
                options = [
                        discord.SelectOption(label=opt, value=opt) for opt in discord_time_h  # noqa: E501
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
                    discord_time_h[selected_time],  # type: ignore
                )  # type: ignore
                await interaction.response.defer(ephemeral=True)

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
                # Filter settings for NSFW logic
                filtered_settings = []
                for s in settings:
                    # Get setting data from config_session
                    setting_data = config_session.Configs.get(category_name, {}).get(s, {})  # noqa: E501
                    nsfw = setting_data.get("nsfw", False)
                    # If nsfw is True, only show in nsfw channels
                    # If interaction is not available, show all
                    filtered_settings.append((s, nsfw))
                select_options = []
                # If interaction is available, check channel nsfw status
                def is_nsfw_channel(interaction):
                    try:
                        return hasattr(interaction.channel, "is_nsfw") and interaction.channel.is_nsfw()  # noqa: E501
                    except Exception:
                        return False
                # Only show settings with nsfw=True in nsfw channels
                # Show all others everywhere
                for s, nsfw in filtered_settings:
                    # If nsfw True, only show if channel is nsfw
                    if nsfw:
                        select_options.append(discord.SelectOption(label=s, value=s))  # noqa: E501
                    else:
                        select_options.append(discord.SelectOption(label=s, value=s))  # noqa: E501
                if not select_options:
                    select_options = [discord.SelectOption(label="No settings available", value="none")]  # noqa: E501
                super().__init__(
                    placeholder="Choose a setting...",
                    options=select_options,
                )

            async def callback(self, interaction: discord.Interaction):  # noqa: C901
                # Filter settings for NSFW logic
                filtered_settings = []
                for s in settings:
                    setting_data = config_session.Configs.get(category_name, {}).get(s, {})  # noqa: E501
                    nsfw = setting_data.get("nsfw", False)
                    filtered_settings.append((s, nsfw))
                # Only show settings with nsfw=True in nsfw channels
                # Show all others everywhere
                is_nsfw = hasattr(interaction.channel, "is_nsfw") and interaction.channel.is_nsfw()  # noqa: E501
                available_settings = [s for s, nsfw in filtered_settings if not nsfw or is_nsfw]  # noqa: E501
                selected = self.values[0]
                if selected not in available_settings:
                    await interaction.response.send_message(content="This setting is only available in NSFW channels.", ephemeral=True)  # noqa: E501
                    return
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

                    embed.add_field(
                        name=option,
                        value=desc,
                        inline=False,
                    )

                    if opt_type == "bool":
                        config_id = interaction.user.id if cconfig is uconfig else interaction.guild.id  # noqa: E501
                        current_value = cconfig.get(config_id, conf_title, conf_key, False)  # noqa: E501
                        view.add_item(BoolOptionButton(option, config_title=conf_title, config_key=conf_key, value=current_value))  # noqa: E501
                    elif opt_type == "textchannel":
                        view.add_item(
                            TextChannelSelectMenu(interaction=interaction, name=option, config_title=conf_title, config_key=conf_key),  # noqa: E501
                        )
                    elif opt_type == "role":
                        view.add_item(
                            RoleSelectMenu(interaction=interaction, name=option, config_title=conf_title, config_key=conf_key),  # noqa: E501
                        )
                    elif opt_type == "text":
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
                            CategorySelectMenu(interaction=interaction, name=option, config_title=conf_title, config_key=conf_key),  # noqa: E501
                        )
                    elif opt_type == "time_low":
                        view.add_item(
                            TimeSelectMenuLow(
                                interaction=interaction,
                                name=option,
                                config_title=conf_title,
                                config_key=conf_key,
                            ),
                        )
                    elif opt_type == "time_high":
                        view.add_item(
                            TimeSelectMenuHigh(
                                interaction=interaction,
                                name=option,
                                config_title=conf_title,
                                config_key=conf_key,
                            ),
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
    def __init__(self, options, config_session: GuildConfig, config_manager):  # noqa: C901
        super().__init__()

        # Filter out categories with no visible settings for this channel
        filtered_options = []
        is_nsfw = False
        # Try to get channel from config_manager if possible (for initial filter)
        if hasattr(config_manager, 'channel'):
            is_nsfw = hasattr(config_manager.channel, "is_nsfw") and config_manager.channel.is_nsfw()  # noqa: E501
        for option in options:
            all_settings = list(config_session.Configs.get(option, {}).keys())
            visible_settings = []
            for s in all_settings:
                setting_data = config_session.Configs.get(option, {}).get(s, {})
                nsfw = setting_data.get("nsfw", False)
                if nsfw and not is_nsfw:
                    continue
                visible_settings.append(s)
            if visible_settings:
                filtered_options.append(option)

        if not filtered_options:
            # No categories to show, do not add dropdown
            return

        class CategoryDropdown(discord.ui.Select):
            def __init__(self, options):
                select_options = [
                    discord.SelectOption(label=option, value=option) for option in options  # noqa: E501
                ]
                super().__init__(
                    placeholder="Choose a category...",
                    options=select_options,
                )

            async def callback(self, interaction: discord.Interaction):
                selected_category = self.values[0]
                logger.debug(f"Selected category: {selected_category}")

                # Get all settings for the category
                all_settings = list(config_session.Configs.get(selected_category, {}).keys())  # noqa: E501
                is_nsfw = hasattr(interaction.channel, "is_nsfw") and interaction.channel.is_nsfw()  # noqa: E501
                filtered_settings = []
                for s in all_settings:
                    setting_data = config_session.Configs.get(selected_category, {}).get(s, {})  # noqa: E501
                    nsfw = setting_data.get("nsfw", False)
                    if nsfw and not is_nsfw:
                        continue
                    filtered_settings.append(s)
                if not filtered_settings:
                    # If no settings, do not show the category at all
                    await interaction.response.send_message(
                        content="No settings available in this category for this channel.",  # noqa: E501
                        ephemeral=True,
                    )
                    return

                embed = discord.Embed(
                    title=f"Settings in {selected_category}",
                    description="Choose a setting to modify",
                )
                for setting in filtered_settings:
                    embed.add_field(name=setting, value="Modify this setting", inline=False)  # noqa: E501
                logger.debug("CAT_VIEW: "+str(config_manager))
                await interaction.response.edit_message(
                    embed=embed,
                    view=SettingView(filtered_settings, config_session, selected_category, config_manager),  # noqa: E501
                )

        self.add_item(CategoryDropdown(filtered_options))


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
            visible_categories = []
            for category, settings_dict in config_session.Configs.items():
                # Filter out settings that are nsfw in non-nsfw channels
                is_nsfw = hasattr(interaction.channel, "is_nsfw") and interaction.channel.is_nsfw()  # noqa: E501
                visible_settings = [
                    s for s, data in settings_dict.items()
                    if not data.get("nsfw", False) or is_nsfw
                ]
                if visible_settings:
                    embed.add_field(name=category, value=f"Configure {category}", inline=False)  # noqa: E501
                    visible_categories.append(category)
            if not visible_categories:
                embed.description = "No categories available for this channel."
            await interaction.response.send_message(
                embed=embed,
                view=CategoryView(visible_categories, config_session, config_manager=gconfig),  # noqa: E501
                ephemeral=True,
            )

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
