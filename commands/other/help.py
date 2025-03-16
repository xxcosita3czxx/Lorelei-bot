import discord
from discord import app_commands
from discord.ext import commands

__PRIORITY__ = 8

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @app_commands.command(name="help", description="Shows help information for commands.")  # noqa: E501
        async def help(self, interaction: discord.Interaction, group: str = None):
            help_manager = HelpManager()
            embed = discord.Embed(title="Help", color=discord.Color.blue())

            if group is None:
                embed.description = "Select a group:"
                options = [
                    discord.SelectOption(label=group_name, value=group_name)
                    for group_name in help_manager.list_groups()
                ]
                select = discord.ui.Select(placeholder="Choose a group...", options=options)  # noqa: E501

                async def select_callback(interaction: discord.Interaction):
                    selected_group = select.values[0]
                    await self.help(interaction, selected_group)

                select.callback = select_callback
                view = discord.ui.View()
                view.add_item(select)
                await interaction.response.send_message(embed=embed, view=view)
            else:
                try:
                    commands = help_manager.list_commands(group)
                    embed.title = f"Help - {group}"
                    for command_name, description in commands.items():
                        embed.add_field(name=command_name, value=description, inline=False)  # noqa: E501
                except ValueError as e:
                    embed.description = str(e)

            await interaction.response.send_message(embed=embed)

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

async def setup(bot:discord.AutoShardedClient):
    cog = HelpCommand(bot)
    await bot.add_cog(cog)
