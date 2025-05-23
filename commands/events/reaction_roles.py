import discord  # noqa: F401
import emoji
from discord import (
    PartialEmoji,
    app_commands,  # noqa: F401
)
from discord.ext import commands

from utils.configmanager import gconfig
from utils.helpmanager import HelpManager


def string2emoji(emoji_string: str):
    if emoji_string.startswith("<:") and emoji_string.endswith(">"):  # Custom emoji
        # Extract name and ID from the custom emoji string
        parts = emoji_string.strip("<:>").split(":")
        name = parts[0]
        emoji_id = int(parts[1])
        return PartialEmoji(name=name, id=emoji_id)
    else:  # Standard Unicode emoji
        return emoji.emojize(emoji_string)

def emoji2string(emoji_obj: PartialEmoji | str):
    if isinstance(emoji_obj, PartialEmoji):  # Custom emoji
        return f"<:{emoji_obj.name}:{emoji_obj.id}>"
    else:  # Standard Unicode emoji
        return emoji.demojize(emoji_obj)

#TODO add reaction roles
#TODO pls its really importante
class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # [reaction-roles]
    # <message-id>-<emoji>-role = <role>
    # PEAK EFFICIENCI :fire:

    @app_commands.command(name="add-reaction-role",description="Create reaction roles")  # noqa: E501
    @app_commands.default_permissions(administrator=True)  # noqa: E501
    async def create_reaction(self, interaction: discord.Interaction,title:str,description:str,emoji:str,role:discord.Role,messageid:str=None,channel:discord.TextChannel=None):  # type: ignore # noqa: E501
        if channel is None:
            channel = interaction.channel
        if messageid is None:
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.blurple(),
            )
            message = await channel.send(embed=embed)
            gconfig.set(interaction.guild.id,"reaction-roles",f"{message.id}-{emoji2string(emoji)}-role",role.id)
            await message.add_reaction(string2emoji(emoji))
            await interaction.response.send_message("Reaction roles message sent!", ephemeral=True)  # noqa: E501
        else:
            message = await channel.fetch_message(int(messageid))
            if message is None:
                await interaction.response.send_message("Message not found!", ephemeral=True)  # noqa: E501
                return
            gconfig.set(interaction.guild.id,"reaction-roles",f"{message.id}-{emoji2string(emoji)}-role",role.id) # type: ignore
            await message.add_reaction(string2emoji(emoji))
            await interaction.response.send_message("Reaction role added!", ephemeral=True)  # noqa: E501

    @commands.Cog.listener("on_reaction_add")
    async def on_react(self, reaction:discord.Reaction, user):
        if user.bot:
            return

        # Example: Reaction role logic
        guild = reaction.message.guild
        reaction_roles_config = gconfig.config.get(str(guild.id), {}).get("reaction-roles", {})  # type: ignore # noqa: E501
        for key, value in reaction_roles_config.items():
            if key.startswith(f"{reaction.message.id}-"):
                _, emoji, _ = key.split("-")
                role_id = value
                if str(reaction.emoji) == string2emoji(emoji):
                    role = guild.get_role(int(role_id)) # type: ignore
                    if role:
                        await user.add_roles(role)

    @commands.Cog.listener("on_reaction_remove")
    async def on_react_remove(self, reaction, user):
        if user.bot:
            return
        guild = reaction.message.guild
        reaction_roles_config = gconfig.config.get(str(guild.id), {}).get("reaction-roles", {})  # noqa: E501
        for key, value in reaction_roles_config.items():
            if key.startswith(f"{reaction.message.id}-"):
                _, emoji, _ = key.split("-")
                role_id = int(value)
                if str(reaction.emoji) == string2emoji(emoji):
                    role = guild.get_role(int(role_id))
                    if role:
                        await user.add_roles(role)
async def setup(bot:commands.Bot):
    cog = ReactionRoles(bot)
    await bot.add_cog(cog)
    hm = HelpManager()
    hmhelp = hm.new_help("reaction-roles","add-reaction-roles","Reaction roles")
    hmhelp.set_help_page(1,"Reaction roles",description="Reaction roles are a way to assign roles to users based on their reactions to a message. This can be used for self-assignable roles, event roles, and more.")  # noqa: E501
    hmhelp.set_help_page(2,"Multiple reaction roles",description="You can add multiple reaction roles to a single message. Just use the same message ID and different emojis. Just ignore title and description as it gets ignored (put anything in there)")  # noqa: E501
