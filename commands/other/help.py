import discord
from discord import app_commands
from discord.ext import commands

import utils.help_embeds as help_pages


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="User Help")
    async def help_user(self,interaction: discord.Interaction):
        embeds = help_pages.help_user
        view = self.Help_Pages(embeds=embeds)
        await view.send_initial_message(interaction)

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

async def setup(bot:commands.Bot):
    await bot.add_cog(HelpCommand(bot))
    bot.tree.add_command(HelpCommand(bot).Help())
