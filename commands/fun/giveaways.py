
#TODO logic for all

import discord
from discord import app_commands
from discord.ext import commands


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.default_permissions(administrator=True)
    class giveaway(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name="giveaway"
            self.description="Giveaway commands"

        @app_commands.command(name="create", description="Create giveaway")
        async def giveaway_create(
            self,
            interaction:discord.Interaction,
            channel:discord.TextChannel,
            duration:int,
            winners:int,
            title:str,
            description:str,
        ):
            view = Giveaways.giveaway_open()
            await view.create(interaction,channel,title,description,winners)
            await interaction.response.send_message(
                content="Giveaway created!",
                ephemeral=True,
            )

        @app_commands.command(name="reroll",description="Rerolls user")
        async def giveaway_reroll(
            self,
            interaction:discord.Interaction,
            message:str,
        ):
            pass

        @app_commands.command(name="edit",description="Edits giveaway")
        async def giveaway_edit(
            self,
            interaction:discord.Interaction,
            message:str,
            title:str,
            description:str,
        ):
            pass

        @app_commands.command(name="remove",description="Removes giveaway.")
        async def giveaway_remove(
            self,
            interaction:discord.Interaction,
            message:str,
        ):
            pass

        @app_commands.command(name="list",description="Lists all running Giveaways.")  # noqa: E501
        async def giveaway_list(
            self,
            interaction:discord.Interaction,
        ):
            pass

    class giveaway_open(discord.ui.View):
        def __init__(self) -> None:  # noqa: ANN101
            super().__init__(timeout = None)

        async def create(
            self,
            interaction: discord.Interaction,
            channel: discord.TextChannel,
            title,
            desc,
            win,
        ):
            embed = discord.Embed(
                title = title,
                description = desc,
            )
            embed.add_field(
                name="Winners",
                value=str(win),
            )
            await channel.send(embed=embed, view=self)

        @discord.ui.button(
            label = "Join",
            style = discord.ButtonStyle.blurple,
            custom_id = "join",
        )
        async def join_giv(self,interaction: discord.Interaction, button: discord.Button): # noqa: E501
            await interaction.response.send_message(content="Joined!",ephemeral=True)  # noqa: E501


async def setup(bot:commands.Bot):
    cog = Giveaways(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.giveaway())
