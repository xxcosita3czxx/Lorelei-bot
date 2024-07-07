import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_color, autocomplete_lang
from utils.configmanager import gconfig, lang, uconfig


class GuildConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.default_permissions(administrator=True)
    class configure_sec(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "security"
            self.description = "Security configurations"

        @app_commands.command(
            name="anti-invite",
            description="No invites in the halls",
        )
        async def anti_invites(
            self,
            interaction: discord.Interaction,
            value: bool,
        ):
            try:
                gconfig.set(
                    id=interaction.guild_id,
                    title="SECURITY",
                    key="anti-invite",
                    value=value,
                )
                await interaction.response.send_message(
                    content=f"Set value {str(value)}",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Failed configuring anti-invites: {e}",
                )

        @app_commands.command(
            name="anti-links",
            description="No links in the halls",
        )
        async def anti_links(
            self,
            interaction: discord.Interaction,
            value: bool,
        ):
            try:
                gconfig.set(
                    id=interaction.guild_id,
                    title="SECURITY",
                    key="anti-links",
                    value=value,
                )
                await interaction.response.send_message(
                    content=f"Set value {str(value)}",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Failed configuring anti-links: {e}",
                )

    @app_commands.default_permissions(administrator=True)
    class configure_appear(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "appearance"
            self.description = "Appearance of bot on your server"

        @app_commands.command(
            name="color",
            description="Changes default color of embeds.",
        )
        @app_commands.describe(
            color="The color to set",
        )
        @app_commands.autocomplete(
            color=autocomplete_color,
        )
        async def config_color_guild(
            self,
            interaction: discord.Interaction,
            color: str,
        ):
            try:
                gconfig.set(
                    id=interaction.guild_id,
                    title="APPEARANCE",
                    key="color",
                    value=color,
                )
                await interaction.response.send_message(
                    content=f"Set value {str(color)}",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )

        @app_commands.command(
            name="language",
            description="Set server default language",
        )
        @app_commands.describe(
            language="Language to set",
        )
        @app_commands.autocomplete(
            language=autocomplete_lang,
        )
        async def config_lang_guild(
            self,
            interaction: discord.Interaction,
            language: str,
        ):
            try:
                gconfig.set(
                    id=interaction.guild_id,
                    title="APPEARANCE",
                    key="language",
                    value=language,
                )
                await interaction.response.send_message(
                    content=f"Set value {str(language)}",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )

    @app_commands.default_permissions(
        administrator=True,
    )
    class configure_ticketing(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "ticketing"
            self.description = "Configure ticketing options"

        @app_commands.command(
            name="reviews",
            description="Review system",
        )
        async def conf_ticketing_reviews(
            self,
            interaction: discord.Interaction,
            channel: discord.TextChannel = None,
            value: bool = None,
        ):
            try:
                lang_key = uconfig.get(
                    id=interaction.user.id,
                    title="Appearance",
                    key="language",
                )
                response_template = lang.get(
                    id=lang_key,
                    title="Responds",
                    key="value_set",
                )

                if channel is not None and value is not None:
                    gconfig.set(
                        id=interaction.guild_id,
                        title="Ticketing",
                        key="reviews-enabled",
                        value=value,
                    )
                    gconfig.set(
                        id=interaction.guild_id,
                        title="Ticketing",
                        key="reviews-channel",
                        value=channel.id,
                    )
                    response_message = response_template.format(
                        values=f"{value}, {channel}",
                    ) if response_template else "Value set"

                    await interaction.response.send_message(
                        content=response_message,
                        ephemeral=True,
                    )

                elif channel is None and value is not None:
                    gconfig.set(
                        id=interaction.guild_id,
                        title="Ticketing",
                        key="reviews-enabled",
                        value=value,
                    )
                    response_message = response_template.format(
                        values=f"{value}",
                    ) if response_template else "Value set"

                    await interaction.response.send_message(
                        content=response_message,
                        ephemeral=True,
                    )

                elif channel is not None and value is None:
                    gconfig.set(
                        id=interaction.guild_id,
                        title="Ticketing",
                        key="reviews-channel",
                        value=channel,
                    )
                    response_message = response_template.format(
                        values=f"{channel}",
                    ) if response_template else "Value set"

                    await interaction.response.send_message(
                        content=response_message,
                        ephemeral=True,
                    )

                else:
                    await interaction.response.send_message(
                        content="You have to choose",
                        ephemeral=True,
                    )
            except discord.Forbidden:
                logging.debug("No permissions")
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )

    @app_commands.default_permissions(
        administrator=True,
    )
    class configure_members(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "members"
            self.description = "Configure bot actions on user"

        @app_commands.command(
            name="auto-role",
            description="Automatic role on join",
        )
        @app_commands.describe(
            role="Role to add on join",
            enabled="Should it be enabled?",
        )
        async def autorole(
            self,
            interaction: discord.Interaction,
            enabled: bool,
            role: discord.Role = None,
        ):
            try:
                gconfig.set(
                    id=interaction.guild_id,
                    title="MEMBERS",
                    key="autorole-role",
                    value=role.id,
                )
                gconfig.set(
                    id=interaction.guild_id,
                    title="MEMBERS",
                    key="autorole-enabled",
                    value=enabled,
                )
                await interaction.response.send_message(
                    content=f"Set value {str(role.name)}, {str(enabled)}",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )

    @app_commands.default_permissions(
        administrator=True,
    )
    class configure(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "guildconfig"
            self.description = "Config for server"
            self.add_command(GuildConfig.configure_sec())
            self.add_command(GuildConfig.configure_appear())
            self.add_command(GuildConfig.configure_members())
            self.add_command(GuildConfig.configure_ticketing())

        @app_commands.command(
            name="reset",
            description="Resets the config. NO TAKIES BACKSIES, AS IT GETS DELETED PERMANENTLY",  # noqa: E501
        )
        async def reset_config(
            self,
            interaction: discord.Interaction,
        ):
            try:
                os.remove(f"data/guilds/{interaction.guild.id}.toml")
                await interaction.response.send_message(
                    content="Config Reset!",
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

async def setup(bot:commands.Bot):
    await bot.tree.add_command(GuildConfig.configure())
    await bot.add_cog(GuildConfig(bot))
