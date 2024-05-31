import asyncio
import logging
import os
import random
import re
from collections import defaultdict
from datetime import datetime
from typing import List

import coloredlogs
import discord
import requests
import toml
from discord import app_commands, utils
from discord.ext import commands
from humanfriendly import format_timespan

import config
import utils.cosita_toolkit as ctkit

coloredlogs.install(
    level=config.loglevel,
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
conflang=config.language

mowner,mrepo = config.repository.split("/")

logger = logging.getLogger(__name__)
time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
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

class ConfigManager:
    def __init__(self, config_dir, fallback_file=None):
        self.config_dir = config_dir
        self.config = defaultdict(dict)
        self.fallback_file = fallback_file
        self._load_all_configs()

    def _load_all_configs(self):
        logging.debug("Loading all configs...")
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.toml'):
                id = filename[:-5]  # Remove the .toml extension to get the ID
                file_path = os.path.join(self.config_dir, filename)
                with open(file_path) as f:
                    self.config[id] = toml.load(f)
        logging.debug(f"Loaded configs: {self.config}")

    def get(self, id, title, key, default=None):
        logging.debug(f"Getting {id}:{title}:{key}")
        result = self.config.get(id, {}).get(title, {}).get(key, default)
        if result is None and self.fallback_file:
            with open(self.fallback_file) as f:
                fallback_config = toml.load(f)
            fallback_result = fallback_config.get(title, {}).get(key, default)
            if fallback_result is not None:
                logging.debug("Giving fallback result...")
                result = fallback_result
        logging.debug("Final result: " + str(result))
        return result

    def set(self, id, title, key, value):
        logging.debug(f"Setting {id}:{title}:{key} to {value}")
        if id not in self.config:
            self.config[id] = {}
        if title not in self.config[id]:
            self.config[id][title] = {}
        self.config[id][title][key] = value
        self._save_config(id)
        self._load_all_configs()  # Reload the specific config after saving
        logging.debug(f"Set {id}:{title}:{key} to {value}")

    def _save_config(self, id):
        file_path = os.path.join(self.config_dir, f"{id}.toml")
        logging.debug(f"Saving config for {id} to {file_path}")
        with open(file_path, 'w') as f:
            toml.dump(self.config[id], f)

    def _load_config(self, id):
        file_path = os.path.join(self.config_dir, f"{id}.toml")
        logging.debug(f"Reloading config for {id} from {file_path}")
        if os.path.exists(file_path):
            with open(file_path) as f:
                self.config[id] = toml.load(f)
        else:
            self.config[id] = defaultdict(dict)
        logging.debug(f"Reloaded config for {id}:", self.config[id])

gconfig = ConfigManager("data/guilds")
uconfig = ConfigManager("data/users")
lang = ConfigManager("data/lang","data/lang/en.toml")

async def autocomplete_color(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:  # noqa: E501
    colors = ['Blurple', 'Red', 'Green', 'Blue', 'Yellow',"Purple","White"]
    return [app_commands.Choice(name=color, value=color) for color in colors if current.lower() in color.lower()]  # noqa: E501

async def autocomplete_lang(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:  # noqa: E501
    directory = "data/lang"
    def get_toml_files(directory: str) -> List[str]:
        toml_files = []
        for f in os.listdir(directory):
            if f.endswith('.toml'):
                filename_without_extension = f[:-5]
                toml_files.append(filename_without_extension)
        return toml_files
    toml_files = get_toml_files(directory)
    return [app_commands.Choice(name=language, value=language) for language in toml_files if current.lower() in language.lower()]  # noqa: E501

async def change_status() -> None:
    while True:
        await bot.change_presence(
            activity=discord.Game(name="Some chords"),
            status=config.status,
        )
        logging.debug(lang.get(conflang,"Bot","debug_status_chng"))
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"On {len(bot.guilds)} servers",
            ),
            status=config.status,
        )
        logging.debug(lang.get(conflang,"Bot","debug_status_chng"))
        await asyncio.sleep(5)
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/help",
            ),
            status=config.status,
        )
        logging.debug(lang.get(conflang,"Bot","debug_status_chng"))
        await asyncio.sleep(5)


class TimeConverter(app_commands.Transformer):

    async def transform(self,interaction:discord.Interaction,argument:str) -> int:  # noqa: E501, ANN101

        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0

        for key, value in matches:

            try:
                time += time_dict[value] * float(key)

            except KeyError:
                raise app_commands.BadArgument(  # noqa: B904
                    f"{value} is an invalid time key! h|m|s|d are valid arguments",
                )

            except ValueError:
                raise app_commands.BadArgument(f"{key} is not a number!")  # noqa: B904

        return round(time)

