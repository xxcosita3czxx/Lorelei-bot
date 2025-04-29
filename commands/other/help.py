import discord
from discord import app_commands
from discord.ext import commands

__PRIORITY__ = 10

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Shows help information for commands.")  # noqa: E501
    async def helpcommand(self, interaction: discord.Interaction, group: str = None, command: str = None, page: int = 1):  # noqa: C901, E501
        help_manager = HelpManager()
        embed = discord.Embed(title="Help", color=discord.Color.blurple())
        message_sent = False

        if group is None:
            # Show list of groups
            embed.description = "Select a group:"
            options = [
                discord.SelectOption(label=group_name, value=group_name)
                for group_name in help_manager.list_groups()
            ]
            select = discord.ui.Select(placeholder="Choose a group...", options=options)  # noqa: E501

            async def select_callback(interaction: discord.Interaction):
                selected_group = select.values[0]
                await self.helpcommand(interaction, group=selected_group)

            select.callback = select_callback
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(embed=embed, view=view)
            message_sent = True

        elif command is None:
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
                    await self.helpcommand(interaction, group=group, command=selected_command)  # noqa: E501

                select.callback = select_callback
                view = discord.ui.View()
                view.add_item(select)
                await interaction.response.send_message(embed=embed, view=view)
                message_sent = True
            except ValueError as e:
                embed.description = str(e)

        else:
            # Show specific page of the command
            try:
                pages = help_manager.list_pages(group, command)
                if page not in pages:
                    raise ValueError(f"Page '{page}' does not exist for command '{command}' in group '{group}'.")  # noqa: E501

                embed = help_manager.get_help_page(group, command, page)
                embed.set_footer(text=f"Page {page} of {len(pages)}")

                if len(pages) > 1:
                    # Add navigation buttons if there are multiple pages
                    view = discord.ui.View()

                    if page > 1:
                        prev_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.primary)  # noqa: E501

                        async def prev_callback(interaction: discord.Interaction):
                            await self.helpcommand(interaction, group=group, command=command, page=page - 1)  # noqa: E501

                        prev_button.callback = prev_callback
                        view.add_item(prev_button)

                    if page < len(pages):
                        next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.primary)  # noqa: E501

                        async def next_callback(interaction: discord.Interaction):
                            await self.helpcommand(interaction, group=group, command=command, page=page + 1)  # noqa: E501

                        next_button.callback = next_callback
                        view.add_item(next_button)

                    await interaction.response.send_message(embed=embed, view=view)
                    message_sent = True
                else:
                    embed.set_footer(text="Page 1 of 1")
            except ValueError as e:
                embed.description = str(e)

        if not message_sent:
            await interaction.response.send_message(embed=embed)

class HelpManager:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.help_pages = {}  # Initialize the dictionary once
        return cls._instance
    class new_help:
        def __init__(self,group_name: str, command_name: str, description: str):  # noqa: E501
            super().__init__(HelpManager._instance)
            self.group_name = group_name
            self.command_name = command_name
            self.description = description

        def set_help_page(self, page: int, title: str, description:str):  # noqa: E501
            """Adds a help page (embed) for a command inside a group."""
            if self.group_name not in self.help_pages:
                self.help_pages[self.group_name] = {}
            if self.page not in self.help_pages[self.group_name]:
                self.help_pages[self.group_name][page] = {}
            self.help_pages[self.group_name][self.command_name][page] = {
                "title": title,
                "description": description,
            }

    def get_help_page(self, group_name: str, command_name: str, page:int) -> discord.Embed:  # noqa: E501
        """Retrieves the help embed for a command inside a group."""
        if group_name not in self.help_pages:
            raise ValueError(f"Group '{group_name}' does not exist.")
        if command_name not in self.help_pages[group_name]:
            raise ValueError(f"Command '{command_name}' does not exist in group '{group_name}'.")  # noqa: E501
        if page not in self.help_pages[group_name][command_name]:
            raise ValueError(f"Page '{page}' does not exist in command '{command_name}'.")  # noqa: E501
        return self.help_pages[group_name][command_name][page]["embed"]

    def list_groups(self) -> list:
        """Returns a list of all help groups."""
        return list(self.help_pages.keys())

    def list_commands(self, group_name: str) -> list:
        """Lists all commands in a given group."""
        if group_name not in self.help_pages:
            raise ValueError(f"Group '{group_name}' does not exist.")
        return list(self.help_pages[group_name].keys())

    def list_pages(self, group_name: str,command_name: str) -> list:
        """Lists all commands in a given group."""
        if group_name not in self.help_pages:
            raise ValueError(f"Group '{group_name}' does not exist.")
        if command_name not in self.help_pages[group_name]:
            raise ValueError(f"Group '{command_name}' does not exist.")
        return list(self.help_pages[group_name][command_name].keys())

async def setup(bot:discord.AutoShardedClient):
    cog = HelpCommand(bot=bot)
    await bot.add_cog(cog)
