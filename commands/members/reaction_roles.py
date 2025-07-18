import discord  # noqa: F401
from discord import app_commands
from discord.ext import commands

from utils.configmanager import gconfig
from utils.emoji import emoji2string, string2emoji
from utils.helpmanager import HelpManager


#TODO Make it nicer and configurable trough new config system
class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # [reaction-roles]
    # <message-id>-<emoji>-role = <role>
    # PEAK EFFICIENCI :fire:

    @app_commands.command(name="add-reaction-role",description="Create reaction roles")  # noqa: E501
    @app_commands.default_permissions(administrator=True)
    async def create_reaction(self, interaction: discord.Interaction,
            title:str,
            description:str,
            emoji:str,
            role:discord.Role,
            messageid:str=None, # type: ignore
            channel:discord.TextChannel=None): # type: ignore
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
    hmhelp = hm.new_help("Members","add-reaction-roles","Reaction roles")
    hmhelp.set_help_page(1,"Reaction roles",description="Reaction roles are a way to assign roles to users based on their reactions to a message. This can be used for self-assignable roles, event roles, and more.")  # noqa: E501
    hmhelp.set_help_page(2,"Multiple reaction roles",description="You can add multiple reaction roles to a single message. Just use the same message ID and different emojis. Just ignore title and description as it gets ignored (put anything in there)")  # noqa: E501
