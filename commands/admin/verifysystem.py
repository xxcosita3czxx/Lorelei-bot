import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_verify_modes
from utils.configmanager import gconfig


class VerifySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="verify-system",description="No bots in the server")
    @app_commands.default_permissions(administrator=True)
    @app_commands.autocomplete(mode=autocomplete_verify_modes)
    async def verify_system(
        self,
        interaction: discord.Interaction,
        title: str,
        description:str,
        role:discord.Role,
        channel: discord.TextChannel,
        mode: str = "button",
    ):
        gconfig.set(
            interaction.guild.id,
            str(channel.id)+"-verify",
            "role",
            role.id,
        )
        if mode == "emoji":
            await interaction.response.send_message(
                content="In progress",
                ephemeral=True,
            )
        elif mode == "button":
            await interaction.response.send_message(
                content="Selected Button",
                ephemeral=True,
            )
            embed = discord.Embed(
                title=title,
                description=description,
            )
            message:discord.Message = await channel.send(
                embed=embed,
                view=self.verify_button(),
            )
            gconfig.set(
            interaction.guild.id,
            str(channel.id)+"-verify",
            "message_id",
            message.id,
        )
        elif mode == "captcha":
            await interaction.response.send_message(
                content="In progress",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                content="Wrong type!",
                ephemeral=True,
            )

    class verify_button(discord.ui.View):
        def __init__(self)-> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Verify",
            style = discord.ButtonStyle.blurple,
            custom_id="verify",
        )
        async def verify(self, interaction: discord.Interaction, button: discord.ui.button): # noqa: E501
            #await interaction.response.send_message(content="Clicked :3",ephemeral=True) # noqa: E501
            try:
                role = gconfig.get(
                    interaction.guild.id,
                    str(interaction.channel.id)+"-verify",
                    "role",
                )
                # Convert the string back to an integer and role
                role_id = int(role)
                role = interaction.guild.get_role(role_id)

                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    content="Verified!",
                    ephemeral=True,
                )
            except discord.errors.Forbidden:
                await interaction.response.send_message(
                    content="Insufficient Permissions",
                )
            except Exception as e:
                logging.error(str(e))



async def setup(bot: commands.Bot):  # noqa: C901
    cog = VerifySystem(bot)
    await bot.add_cog(cog)

    for filename in os.listdir("data/guilds"):
        if filename.endswith(".toml"):
            guild_id = filename[:-5]  # Remove the .toml extension

            for key in gconfig.config[guild_id]:
                if key.endswith("-verify"):
                    message_id = gconfig.get(guild_id, key, "message_id")
                    channel_id_str = key[:-7]
                    role_id = gconfig.get(guild_id, key, "role")

                    # Convert channel_id to integer
                    try:
                        channel_id = int(channel_id_str)
                    except ValueError:
                        logging.error(f"Invalid channel ID {channel_id_str}")
                        continue

                    if role_id and message_id:
                        guild = bot.get_guild(int(guild_id))
                        if not guild:
                            logging.debug(f"Guild {guild_id} not found.")
                            continue
                        else:
                            logging.debug(f"Guild found: {guild}")

                        channel = guild.get_channel(channel_id)
                        if not channel:
                            logging.debug(f"Channel {channel_id} not found in guild {guild_id}")  # noqa: E501
                        else:
                            logging.debug(f"Channel found: {channel}")

                        view = cog.verify_button()
                        try:
                            message = await channel.fetch_message(int(message_id))
                            await message.edit(view=view)
                            logging.debug(f"Updated message {message_id} in channel {channel_id} with new view.")  # noqa: E501
                        except discord.NotFound:
                            logging.debug(f"Message {message_id} not found in channel {channel_id}.")  # noqa: E501
                        except discord.Forbidden:
                            logging.debug(f"Bot does not have permission to fetch message {message_id}.")  # noqa: E501
                        except discord.HTTPException as e:
                            logging.error(f"HTTP error when fetching message {message_id}: {e}")  # noqa: E501
                        except Exception as e:
                            logging.error(f"Unexpected error when updating message {message_id}: {e}")  # noqa: E501
