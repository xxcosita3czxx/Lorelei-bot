
#TODO logic for all
#TODO Modal Editor

import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import gconfig

logger = logging.getLogger("giveaways")

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
            await interaction.response.defer(ephemeral=True)  # type: ignore

        @app_commands.command(name="running",description="List of all running Giveaways.")  # noqa: E501
        async def giveaway_list(
            self,
            interaction:discord.Interaction,
        ):
            await Giveaways.giveaway_list().create(interaction=interaction)

    class giveaway_list(discord.ui.View):
        def __init__(self):
            super().__init__(timeout = None)
        async def create(self,interaction:discord.Interaction):
            embed= discord.Embed(
                title="Running Giveaways in the server",
            )
            await interaction.response.send_message(embed=embed,view=self) # type: ignore
        @discord.ui.button(
            label="Previous",
            style=discord.ButtonStyle.blurple,
            custom_id="prev_giveaway_list",
        ) # type: ignore
        async def previous(self,interaction:discord.Interaction,button:discord.Button):  # noqa: E501
            await interaction.response.send_message("Previous",ephemeral=True)

        @discord.ui.button(
            label="Next",
            style=discord.ButtonStyle.blurple,
            custom_id="next_giveaway_list",
        ) # type: ignore
        async def next(self,interaction:discord.Interaction,button:discord.Button):
            await interaction.response.send_message("Next",ephemeral=True)

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
        ) # type: ignore
        async def join_giv(self,interaction: discord.Interaction, button: discord.Button): # noqa: E501
            if gconfig.get(interaction.guild.id,"Giveaways",f"{interaction.message.id}-joined") is not None:  # type: ignore # noqa: E501
                old = gconfig.get(interaction.guild.id,"Giveaways",f"{interaction.message.id}-joined")  # type: ignore # noqa: E501
                gconfig.set(interaction.guild.id,"Giveaways",f"{interaction.message.id}-joined",f"{old} {interaction.user.id}")  # type: ignore # noqa: E501
            else:
                gconfig.set(interaction.guild.id,"Giveaways",f"{interaction.message.id}-joined",interaction.user.id) # type: ignore
            await interaction.response.send_message(content="Joined!",ephemeral=True)  # noqa: E501
            logger.debug(gconfig.get(interaction.guild.id,"Giveaways",f"{interaction.message.id}-joined")) # type: ignore

async def setup(bot:commands.Bot):
    cog = Giveaways(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.giveaway())
#    pass
