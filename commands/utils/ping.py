import discord
from discord import app_commands
from discord.ext import commands

from utils.configmanager import lang, uconfig


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="ping", description="Lets play ping pong")
    async def ping(self,interaction: discord.Interaction):

        '''
        Ping Pong the bot
        '''
        language = uconfig.get(interaction.user.id,"Appearance","language")
        embed = discord.Embed(
            title=lang.get(language,"Responds","ping"),
            description=lang.get(language,"Responds","ping_latency").format(latency=round(self.bot.latency,2)),
        )
        await interaction.response.send_message(
            embed=embed,
        )

async def setup(bot:commands.Bot):
    await bot.add_cog(Ping(bot))