#########################################################################################

class aclient(discord.Client):

    '''
    Main Client proccess

    This connects the bot to discord
    '''

    def __init__(self) -> None:  # noqa: ANN101
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents = intents)
        self.synced = False
        self.added = False

    async def on_ready(self) -> None:  # noqa: ANN101

        await self.wait_until_ready()

        if not self.synced:
            await tree.sync()
            self.synced = True

        if not self.added:
            self.add_view(ticket_launcher())
            self.add_view(main())
            self.added = True

        logger.info(lang.get(conflang,"Bot","info_logged").format(user=self.user))
        await change_status()

bot = aclient()
tree = app_commands.CommandTree(bot)
tree.remove_command("help")

################################ EVENTS ############################################

@bot.event
async def on_message(message:discord.Message):
    logging.debug("on_message was triggered")
    ulanguage = uconfig.get(message.author.id,"Appearance","language")
    if message.guild:
        guild_id = message.guild.id
        logging.debug(message.guild)
        logging.debug(guild_id)
        if gconfig.get(str(guild_id),"SECURITY","anti-invite") is True:
            logging.debug("Anti-invite status:"+str(gconfig.get(
                str(guild_id),"SECURITY","anti-invite")),
            )
            if message.author == bot.user:
                return
            if 'discord.gg' in message.content:
                await message.delete()
                await message.author.send(
                    content=lang.get(ulanguage,"Responds","no_invites"),
                )
        else:
            logging.debug("anti-invite disabled")

        if gconfig.get(str(guild_id),"SECURITY","anti-links") is True:
            logging.debug("Anti-links Status:"+str(
                gconfig.get(str(guild_id),"SECURITY","anti-links")),
            )
            if message.author == bot.user:
                return
            if 'https://' or "http://" or "www." in message.content.lower():  # noqa: SIM222
                await message.delete()
                await message.author.send(
                    content=lang.get(
                        ulanguage,
                        "Responds",
                        "no_links",
                    ).format(author=message.author.mention),
                )
        else:
            logging.debug("anti_links disabled")
@bot.event
async def on_member_join(member:discord.Member):
    logging.debug("on_member_join was triggered!")
    logging.debug(str(member.guild) + " / " + str(member.guild.id))
    if gconfig.get(str(member.guild.id),"MEMBERS","autorole-enabled") is True:
        role_id = gconfig.get(str(member.guild.id),"MEMBERS","autorole-role")
        logging.debug("Role_id:"+str(role_id))
        role = member.guild.get_role(role_id)
        await member.add_roles(role)

############################# Context Commands #####################################

@tree.context_menu(name="User Info")
async def user_info_context(interaction: discord.Interaction, member:discord.User):
    logger.debug(member.display_avatar.key)
    embed = discord.Embed(title="Info about", color=discord.Color.blurple())
    embed.set_thumbnail(url=member.display_avatar.url)
    ulang = uconfig.get(interaction.user.id,"Appearance","language")

    embed.add_field(
        name=lang.get(ulang,"UserInfo","username"),
        value=member.name,
        inline=True,
    )

    embed.add_field(
        name=lang.get(ulang,"UserInfo","display_name"),
        value=member.display_name,
        inline=True,
    )

    embed.add_field(
        name=lang.get(ulang,"UserInfo","id"),
        value=member.id,
        inline=True,
    )

    embed.add_field(
        name=lang.get(ulang,"UserInfo","joined_dsc"),
        value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=True,
    )

    embed.add_field(
        name=lang.get(ulang,"UserInfo","joined_guild"),
        value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=True,
    )

    embed.add_field(
        name=lang.get(ulang,"UserInfo","roles"),
        value=", ".join([role.name for role in member.roles]),
        inline=False,
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )


############################ Basic ########################


