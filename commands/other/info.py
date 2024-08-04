import discord
from discord import app_commands
from discord.ext import commands

import config
import utils.cosita_toolkit as ctkit
from utils.configmanager import lang, uconfig

mowner,mrepo = config.repository.split("/")
def info_text_gen(userid):
    info_text_raw = lang.get(
        uconfig.get(
            userid,
            "Appearance",
            "language",
        ),
        "Responds",
        "info_text_raw",
    )

    contributors = ctkit.GithubApi.get_repo_contributors(owner=mowner,repo=mrepo)
    contributors = [
        contributor for contributor in contributors if contributor != mowner
    ]
    for contributor in contributors:
        if contributor is not str(mowner):
            info_text_raw += f"- {contributor}\n"
    return info_text_raw

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="Info about bot")
    async def info(self,interaction: discord.Interaction):
        '''Help command
        Will let user know what all can he do
        '''
        embed = discord.Embed(
            title="Lorelei-bot",
            description=info_text_gen(userid=interaction.user.id),
            color=discord.colour.Color.blurple(),
        )

        await interaction.response.send_message(
            embed=embed,
        )

async def setup(bot:commands.Bot):
    await bot.add_cog(Info(bot))
