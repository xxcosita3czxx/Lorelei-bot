import logging
import random

import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_dice_modes
from utils.configmanager import gconfig, lang, uconfig
from utils.dices import dices
from utils.guildconfig import GuildConfig

logger = logging.getLogger("dice")

class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dice",description="Roll the Dice!")
    @app_commands.autocomplete(mode=autocomplete_dice_modes)
    async def dice(self,interaction:discord.Interaction,mode:str=None): # type: ignore
        if mode == "" or mode is None:  # noqa: SIM118
            mode = gconfig.get(
                id=interaction.guild.id, # type: ignore
                title="FUN",
                key="def_dice",
            )
            if mode is None:
                mode = uconfig.get(
                    id=interaction.user.id,
                    title="FUN",
                    key="def_dice",
                )
                if mode is None:
                    mode = "classic (D6)"
        elif mode not in dices.keys():  # noqa: SIM118
            embed = discord.Embed(
                title="Error",
                description="Invalid dice mode",
            )
            await interaction.response.send_message(embed=embed,ephemeral=True)
            return
        try:
            min_val, max_val = dices[mode]
            roll = random.randint(min_val,max_val)  # noqa: S311
            embed = discord.Embed(
                title=lang.get(uconfig.get(interaction.user.id,"APPEARANCE","language"),"Responds","dice_roller_title"),
                description=lang.get(uconfig.get(interaction.user.id,"APPEARANCE","language"),"Responds","dice_roller_desc").format(mode=mode,roll=roll),
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"dice failed, \n{e}")
async def setup(bot:commands.Bot):
    await bot.add_cog(Dice(bot))
    configman = GuildConfig()
    configman.add_setting("Fun", "Dice Type", "Configure the default dice type on the server")  # noqa: E501
    configman.add_option_list(  # type: ignore
        category_name="Fun",
        setting_name="Dice Type",
        name="Default Dice Type",
        options_list=dices.keys(),
        config_title="FUN",
        config_key="def_dice",
        description="Default dice type to use when no mode is specified.",
    )