@tree.command(name="user-info",description="Info about user")
async def user_info(interaction: discord.Interaction, member:discord.User):
    logger.debug(member.display_avatar.key)
    embed = discord.Embed(title="Info about", color=discord.Color.blurple())
    embed.set_thumbnail(url=member.display_avatar.url)
    ulang = uconfig.get(interaction.user.id,"Appearance","language")

    embed.add_field(
        name=lang.get(ulang,"UserInfo","username"),
        value=member.name,
        inline=True,
    )

    embed.add_field(
        name=lang.get(ulang,"UserInfo","display_name"),
        value=member.display_name,
        inline=True,
    )

    embed.add_field(
        name=lang.get(ulang,"UserInfo","id"),
        value=member.id,
        inline=True,
    )

    embed.add_field(
        name=lang.get(ulang,"UserInfo","joined_dsc"),
        value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=True,
    )

    embed.add_field(
        name=lang.get(ulang,"UserInfo","joined_guild"),
        value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=True,
    )

    embed.add_field(
        name=lang.get(ulang,"UserInfo","roles"),
        value=", ".join([role.name for role in member.roles]),
        inline=False,
    )

@tree.command(name="info", description="Info about bot")
async def info(interaction: discord.Interaction):
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

@tree.command(name="ping", description="Lets play ping pong")
async def ping(interaction: discord.Interaction):

    '''
    Ping Pong the bot
    '''
    language = uconfig.get(interaction.user.id,"Appearance","language",default="en")
    embed = discord.Embed(
        title=lang.get(language,"Responds","ping"),
        description=lang.get(language,"Responds","ping_latency").format(latency=round(bot.latency,2)),
    )
    await interaction.response.send_message(
        embed=embed,
    )

@tree.command(name="echo",description="Echoes message in embed")
@app_commands.default_permissions(manage_messages=True)
async def echo(interaction: discord.Interaction,channel:discord.channel.TextChannel, title:str="", text:str=""):  # noqa: E501
    try:
        embed = discord.Embed(
            title=title,
            description=text,
            color=discord.Color.blurple(),
        )
        await channel.send(embed=embed)
        await interaction.response.send_message(
            content="Message sent succesfuly!",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(
            content=f"Echo Failed!: {e}",
            ephemeral=True,
        )


@app_commands.default_permissions(manage_guild=True)
class ticketing_group(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name="ticketing"
        self.description="Ticket commands"
    @app_commands.command(name="add",description="Add user or role into ticket")
    @app_commands.describe(user="Member to add")
    @app_commands.describe(role="Role to add")
    async def ticket_add(self,interaction: discord.Interaction, user:discord.member.Member=None, role:discord.role.Role=None):  # noqa: E501
        try:
            overwrites = discord.PermissionOverwrite(
                view_channel=True,
                read_message_history=True,
                send_messages=True,
                attach_files=True,
                embed_links=True,
            )
            if user is None and role is not None:
                await interaction.channel.set_permissions(
                    target=role,
                    overwrite=overwrites,
                )
                await interaction.response.send_message(
                    content=f"Added role {role} to ticket",
                )  # noqa: E501
            elif role is None and user is not None:
                await interaction.channel.set_permissions(
                    target=user,
                    overwrite=overwrites,
                )
                await interaction.response.send_message(
                    content=f"Adding user {user} to ticket",
                )  # noqa: E501
            elif role is not None and user is not None:
                await interaction.response.send_message(
                    content="You can only use one.",
                )
            elif role is None and user is None:
                await interaction.response.send_message(
                    content="You have to choose one stupid.",
                )
            else:
                await interaction.response.send_message(
                    content="Unknown error while parsing values",
                )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Error while running: {e}",
                ephemeral=True,
            )

    @app_commands.command(name="remove",description="Remove user or role from ticket")  # noqa: E501
    @app_commands.describe(user="Member to remove")
    @app_commands.describe(role="Role to remove")
    async def ticket_remove(self,interaction: discord.Interaction, user:discord.member.Member=None, role:discord.role.Role=None):  # noqa: E501, F811
        try:
            if user is None and role is not None:
                await interaction.channel.set_permissions(
                    target=role,
                    overwrite=None,
                )
                await interaction.response.send_message(
                    content=f"Removed role {role} from ticket",
                )  # noqa: E501
            elif role is None and user is not None:
                await interaction.channel.set_permissions(
                    target=user,
                    overwrite=None,
                )
                await interaction.response.send_message(
                    content=f"Removed user {user} from ticket",
                )  # noqa: E501
            elif role is not None and user is not None:
                await interaction.response.send_message(
                    content="You can only use one.",
                )
            elif role is None and user is None:
                await interaction.response.send_message(
                    content="You have to choose one stupid.",
                )
            else:
                await interaction.response.send_message(
                    content="Unknown error while parsing values",
                )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Error while running: {e}",
            )
    @app_commands.command(name = 'panel', description='Launches the ticketing system')  # noqa: E501
    @app_commands.checks.cooldown(3, 60, key = lambda i: (i.guild_id))
    async def ticketing(self,interaction: discord.Interaction, text:str="Hi! If you need help or have a question, don't hesitate to create a ticket."):  # noqa: E501

        '''
        Ticket command

        This will actually launch the ticket system
        '''

        embed = discord.Embed(
            title = text,
            color = discord.Colour.blurple(),
        )
        await interaction.channel.send(embed = embed, view = ticket_launcher())
        await interaction.response.send_message(
            "Ticketing system launched!",
            ephemeral = True,
        )

