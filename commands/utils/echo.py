import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_color
from utils.configmanager import gconfig

#TODO Be able to set more than title and description

class Echo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="echo",description="Echoes message in embed")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.autocomplete(color=autocomplete_color)
    async def echo(self,interaction: discord.Interaction,channel:discord.channel.TextChannel, title:str="", text:str="",color:str=None, is_embed:bool=True):  # noqa: E501
        try:
            if is_embed is True:
                embed = discord.Embed(
                    title=title,
                    description="\u200B" + text,
                    color=gconfig.get(interaction.guild.id,"APPEARANCE","color"),
                )
                if color:
                    embed.color = discord.Color.from_str(color)
                await channel.send(embed=embed)
                await interaction.response.send_message(
                    "Message sent successfully!",
                    ephemeral=True,
                )
            else:
                await channel.send(f"# {title}\n\n"+"\u200B"+text)
                await interaction.response.send_message(
                    "Message sent successfully!",
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
    async def echo_edit(self,interaction: discord.Interaction, message_id:str, title:str="", text:str="",color:str=None):  # noqa: E501
        try:
            message = await interaction.channel.fetch_message(message_id)
            # Automatically detect whether the message contains an embed or is plain text  # noqa: E501
            if message.embeds:
                embed = message.embeds[0]
                # Check that this is an echo message by looking for the invisible space marker  # noqa: E501
                if not (embed.description and "\u200B" in embed.description):
                    await interaction.response.send_message(
                        "This message is not an echo message.",
                        ephemeral=True,
                    )
                    return
                embed.title = title
                embed.description = "\u200B" + text
                if color:
                    embed.color = discord.Color.from_str(color)
                await message.edit(embed=embed, content=None)
            else:
                # Edit raw message content. Use same format as echo when not embedding.  # noqa: E501
                # If the message looks like an echo (starts with '# '), replace it; otherwise just replace content.  # noqa: E501
                content = f"# {title}\n\n\u200B{text}"
                await message.edit(content=content, embed=None)
            await interaction.response.send_message(
                "Message edited successfully!",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Echo edit failed!: {e}",
                ephemeral=True,
            )
async def setup(bot:commands.Bot):
    await bot.add_cog(Echo(bot))
