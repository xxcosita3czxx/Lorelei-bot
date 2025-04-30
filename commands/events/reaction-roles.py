import discord  # noqa: F401
import emoji
from discord import (
    PartialEmoji,
    app_commands,  # noqa: F401
)
from discord.ext import commands

from utils.configmanager import gconfig


def string2emoji(emoji_string:str):
    if emoji_string.startswith("<:") and emoji_string.endswith(">"):  # Custom emoji
        # Extract name and ID from the custom emoji string
        parts = emoji_string.strip("<:>").split(":")
        name = parts[0]
        emoji_id = int(parts[1])
        return PartialEmoji(name=name, id=emoji_id)
    else:  # Standard Unicode emoji
        return emoji.emojize(emoji_string, use_aliases=True)

#TODO add reaction roles
#TODO pls its really importante
class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test-reaction-roles",description="pls dont use, its testing only")  # noqa: E501
    async def create_reaction(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Reaction Roles",
            description="React with 👍 to get the ExampleRole!",
            color=discord.Color.blurple(),
        )
        message = await interaction.channel.send(embed=embed)
        gconfig.set(interaction.guild.id,"reaction-roles","message-id",message.id)
        await message.add_reaction(string2emoji(":thumbs_up:"))
    @commands.Cog.listener("on_reaction_add")
    async def on_react(self, reaction:discord.Reaction, user):
        if user.bot:
            return

        # Example: Reaction role logic
        guild = reaction.message.guild
        if reaction.message.id == gconfig.get(guild.id,"reaction-roles","message-id"):  # Replace with your message ID  # noqa: E501, SIM102
            if str(reaction.emoji) == ":thumbs_up:":  # Replace with your emoji
                await user.send("You have been given the role!")

    @commands.Cog.listener("on_reaction_remove")
    async def on_react_remove(self, reaction, user):
        if user.bot:
            return

        # Example: Reaction role removal logic
        guild = reaction.message.guild
        if reaction.message.id == gconfig.get(guild.id,"reaction-roles","message-id"):  # Replace with your message ID  # noqa: E501, SIM102
            if str(reaction.emoji) == "👍":  # Replace with your emoji
                await user.send("The role has been removed.")
async def setup(bot:commands.Bot):
    cog = ReactionRoles(bot)
    await bot.add_cog(cog)