tree.add_command(ticketing_group())

############################# Admin Essentials #####################################

@tree.command(name="kick", description="Kick a user")
@app_commands.describe(member="User to kick", reason="Reason for kick")
@app_commands.default_permissions(kick_members=True, ban_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):  # noqa: E501

    '''
    Kick command

    Kicks user from guild and let him know why
    '''

    if member == interaction.user or member == interaction.guild.owner:
        return await interaction.response.send_message(
            "You can't kick this user",
            ephemeral=True,
        )

    if member.top_role >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "I can't kick this user",
            ephemeral=True,
        )

    if member.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "You can't kick this user due to role hierarchy",
            ephemeral=True,
        )

    try:
        await member.send(
            embed=discord.Embed(
                description=f"You have been kicked from {interaction.guild.name}\n**Reason**: {reason}",  # noqa: E501
                color=discord.Color.red(),
            ),
        )

    except discord.HTTPException as e:
        await interaction.response.send_message(content=f"UNSEND KICK MESSAGE: {e}")
        logger.warning(f"UNSENT KICK MESSAGE: {e}")

    await member.kick(reason=reason)
    await interaction.response.send_message(
        f"Kicked {member.mention}",
        ephemeral=True,
    )
    embed = discord.Embed(
        description=f"{member.mention} has been kicked\n**Reason**: {reason}",
        color=0x2f3136,
    )
    await interaction.followup.send(embed=embed, ephemeral=False)


@tree.command(name="ban", description="Ban a user")
@app_commands.describe(
    reason="Reason for ban",
    time="Duration of ban",
    member="User to ban",
)
@app_commands.default_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str , time: app_commands.Transform[str, TimeConverter]=None):  # noqa: E501

    '''
    Ban command

    Bans user and let him know why
    '''

    if member == interaction.user or member == interaction.guild.owner:
        return await interaction.response.send_message(
            "You can't ban this user",
            ephemeral=True,
        )

    if member.top_role >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "I can't ban this user",
            ephemeral=True,
        )

    if member.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "You can't ban this user due to role hierarchy",
            ephemeral=True,
        )

    try:
        await member.send(
            embed=discord.Embed(
                description=f"You have been banned from {interaction.guild.name} for {format_timespan(time)}\n**Reason**: {reason}",  # noqa: E501
                color=discord.Color.blurple(),
            ),
        )

    except discord.HTTPException:
        logger.warning("UNSENT BAN MESSAGE")
        await interaction.response.send_message("UNSENT BAN MESSAGE",ephemeral=True)
    await interaction.guild.ban(member, reason=reason)
    await interaction.response.send_message(
        f"Banned {member.mention}",
        ephemeral=True,
    )
    await interaction.followup.send(
        embed=discord.Embed(
            description=f"{member.mention} has been banned for {format_timespan(time)}\n**Reason**: {reason}",  # noqa: E501
            color=0x2f3136,
        ),
        ephemeral=False,
    )

@tree.command(name="unban", description="Unban a user")
@app_commands.describe(member="User to unban", reason="Reason for unban")
@app_commands.default_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, member: discord.User, reason: str):  # noqa: E501

    '''
    Unban Command

    This will unban person
    '''

    try:
        await interaction.guild.unban(member, reason=reason)

    except discord.NotFound:
        return await interaction.response.send_message(
            "This user is not banned",
            ephemeral=True,
        )

    await interaction.response.send_message(
        f"Unbanned {member.mention}",
        ephemeral=True,
    )
    embed = discord.Embed(
        description=f"{member.mention} has been unbanned\n**Reason**: {reason}",
        color=0x2f3136,
    )
    await interaction.followup.send(embed=embed, ephemeral=False)

################################ Giveaway Command ##################################

#TODO logic for all

