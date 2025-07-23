#TODO Classic counting system like carl or smt
#TODO Basicaly counting, validate with reaction, if wrong raise embed
#TODO Basic math would be fun
#TODO Maybe could implement in the level system
#TODO Be able to set the counting channel

#TODO WARNING, DOESNT WORK

import ast
import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import gconfig

logger = logging.getLogger("counting")

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(
        name="counting",
        description="Start a counting game in the channel",
    )
    async def counting(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="Counting game started! React with the next number. Im starting:\n# 1",  # noqa: E501
        )
        gconfig.set(interaction.guild.id,f"{interaction.channel.id}-counting","count",1) # type: ignore

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(
        name="counting-remove",
        description="Removes the counting",
    ) # type: ignore
    async def remcounting(self,interaction:discord.Interaction):
        await interaction.response.send_message("Removing counting!")
        gconfig.delete(interaction.guild.id,f"{interaction.channel.id}-counting") # type: ignore

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        logger.debug(f"Received message: {message.content} for counter")  # noqa: E501
        guild_id = message.guild.id if message.guild else None
        if not guild_id:
            return
        config: dict = gconfig.config.get(guild_id, {})
        # Find the counting channel for this guild
        counting_channel_id = None
        for key in config:
            if key.endswith("-counting"):
                counting_channel_id = int(key.split("-")[0])
                logger.debug(f"Counting channel found: {counting_channel_id}")  # noqa: E501
                if counting_channel_id and message.channel.id == counting_channel_id:  # noqa: E501, SIM102
                    try:
                        # Evaluate math expressions safely
                        expr = message.content.replace(" ", "")
                        node = ast.parse(expr, mode='eval')
                        allowed_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.USub, ast.UAdd, ast.FloorDiv, ast.LShift, ast.RShift, ast.BitOr, ast.BitAnd, ast.BitXor, ast.Invert)  # noqa: E501
                        if not all(isinstance(n, allowed_nodes) for n in ast.walk(node)):  # noqa: E501
                            await message.delete()# type: ignor  # noqa: E501
                            return
                        number = int(ast.literal_eval(compile(node, "<string>", "eval"))) # type: ignore  # noqa: E501
                    except Exception:
                        await message.delete()
                        return

                    if number == gconfig.get(message.guild.id,f"{message.channel.id}-counting","count") + 1:  # type: ignore # noqa: E501
                        await message.add_reaction(":white_check_mark:")
                        gconfig.set(message.guild.id,f"{message.channel.id}-counting","count",gconfig.get(message.guild.id,f"{message.channel.id}-counting","count")+1) # type: ignore
                    else:
                        await message.add_reaction(":x:")
                        await message.reply(f"{message.author.mention} has broken the count! Starting again..\n# 1")  # noqa: E501
                        gconfig.set(interaction.guild.id,f"{interaction.channel.id}-counting","count",1) # type: ignore  # noqa: F821

async def setup(bot:commands.Bot):
    cog = Counting(bot)
    await bot.add_cog(cog)
