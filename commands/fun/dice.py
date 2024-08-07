import logging
import random

import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_dice_modes
from utils.configmanager import gconfig, uconfig
from utils.dices import dices


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dice",description="Roll the Dice!")
    @app_commands.autocomplete(mode=autocomplete_dice_modes)
    async def dice(self,interaction:discord.Interaction,mode:str):
        if mode == "" or mode is None:  # noqa: SIM118
            mode = gconfig.get(id=interaction.guild.id,title="FUN",key="def_dice")  # noqa: E501
            if mode is None:
                mode = uconfig.get(id=interaction.user.id,title="FUN",key="def_dice")  # noqa: E501
                if mode is None:
                    mode = "classic (6 sides)"
        elif mode not in dices.keys():  # noqa: SIM118
            embed = discord.Embed(
                title="Error",
                description="Invalid dice mode",
            )
            await interaction.response.send_message(embed=embed,ephemeral=True)  # noqa: E501
            return
        try:
            min_val, max_val = dices[mode]
            roll = random.randint(min_val,max_val)  # noqa: S311
            embed = discord.Embed(
                title="The Dice Roller 3000",
                description=f"And rolled number is....\n# {roll}",
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logging.error(f"dice failed, \n{e}")
async def setup(bot:commands.Bot):
    await bot.add_cog(Dice(bot))
