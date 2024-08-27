import discord
from discord import app_commands
from discord.ext import commands

from utils.embeder import respEmbed


class Echo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="echo",description="Echoes message in embed")
    @app_commands.default_permissions(manage_messages=True)
    async def echo(self,interaction: discord.Interaction,channel:discord.channel.TextChannel, title:str="", text:str=""):  # noqa: E501
        try:
            embed = discord.Embed(
                title=title,
                description=text,
                color=discord.Color.blurple(),
            )
            await channel.send(embed=embed)
            respEmbed(
                content="Message sent succesfuly!",
                ephemeral=True,
            )
        except Exception as e:
            respEmbed(
                content=f"Echo Failed!: {e}",
                ephemeral=True,
            )

async def setup(bot:commands.Bot):
    await bot.add_cog(Echo(bot))
