
#TODO Classic counting system like carl or smt
#TODO Basic math would be fun
#TODO Maybe could implement in the level system

import ast
import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import gconfig
from utils.emoji import string2emoji

logger = logging.getLogger("counting")

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.default_permissions(manage_channels=True)
    @app_commands.command(
        name="counting",
        description="Start a counting game in the channel",
    )
    async def counting(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(title="Counting game started!", description="React with the next number. Im starting:\n# 1"),  # noqa: E501
        )
        gconfig.set(interaction.guild.id,f"{interaction.channel.id}-counting","count",1) # type: ignore

    @app_commands.default_permissions(manage_channels=True)
    @app_commands.command(
        name="counting-remove",
        description="Removes the counting",
    ) # type: ignore
    async def remcounting(self,interaction:discord.Interaction):
        await interaction.response.send_message(embed=discord.Embed(description="Removing counting!"))  # noqa: E501
        gconfig.delete(interaction.guild.id,f"{interaction.channel.id}-counting") # type: ignore

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):  # noqa: C901
        logger.debug(f"Received message: {message.content} (author: {message.author}, channel: {message.channel.id})")  # noqa: E501
        guild_id = message.guild.id if message.guild else None
        if not guild_id:
            logger.debug("No guild_id found, returning.")
            return
        config: dict = gconfig.config.get(str(guild_id),{})  # type: ignore
        logger.debug(f"Guild config: {config} for id {guild_id}")
        # Directly check for the counting key for this channel
        counting_key = f"{message.channel.id}-counting"
        if counting_key in config:
            logger.debug(f"Counting channel found: {message.channel.id}")
            if message.channel.id == int(counting_key.split('-')[0]):
                logger.debug(f"Message is in the counting channel: {message.channel.id}")  # noqa: E501
                try:
                    expr = message.content.replace(" ", "")
                    logger.debug(f"Evaluating expression: {expr}")
                    node = ast.parse(expr, mode='eval')
                    # Only allow +, -, *, / and numbers
                    allowed_nodes = (
                        ast.Expression, ast.BinOp, ast.UnaryOp,
                        ast.Num,  # for Python <3.8
                        ast.Constant,  # for Python 3.8+
                        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd,
                    )
                    for n in ast.walk(node):
                        logger.debug(f"AST node: {type(n).__name__}")
                    if not all(isinstance(n, allowed_nodes) for n in ast.walk(node)):  # noqa: E501
                        logger.debug("Disallowed AST node detected, deleting message.")  # noqa: E501
                        if message.author.id != self.bot.user.id:  # type: ignore
                            await message.delete()
                            return
                    # For mode='eval', node.body is the root expression
                    if not isinstance(node, ast.Expression):
                        logger.debug(f"AST root is not Expression: {type(node).__name__}")  # noqa: E501
                        raise ValueError("Malformed expression")
                    # Use eval(compile(...)) since ast.literal_eval does not support BinOp  # noqa: E501
                    number = int(eval(compile(node, '<string>', 'eval'), {"__builtins__": {}}))  # noqa: E501, S307 #TODO Replace with something safers
                    logger.debug(f"Parsed number: {number}")
                except Exception as e:
                    logger.debug(f"Exception during parsing/eval: {e}")
                    if message.author.id != self.bot.user.id:  # type: ignore
                        await message.delete()
                    return  # Always return after handling the exception to avoid using 'number'  # noqa: E501

                current_count = gconfig.get(message.guild.id, f"{message.channel.id}-counting", "count")  # noqa: E501
                logger.debug(f"Current count: {current_count}, Next expected: {current_count + 1}")  # noqa: E501
                if number == current_count + 1:
                    logger.debug("Correct number! Adding :white_check_mark: reaction.")  # noqa: E501
                    await message.add_reaction(string2emoji(":check_mark_button:"))
                    gconfig.set(message.guild.id, f"{message.channel.id}-counting", "count", current_count + 1)  # noqa: E501
                else:
                    logger.debug(f"Incorrect number! Got {number}, expected {current_count + 1}.")  # noqa: E501
                    await message.add_reaction(string2emoji(":cross_mark:"))
                    await message.reply(embed=discord.Embed(title=f"{message.author.mention} has broken the count!", description="Starting again..\n# 1"))  # noqa: E501
                    gconfig.set(message.guild.id, f"{message.channel.id}-counting", "count", 1)  # noqa: E501

async def setup(bot:commands.Bot):
    cog = Counting(bot)
    await bot.add_cog(cog)
