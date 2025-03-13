import discord
from discord import app_commands
from discord.ext import commands

import utils.help_embeds as help_pages

__PRIORITY__ = 8
class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    class Help_Pages(discord.ui.View):
        def __init__(self, embeds, *, timeout=180):
            super().__init__(timeout=timeout)
            self.embeds = embeds
            self.current_page = 0
            self.total_pages = len(embeds)

        async def send_initial_message(self, interaction: discord.Interaction):
            await interaction.response.send_message(
                embed=self.embeds[self.current_page],
                view=self,
            )

        @discord.ui.button(label='Previous', style=discord.ButtonStyle.primary)
        async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):  # noqa: E501
            if self.current_page > 0:
                self.current_page -= 1
                await interaction.response.edit_message(
                    embed=self.embeds[self.current_page],
                    view=self,
                )

        @discord.ui.button(label='Next', style=discord.ButtonStyle.primary)
        async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):  # noqa: E501
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
                await interaction.response.edit_message(
                    embed=self.embeds[self.current_page],
                    view=self,
                )

    @app_commands.command(name="help", description="User Help")
    async def help_user(self,interaction: discord.Interaction):
        embeds = help_pages.help_user
        view = self.Help_Pages(embeds=embeds)
        await view.send_initial_message(interaction)

    @app_commands.default_permissions(administrator=True)
    class Help(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "helpadmin"
            self.description = "Help command"

        @app_commands.command(name="configure",description="Configuring help")
        async def help_configure(self,interaction:discord.Interaction):
            pass

        @app_commands.command(name="admin",description="Admin help")
        async def help_admin(self,interaction:discord.Interaction):
            embeds = help_pages.help_user
            view = self.Help_Pages(embeds=embeds)
            await view.send_initial_message(interaction)

        @app_commands.command(name="other",description="Other/test commands")
        async def help_other(self,interaction:discord.Interaction):
            pass

class HelpManager:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.help_pages = {}  # Initialize the dictionary once
        return cls._instance

    def create_group(self, group_name: str):
        """Creates a new help group if it doesn't exist."""
        if group_name in self.help_pages:
            raise ValueError(f"Group '{group_name}' already exists.")
        self.help_pages[group_name] = {}

    def add_help_page(self, group_name: str, command_name: str, embed: discord.Embed):  # noqa: E501
        """Adds a help page (embed) for a command inside a group."""
        if group_name not in self.help_pages:
            self.create_group(group_name)  # Auto-create the group if missing
        self.help_pages[group_name][command_name] = embed

    def get_help_page(self, group_name: str, command_name: str) -> discord.Embed:
        """Retrieves the help embed for a command inside a group."""
        if group_name not in self.help_pages:
            raise ValueError(f"Group '{group_name}' does not exist.")
        if command_name not in self.help_pages[group_name]:
            raise ValueError(f"Command '{command_name}' does not exist in group '{group_name}'.")  # noqa: E501
        return self.help_pages[group_name][command_name]

    def list_groups(self) -> list:
        """Returns a list of all help groups."""
        return list(self.help_pages.keys())

    def add_command_to_group(self, group_name: str, command_name: str, description: str):  # noqa: E501
        """Adds a command with a description to a group."""
        if group_name not in self.help_pages:
            raise ValueError(f"Group '{group_name}' does not exist.")
        self.help_pages[group_name][command_name] = description

    def list_commands(self, group_name: str) -> dict:
        """Lists all commands in a given group."""
        if group_name not in self.help_pages:
            raise ValueError(f"Group '{group_name}' does not exist.")
        return self.help_pages[group_name]


async def setup(bot:commands.Bot):
#    await bot.add_cog(HelpCommand(bot))
#    bot.tree.add_command(HelpCommand(bot).Help())
    pass
