import logging

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from utils.configmanager import gconfig, themes


def profile_gen(interaction=discord.Interaction,theme:str="Default"):  # noqa: E501
    logging.debug(themes.config)

    # Vars
    bg = themes.get(theme,"Data","bg")
    fixed_size = (710, 800)  # Fixed size for the profile image
    texts = themes.get(theme,"Text", "text")
    font = themes.get(theme,"Text","font")

    # Load and resize the background image
    if bg.startswith("#"):
        background = Image.new('RGB', fixed_size, color=bg)
    else:
        background = Image.open(bg)
        background = background.resize(fixed_size, Image.ANTIALIAS)

    draw = ImageDraw.Draw(background)
    logging.debug(texts)
    for text in texts:
        logging.debug(text)
        draw.text(text.position, text.content, font=ImageFont.truetype(font, text.size), fill=text.color)  # noqa: E501

    # Save the image
    if interaction.guild.id:
        background.save(f".cache/{interaction.user.id}-{interaction.guild.id}.png")
        return f".cache/{interaction.user.id or "lorem-user"}-{interaction.guild.id or "lorem-id"}.png"  # noqa: E501
    else:
        background.save(f".cache/{interaction.user.id}.png")
        return f".cache/{interaction.user.id}.png"

#def profile_gen(interaction:discord.Interaction,bg:str,theme:str="Default"):  # noqa: E501

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="global-leaderboard",description="Level Leaderboard")
    async def global_leaderboard(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="leaderboard",description="Server Leaderboard")
    async def leaderboard(self, interaction:discord.Interaction):
        if gconfig.get(interaction.guild.id,""):
            pass

    @app_commands.command(name="profile",description="Your profile")
    async def profile(self,interaction: discord.Interaction, minimal:bool=False):
        if not minimal:
            image = profile_gen(interaction=interaction,bg="data/prof-bgs/Default.png")  # noqa: E501
            embed = discord.Embed(title=f"Profile of {interaction.user.name}")
            file = discord.File(image, filename="profile.png")
            embed.set_image(url="attachment://profile.png")
            await interaction.response.send_message(embed=embed,file=file)
        else:
            embed = discord.Embed(title=f"Profile of {interaction.user.name}")
            embed.add_field(name="Level: {lorem ipsum}")
            interaction.response.send_message(embed=embed)

async def setup(bot:commands.Bot):
#    cog = LevelSystem(bot)
#    await bot.add_cog(cog)
    pass
