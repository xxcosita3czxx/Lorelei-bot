import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_color
from utils.configmanager import gconfig, lang, userlang

#TODO Be able to set more than title and description

#IDEA could make simmilar editor to role editor

class Echo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="echo",description="Echoes message in embed")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.autocomplete(color=autocomplete_color)
    async def echo(self,interaction: discord.Interaction,channel:discord.channel.TextChannel, title:str="", text:str="",color:str=None, is_embed:bool=True):  # noqa: E501
        try:
            if is_embed is True:
                text = text.replace("\\n", "\n")
                embed = discord.Embed(
                    title=title,
                    description="\u200B" + text,
                    color=gconfig.get(interaction.guild.id,"APPEARANCE","color"),
                )
                if color:
                    embed.color = discord.Color.from_str(color)
                await channel.send(embed=embed)
                await interaction.response.send_message(
                    lang.get(userlang(interaction.user.id),"Responds","message_sent"),  # noqa: E501
                    ephemeral=True,
                )
            else:
                await channel.send(f"# {title}\n\n"+"\u200B"+text)
                await interaction.response.send_message(
                    lang.get(userlang(interaction.user.id),"Responds","message_sent"),  # noqa: E501
                    ephemeral=True,
                )
        except Exception as e:
            await interaction.response.send_message(
                f"Echo Failed!: {e}",
                ephemeral=True,
            )
    @app_commands.command(name="echo-edit",description="Edits the echo message with id.")  # noqa: E501
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.autocomplete(color=autocomplete_color)
    async def echo_edit(self,interaction: discord.Interaction, message_id:str, title:str="", text:str="",color:str=None):  # noqa: C901, E501
        try:
            message = await interaction.channel.fetch_message(message_id)
            # Automatically detect whether the message contains an embed or is plain text  # noqa: E501
            if message.embeds:
                embed = message.embeds[0]
                # Check that this is an echo message by looking for the invisible space marker  # noqa: E501
                if not (embed.description and "\u200B" in embed.description):
                    await interaction.response.send_message(
                        lang.get(userlang(interaction.user.id),"Responds","message_not_an_echo"),  # noqa: E501
                        ephemeral=True,
                    )
                    return
                if title == "":
                    title = embed.title if embed.title else ""
                if text == "":
                    # Remove the invisible space marker before preserving existing text  # noqa: E501
                    text = embed.description.replace("\u200B", "") if embed.description else ""  # noqa: E501                embed.title = title
                # preserve newlines
                text = text.replace("\\n", "\n")
                embed.description = "\u200B" + text
                if color:
                    embed.color = discord.Color.from_str(color)
                await message.edit(embed=embed, content=None)
            else:
                # Edit raw message content. Use same format as echo when not embedding.  # noqa: E501
                # If the message looks like an echo (starts with '# '), replace it; otherwise just replace content.  # noqa: E501
                if text == "":
                    # Remove the leading '# ' and preserve existing text  # noqa: E501
                    existing_content = message.content
                    if existing_content.startswith("# "):
                        existing_content = existing_content[2:]
                    text = existing_content
                if title == "":
                    # Extract existing title if present  # noqa: E501
                    existing_content = message.content
                    if existing_content.startswith("# "):
                        existing_title = existing_content.split("\n\n")[0][2:]
                        title = existing_title
                content = f"# {title}\n\n\u200B{text}"
                await message.edit(content=content, embed=None)
            await interaction.response.send_message(
                lang.get(userlang(interaction.user.id),"Responds","message_edited"),  # noqa: E501
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Echo edit failed!: {e}",
                ephemeral=True,
            )
async def setup(bot:commands.Bot):
    await bot.add_cog(Echo(bot))
