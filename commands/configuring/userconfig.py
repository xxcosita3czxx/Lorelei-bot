import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_color, autocomplete_lang
from utils.configmanager import lang, uconfig

name="userconfig"
description="User Config"
group = app_commands.Group(name=name,description=description)

class UserConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @group.command(name="color",description="Default color bot will respond for you")  # noqa: E501
    @app_commands.autocomplete(color=autocomplete_color)
    async def conf_user_color(self,interaction:discord.Interaction, color:str):
        try:
            uconfig.set(interaction.user.id,"Appearance","color",color)
            await interaction.response.send_message(
                content=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","value_set").format(values=color),
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Exception happened: {e}",
                ephemeral=True,
            )

    @group.command(
        name="language",
        description="Language the bot will respond to you",
    )
    @app_commands.autocomplete(language=autocomplete_lang)
    async def conf_user_lang(self,interaction:discord.Interaction,language:str):
        try:
            uconfig.set(interaction.user.id,"Appearance","language",language)
            await interaction.response.send_message(
                content=f"Setted value {str(language)}",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Exception happened: {e}",
                ephemeral=True,
            )

async def setup(bot:commands.Bot):
    cog = UserConfig(bot)
    bot.tree.add_command(group)
    await bot.add_cog(cog)
