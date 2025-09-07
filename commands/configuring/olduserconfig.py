from discord import app_commands
import discord
from discord.ext import commands

from utils.autocomplete import (
    autocomplete_color,
    autocomplete_dice_modes,
    autocomplete_lang,
)
from utils.configmanager import lang, uconfig
from utils.dices import dices


__PRIORITY__ = 9
class UserConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.default_permissions(
        administrator=True,
    )
    class userconfig(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "olduserconfig"
            self.description = "Config for users"
        @app_commands.command(name="color",description="Default color bot will respond for you")  # noqa: E501
        @app_commands.autocomplete(color=autocomplete_color)
        async def conf_user_color(self,interaction:discord.Interaction, color:str):
            try:
                uconfig.set(interaction.user.id,"Appearance","color",color) # type: ignore
                await interaction.response.send_message(
                    content=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","value_set").format(values=color),
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )
        @app_commands.command(name="dice",description="Default dice mode")
        @app_commands.autocomplete(mode=autocomplete_dice_modes)
        async def conf_fun_dice(self, interaction:discord.Interaction,mode:str):
            if mode is None or mode == "" and mode not in dices.keys():  # noqa: SIM118
                mode = "classic (6 sides)"
            uconfig.set(interaction.guild.id,"FUN","def_dice",mode) # type: ignore
            await interaction.response.send_message(content=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","value_set").format(values=mode))  # noqa: E501

        @app_commands.command(
            name="language",
            description="Language the bot will respond to you",
        )
        @app_commands.autocomplete(language=autocomplete_lang)
        async def conf_user_lang(self,interaction:discord.Interaction,language:str):
            try:
                uconfig.set(interaction.user.id,"Appearance","language",language) # type: ignore
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
    #cog = UserConfig(bot)
    #await bot.add_cog(cog)
    #bot.tree.add_command(cog.userconfig())
    pass
