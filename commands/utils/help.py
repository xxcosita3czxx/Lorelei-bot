import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import (
    autocomplete_help_commands,
    autocomplete_help_groups,
    autocomplete_help_pages,
)
from utils.helpmanager import HelpManager

logger = logging.getLogger("help")
__PRIORITY__ = 10

#TODO help doesnt show all commands if group is none
#TODO add nsfw flag to exclude help when not in nsfw channel
#TODO Help should edit single message

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Shows help information for commands.")  # noqa: E501
    @app_commands.autocomplete(
        group=autocomplete_help_groups,  # noqa: E501
        command=autocomplete_help_commands,  # noqa: E501
        page=autocomplete_help_pages,  # noqa: E501
    )
    async def helpcommand(self, interaction: discord.Interaction, group: str = None, command: str = None, page: int = 1):  # type: ignore # noqa: E501
        await self.handle_help(interaction, group, command, page)

    async def handle_help(self, interaction: discord.Interaction, group: str = None, command: str = None, page: int = 1):  # type: ignore # noqa: C901, E501
        help_manager = HelpManager()
        embed = discord.Embed(title="Help", color=discord.Color.blurple())
        message_sent = False

        if group is None and command is None:
            # Show list of groups
            embed.description = "Select a group:"
            options = [
                discord.SelectOption(label=group_name, value=group_name)
                for group_name in help_manager.list_groups()
            ]
            select = discord.ui.Select(placeholder="Choose a group...", options=options)  # noqa: E501

            async def select_callback(interaction: discord.Interaction):
                selected_group = select.values[0]
                await self.handle_help(interaction, group=selected_group)

            select.callback = select_callback
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)  # noqa: E501
            message_sent = True

        elif command is None and group:
            # Show list of commands in the group
            try:
                commands = help_manager.list_commands(group)
                embed.title = f"Help - {group}"
                embed.description = "Select a command:"
                options = [
                    discord.SelectOption(label=command_name, value=command_name)
                    for command_name in commands
                ]
                select = discord.ui.Select(placeholder="Choose a command...", options=options)  # noqa: E501

                async def select_callback(interaction: discord.Interaction):
                    selected_command = select.values[0]
                    await self.handle_help(interaction, group=group, command=selected_command)  # noqa: E501

                select.callback = select_callback
                view = discord.ui.View()
                view.add_item(select)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)  # noqa: E501
                message_sent = True
            except ValueError as e:
                embed.description = str(e)

        else:
            # Show specific page of the command
            try:
                pages = help_manager.list_pages(group, command)
                if page not in pages:
                    raise ValueError(f"Page '{page}' does not exist for command '{command}' in group '{group}'.")  # noqa: E501

                embed = discord.Embed(title=help_manager.get_help_page(group, command, page)["title"],description=help_manager.get_help_page(group, command, page)["description"])  # type: ignore # noqa: E501
                embed.set_footer(text=f"Page {page} of {len(pages)}")

                if len(pages) > 1:
                    # Add navigation buttons if there are multiple pages
                    view = discord.ui.View()

                    if page > 1:
                        prev_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.primary)  # noqa: E501

                        async def prev_callback(interaction: discord.Interaction):
                            await self.handle_help(interaction, group=group, command=command, page=page - 1)  # noqa: E501

                        prev_button.callback = prev_callback
                        view.add_item(prev_button)

                    if page < len(pages):
                        next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.primary)  # noqa: E501

                        async def next_callback(interaction: discord.Interaction):
                            await self.handle_help(interaction, group=group, command=command, page=page + 1)  # noqa: E501

                        next_button.callback = next_callback
                        view.add_item(next_button)

                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)  # noqa: E501
                    message_sent = True
                else:
                    embed.set_footer(text="Page 1 of 1")
            except ValueError as e:
                embed.description = str(e)

        if not message_sent:
            await interaction.response.send_message(embed=embed, ephemeral=True)  # noqa: E501

async def setup(bot:discord.AutoShardedClient):
    cog = HelpCommand(bot=bot)
    await bot.add_cog(cog) # type: ignore
