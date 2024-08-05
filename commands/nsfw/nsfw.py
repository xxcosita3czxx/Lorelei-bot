import random

import discord
import requests
from discord import app_commands
from discord.ext import commands


def get_nsfw_post() -> str:
    url = 'https://www.reddit.com/r/nsfw/hot/.json'
    headers = {'User-Agent': 'Lorelei-bot'}
    response = requests.get(url, headers=headers,timeout=60)
    data = response.json()
    posts = data['data']['children']
    post = random.choice(posts)['data']  # noqa: S311
    return post['url']

class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class nsfw(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "nsfw"
            self.description = "nsfw"
            self.nsfw = True

        @app_commands.command(name="irl",description="IRL photos",nsfw=True)
        async def irl(self,interaction:discord.Interaction):
            data = get_nsfw_post()
            embed = discord.Embed(
                color=discord.Color.blurple(),
                title="IRL NSFW Image",
                description="Here is nsfw image:",
            )
            embed.thumbnail(url=data)
            await interaction.response.send_message(embed=embed)

async def setup(bot:commands.Bot):
    cog = NSFW(bot)
    bot.tree.add_command(cog.nsfw())
    await bot.add_cog(cog)