@app_commands.default_permissions(administrator=True)
class giveaway(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name="giveaway"
        self.description="Giveaway commands"

    @app_commands.command(name="create", description="Create giveaway")
    async def giveaway_create(
        self,
        interaction:discord.Interaction,
        channel:discord.TextChannel,
    ):
        pass

    @app_commands.command(name="reroll",description="Rerolls user")
    async def giveaway_reroll(
        self,
        interaction:discord.Interaction,
        message:str,
    ):
        pass

    @app_commands.command(name="edit",description="Edits giveaway")
    async def giveaway_change(
        self,
        interaction:discord.Interaction,
        message:str,
    ):
        pass

    @app_commands.command(name="remove",description="Removes giveaway.")
    async def giveaway_remove(
        self,
        interaction:discord.Interaction,
        message:str,
    ):
        pass

    @app_commands.command(name="list",description="Lists all running Giveaways.")
    async def giveaway_list(
        self,
        interaction:discord.Interaction,
    ):
        pass
tree.add_command(giveaway())

################################## Music Player ####################################

class music_player(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name="music"
        self.description="Music Player"

    @app_commands.command(name="play",description="Play music")
    async def play(self,interaction:discord.Interaction, query:str):
        try:
            voice_channel = interaction.user.voice.channel
            if voice_channel is None:
                await interaction.response.send_message(
                    "You need to be in a voice channel to use this command!",
                )

            else:
                vc = await voice_channel.connect()
                # Search for the track on SoundCloud
                url = f'http://api.soundcloud.com/tracks?q={query}?client_id=hKP7kcwGL0q6weES7f6X5qOjGnWfyOVX'
                response = requests.get(url,timeout=60)
                logging.debug(response)
                if response.status_code == 200:  # noqa: PLR2004
                    tracks = response.json()
                    if tracks:
                        track = tracks[0]
                        stream_url = track.get('stream_url')
                        if stream_url:
                            await interaction.response.send_message(
                                f'Now playing: {track["title"]}',
                            )
                            voice_channel = interaction.user.voice.channel
                            if voice_channel:
                                voice_client = await voice_channel.connect()
                                voice_client.play(
                                    discord.FFmpegPCMAudio(
                                        stream_url + '?client_id=hKP7kcwGL0q6weES7f6X5qOjGnWfyOVX', # noqa: E501

                                    ),
                                )
                            else:
                                await interaction.response.send_message(
                                    "You need to be in a voice channel to use this command.",  # noqa: E501
                                )
                        else:
                            await interaction.response.send_message(
                                "Track is not available for streaming.",
                            )
                    else:
                        await interaction.response.send_message("No results found.")
                else:
                    await vc.disconnect()
                    await interaction.response.send_message(
                        "Failed to fetch data from SoundCloud.",
                    )
        except Exception as e:
            interaction.response.send_message("Exception: " + e)

    @app_commands.command(name="stop",description="Stop music")
    async def stop(self,interaction:discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("Music stopped!")
        else:
            await interaction.response.send_message(
                "No music is currently playing.",
            )

    @app_commands.command(name="disconnect",description="Disconnects bot from channel")  # noqa: E501
    async def disconnect(self,interaction:discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message(
                "Disconnected from voice channel.",
            )
        else:
            await interaction.response.send_message(
                "I'm not connected to a voice channel.",
            )

tree.add_command(music_player())


################################### CONFIGURE COMMAND ##############################

@app_commands.default_permissions(administrator=True)
class configure_sec(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name="security"
        self.description="Security configurations"

    @app_commands.command(name="anti-invite",description="No invites in the halls")
    async def anti_invites(self,interaction: discord.Interaction,value:bool):
        try:
            gconfig.set(interaction.guild_id,"SECURITY","anti-invite",value=value)
            await interaction.response.send_message(
                content=f"Setted value {str(value)}",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Failed configuring anti-invites: {e}",
            )

@app_commands.default_permissions(administrator=True)
class configure_appear(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name="appearance"
        self.description="Appearance of bot on your server"

    @app_commands.command(name="color",description="Changes default color of embeds.")  # noqa: E501
    @app_commands.describe(color="The color to set")
    @app_commands.autocomplete(color=autocomplete_color)
    async def config_color(self,interaction: discord.Interaction,color:str):
        try:
            gconfig.set(interaction.guild_id,"APPEARANCE","color",value=color)
            await interaction.response.send_message(
                content=f"Setted value {str(color)}",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Exception happened: {e}",
                ephemeral=True,
            )

@app_commands.default_permissions(administrator=True)
class configure_ticketing(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name="ticketing"
        self.description="Configure ticketing options"

    @app_commands.command(name="rewiews",description="Rewiew system")
    async def conf_ticketing_rewiews(
        self,
        interaction:discord.Interaction,
        channel:discord.TextChannel=None,
        value:bool=None,
    ):
        try:
            if channel is not None and value is not None:
                gconfig.set(interaction.guild_id,"Ticketing","reviews-enabled",value=value)
                gconfig.set(interaction.guild_id,"Ticketing","reviews-channel",value=channel)
                await interaction.response.send_message(
                    content=f"Setted value {str(value)},{str(channel)}",
                    ephemeral=True,
                )

            if channel is None and value is not None:
                gconfig.set(interaction.guild_id,"Ticketing","reviews-enabled",value=value)
                await interaction.response.send_message(
                    content=f"Setted value {str(value)}",
                    ephemeral=True,
                )
            if channel is not None and value is None:
                gconfig.set(interaction.guild_id,"Ticketing","reviews-channel",value=channel)
                await interaction.response.send_message(
                    content=f"Setted value {str(channel)}",
                    ephemeral=True,
                )
            if channel is None and value is None:
                await interaction.response.send_message(
                    content="You have to choose",
                    ephemeral=True,
                )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Exception happened: {e}",
                ephemeral=True,
            )
@app_commands.default_permissions(administrator=True)
class configure_members(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name="members"
        self.description="Configure bot actions on user"

    @app_commands.command(
        name="auto-role",
        description="Automatic role on join",
    )
    @app_commands.describe(
        role="Role to add on join",
        enabled="Should it be enabled?")
    async def autorole(self, interaction:discord.Interaction, enabled:bool, role:discord.Role = None):  # noqa: E501
        try:
            gconfig.set(interaction.guild_id,"MEMBERS","autorole-role",role.id)
            gconfig.set(interaction.guild_id,"MEMBERS","autorole-enabled",enabled)
            await interaction.response.send_message(
                content=f"Setted value {str(role.name)}, {str(enabled)}",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Exception happened: {e}",
                ephemeral=True,
            )
@app_commands.default_permissions(administrator=True)
class configure(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name="guildconfig"
        self.description="Config for server"
        self.add_command(configure_sec())
        self.add_command(configure_appear())
        self.add_command(configure_members())
        self.add_command(configure_ticketing())
tree.add_command(configure())

class configure_user(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name="userconfig"
        self.description="User Config"

    @app_commands.command(name="color",description="Default color bot will respond for you")  # noqa: E501
    @app_commands.autocomplete(color=autocomplete_color)
    async def conf_user_def_color(self,interaction:discord.Interaction, color:str):
        try:
            uconfig.set(interaction.user.id,"Appearance","color",color)
            await interaction.response.send_message(
                content=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","value_set").format(values=color),
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Exception happened: {e}",
                ephemeral=True,
            )

    @app_commands.command(
        name="language",
        description="Language the bot will respond to you",
    )
    @app_commands.autocomplete(language=autocomplete_lang)
    async def conf_user_lang(self,interaction:discord.Interaction,language:str):
        try:
            uconfig.set(interaction.user.id,"Appearance","language",language)
            await interaction.response.send_message(
                content=f"Setted value {str(language)}",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                content=f"Exception happened: {e}",
                ephemeral=True,
            )

tree.add_command(configure_user())
####################################################################################

@tree.command(name="slowmode", description="Set slowmode for the channel")
@app_commands.describe(time="Slowmod Time")
@app_commands.default_permissions(manage_channels = True)
async def slowmode(interaction: discord.Interaction,time: app_commands.Transform[str, TimeConverter]=None):  # noqa: E501

    max_time = 21600
    if time <= 0:
        await interaction.channel.edit(slowmode_delay=0)
        await interaction.response.send_message(
            "Slowmode has been disabled",
            ephemeral=True,
        )
        await interaction.channel.send(
            embed=discord.Embed(
                description=f"Slow mode has been disabled by in {interaction.channel.mention}",  # noqa: E501
                color=discord.Color.green(),
            ),
        )

    elif time > max_time:
        await interaction.response.send_message(
            "Slowmode can't be more than 6 hours",
            ephemeral=True,
        )

    else:
        await interaction.channel.edit(slowmode_delay=time)
        await interaction.response.send_message(
            f"Slowmode has been set to {format_timespan(time)} seconds",
            ephemeral=True,
        )
        await interaction.channel.send(
            embed=discord.Embed(
                description=f"Slow mode has been set to {format_timespan(time)} to {interaction.channel.mention}",  # noqa: E501
                color=discord.Color.green(),
            ),
        )

@tree.command(name="clear", description="Clear n messages specific user")
@app_commands.default_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount:int, member: discord.Member = None):  # noqa: E501
    try:
        await interaction.response.defer()
        channel = interaction.channel

        if member is None:
            await channel.purge(limit=amount)
            await interaction.followup.send(
                embed=discord.Embed(
                    description=f"Successfully deleted {amount} messages.",
                    color=discord.Color.green(),
                ),
            )

        elif member is not None:
            await channel.purge(limit=amount)
            await interaction.followup.send(
                embed=discord.Embed(
                    description=f"Successfully deleted {amount} messages from {member.name}",  # noqa: E501
                    color=discord.Color.green(),
                ),
            )
        else:
            await interaction.followup.send(
                content="INTERACTION FAILED",
                ephemeral=True,
            )
    except discord.errors.NotFound:
        await interaction.followup.send(
            content="Removed all that we could, but exception happened",
        )
    except Exception as e:
        await interaction.followup.send(
            content=f"Clear failed!: {e}",
            ephemeral=True,
        )

############################ HELP COMMAND ##########################################
class Help_Pages(discord.ui.View):
    def __init__(self, embeds, *, timeout=180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.total_pages = len(embeds)

    async def send_initial_message(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=self.embeds[self.current_page],
            view=self,
        )

    @discord.ui.button(label='Previous', style=discord.ButtonStyle.primary)
    async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):  # noqa: E501
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page],
                view=self,
            )

    @discord.ui.button(label='Next', style=discord.ButtonStyle.primary)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):  # noqa: E501
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page],
                view=self,
            )

@app_commands.default_permissions(administrator=True)
class Help(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name = "helpadmin"
        self.description = "Help command"

    @app_commands.command(name="configure",description="Configuring help")
    async def help_configure(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="admin",description="Admin help")
    async def help_admin(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="other",description="Other/test commands")
    async def help_other(self,interaction:discord.Interaction):
        pass

@tree.command(name="help", description="User Help")
async def help_user(interaction: discord.Interaction):
    embeds = help_user
    view = Help_Pages(embeds=embeds)
    await view.send_initial_message(interaction)

tree.add_command(Help())
############################ e621.net commands #####################################

class e6_commands(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name = "e6"
        self.description = "e621 Images"
        self.nsfw = True

    @app_commands.command(
        name="random-post",
        description="Gives you random post from e6",
    )
    async def e6_random_post(self,interaction:discord.Interaction,tags:str=""):
        try:
            tags = tags.replace(" ","+")
            url = "https://e621.net/posts.json?limit=100"
            if tags != "":
                url += f"&tags={tags}"
            response = requests.get(
                url,
                timeout=60,
                headers={"User-Agent": "Lorelei-bot"},
            )
            data = response.json()
            if not data["posts"]:
                if tags is not None:
                    await interaction.response.send_message(
                        content=f"No images found for these tags: {tags}",
                    )
                else:
                    await interaction.response.send_message(
                    content="No image found.",
                )
            post = random.choice(data["posts"]) # noqa: S311

            embed = discord.Embed(
                title = f"Post {post['id']}, by {post['tags']['artist']}",
            )
            embed.set_image(url = post["file"]["url"])
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(content=f"Exception: {e}")

tree.add_command(e6_commands())

############################### discord.Views ######################################


class ticket_launcher(discord.ui.View):

    '''
    This will create the ticket
    '''

    def __init__(self) -> None:  # noqa: ANN101
        super().__init__(timeout = None)
        self.cooldown = commands.CooldownMapping.from_cooldown(
            1,
            60,
            commands.BucketType.member,
        )

    @discord.ui.button(
        label = "Open Ticket",
        style = discord.ButtonStyle.blurple,
        custom_id = "ticket_button",
    )
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa: E501, ANN201, ANN101

        interaction.message.author = interaction.user
        retry = self.cooldown.get_bucket(interaction.message).update_rate_limit()

        if retry:
            return await interaction.response.send_message(
                f"Slow down! Try again in {round(retry, 1)} seconds!",
                ephemeral = True,
            )
        ticket = utils.get(
            interaction.guild.text_channels,
            name = f"ticket-for-{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}")  # noqa: E501

        if ticket is not None:
            await interaction.response.send_message(
                f"You already have a ticket open at {ticket.mention}!",
                ephemeral = True,
            )

        else:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(
                    view_channel = False,
                ),
                interaction.user: discord.PermissionOverwrite(
                    view_channel = True,
                    read_message_history = True,
                    send_messages = True,
                    attach_files = True,
                    embed_links = True,
                ),
                interaction.guild.me: discord.PermissionOverwrite(
                    view_channel = True,
                    send_messages = True,
                    read_message_history = True,
                ),
            }
            try:
                channel = await interaction.guild.create_text_channel(
                    name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}",  # noqa: E501
                    overwrites = overwrites,
                    reason = f"Ticket for {interaction.user}",
                )

            except Exception as e:
                return await interaction.response.send_message(
                    f"Ticket creation failed! Make sure I have `manage_channels` permissions! --> {e}",  # noqa: E501
                    ephemeral = True,
                )

            await channel.send(
                f"@everyone, {interaction.user.mention} created a ticket!",
                view = main(),
            )
            await interaction.response.send_message(
                f"I've opened a ticket for you at {channel.mention}!",
                ephemeral = True,
            )

class confirm(discord.ui.View):

    '''
    Ticket confirm embed
    '''

    def __init__(self) -> None:  # noqa: ANN101
        super().__init__(timeout = None)

    @discord.ui.button(
        label = "Confirm",
        style = discord.ButtonStyle.red,
        custom_id = "confirm",
    )
    async def confirm_button(self, interaction:discord.Interaction, button) -> None:  # noqa: ANN101, ANN001
        embed=discord.Embed(
            title=lang.get(interaction.user.id,"TicketingCommand","embed_review_title"),
            description=lang.get(interaction.user.id,"TicketingCommand","embed_review_description"),
        )
        try:
            await interaction.channel.delete()
            if gconfig.get(interaction.guild.id,"Ticketing","reviews-enabled") is True:  # noqa: E501
                await interaction.user.send(embed=embed)

        except discord.Forbidden :
            await interaction.response.send_message(
                content="Channel deletion failed! Make sure I have `manage_channels` permissions!",  # noqa: E501
                ephemeral = True,
            )

class main(discord.ui.View):

    '''
    In-Ticket embed
    '''

    def __init__(self) -> None:  # noqa: ANN101
        super().__init__(timeout = None)

    @discord.ui.button(
        label = "Close Ticket",
        style = discord.ButtonStyle.red,
        custom_id = "close",
    )
    async def close(self, interaction:discord.Interaction, button) -> None:  # noqa: ANN101, ANN001

        embed = discord.Embed(
            title = lang.get(uconfig.get(interaction.user.id, "Appearance","")),
            color = discord.Colour.blurple(),
        )
        await interaction.response.send_message(
            embed = embed,
            view = confirm(),
            ephemeral = True,
        )

    @discord.ui.button(
        label = "Transcript",
        style = discord.ButtonStyle.blurple,
        custom_id = "transcript",
    )
    async def transcript(self, interaction, button):

        await interaction.response.defer()
        if os.path.exists(f"{interaction.channel.id}.md"):
            return await interaction.followup.send(
                "A transcript is already being generated!",
                 ephemeral = True,
            )

        with open(f"{interaction.channel.id}.md", 'a') as f:
            f.write(f"# Transcript of {interaction.channel.name}:\n\n")
            async for message in interaction.channel.history(
                limit = None,
                oldest_first = True,
            ):

                created = datetime.strftime(
                    message.created_at,
                    "%m/%d/%Y at %H:%M:%S",
                )

                if message.edited_at:
                    edited = datetime.strftime(
                        message.edited_at,
                        "%m/%d/%Y at %H:%M:%S",
                    )
                    f.write(
                        f"{message.author} on {created}: {message.clean_content} (Edited at {edited})\n",  # noqa: E501
                    )

                else:
                    f.write(
                        f"{message.author} on {created}: {message.clean_content}\n",
                    )

            generated = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
            f.write(
                f"\n*Generated at {generated} by {bot.user}*\n*Date Formatting: MM/DD/YY*\n*Time Zone: UTC*",  # noqa: E501
            )

        with open(f"{interaction.channel.id}.md", 'rb') as f:
            await interaction.followup.send(
                file = discord.File(
                    f,
                    f"{interaction.channel.name}.md"),
            )

        os.remove(f"{interaction.channel.id}.md")


########################## Main Runner #############################################


if __name__=="__main__":
    with open(".secret.key") as key:
        token = key.read()
    bot.run(token=token)
