import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_verify_modes
from utils.configmanager import gconfig


class VerifySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="verify-system",description="No bots in the server")
    @app_commands.default_permissions(administrator=True)
    @app_commands.autocomplete(mode=autocomplete_verify_modes)
    async def verify_system(
        self,
        interaction: discord.Interaction,
        title: str,
        description:str,
        role:discord.Role,
        channel: discord.TextChannel,
        mode: str = "button",
    ):
        gconfig.set(
            interaction.guild.id,
            str(interaction.channel.id)+"-verify",
            "role",
            role,
        )
        if mode == "emoji":
            await interaction.response.send_message(
                content="In progress",
                ephemeral=True,
            )
        elif mode == "button":
            await interaction.response.send_message(
                content="Selected Button",
                ephemeral=True,
            )
            embed = discord.Embed(
                title=title,
                description=description,
            )
            await channel.send(embed=embed,view=self.verify_button())
        elif mode == "captcha":
            await interaction.response.send_message(
                content="In progress",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                content="Wrong type!",
                ephemeral=True,
            )

    class verify_button(discord.ui.View):
        def __init__(self)-> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Verify",
            style = discord.ButtonStyle.blurple,
            custom_id="verify",
        )
        async def verify(self, interaction: discord.Interaction, button: discord.ui.button): # noqa: E501
            #await interaction.response.send_message(content="Clicked :3",ephemeral=True) # noqa: E501
            try:
                role = gconfig.get(
                    interaction.guild.id,
                    str(interaction.channel.id)+"-verify",
                    "role",
                )
                await interaction.user.add_roles(role)
                await interaction.response.send_message(content="Verified!")
            except discord.errors.Forbidden:
                await interaction.response.send_message(
                    content="Insufficient Permissions",
                )
            except Exception as e:
                logging.error(str(e))

async def setup(bot:commands.Bot):
    await bot.add_cog(VerifySystem(bot))
