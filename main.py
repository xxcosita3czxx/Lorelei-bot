import asyncio
import logging
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import List

import coloredlogs
import discord
import toml
from discord import app_commands, utils
from discord.ext import commands
from humanfriendly import format_timespan

import config

coloredlogs.install(
    level=config.loglevel,
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

help_user1=discord.Embed(
    title="User Help",
    description="Page 1",
)

help_user = [help_user1]


logger = logging.getLogger(__name__)
time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
info_text="""
Hello!
This is Lorelei Bot developed by cosita3cz.
And constributor Apoliak.
Developed in python for everyone.
"""
conflang=config.language
class ConfigManager:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.config = defaultdict(dict)
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
        logging.debug("Result is: "+result)
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
lang = ConfigManager("data/lang")

async def autocomplete_color(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:  # noqa: E501
    colors = ['Blurple', 'Red', 'Green', 'Blue', 'Yellow',"Purple","White"]
    return [app_commands.Choice(name=color, value=color) for color in colors if current.lower() in color.lower()]  # noqa: E501

async def autocomplete_lang(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:  # noqa: E501
    languages = ["en","cz","sk"]
    return [app_commands.Choice(name=language, value=language) for language in languages if current.lower() in language.lower()]  # noqa: E501

async def change_status() -> None:
    while True:
        await bot.change_presence(
            activity=discord.Game(name="Some chords"),
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
                    content=f"{message.author.mention} Don't send invites!",
                )
        else:
            logging.debug("anti-invite disabled")
            return
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
                        conflang,
                        "Responds",
                        "no_links",
                    ).format(author=message.author.mention),
                )
        else:
            logging.debug("anti_links disabled")
            return
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

    embed.add_field(
        name="Username",
        value=member.name,
        inline=True,
    )

    embed.add_field(
        name="Display Name",
        value=member.display_name,
        inline=True,
    )

    embed.add_field(
        name="ID",
        value=member.id,
        inline=True,
    )

    embed.add_field(
        name="Joined Discord",
        value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=True,
    )

    embed.add_field(
        name="Joined Server",
        value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=True,
    )

    embed.add_field(
        name="Roles",
        value=", ".join([role.name for role in member.roles]),
        inline=False,
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )



@tree.command(name="info", description="Info about bot")
async def info(interaction: discord.Interaction):
    '''Help command
    Will let user know what all can he do
    '''
    embed = discord.Embed(
        title="Lorelei-bot",
        description=info_text,
        color=discord.colour.Color.blurple(),
    )

    await interaction.response.send_message(
        embed=embed,
    )

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
    async def confirm_button(self, interaction, button) -> None:  # noqa: ANN101, ANN001

        try:
            await interaction.channel.delete()

        except discord.Forbidden :
            await interaction.response.send_message(
                "Channel deletion failed! Make sure I have `manage_channels` permissions!",  # noqa: E501
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
    async def close(self, interaction, button) -> None:  # noqa: ANN101, ANN001

        embed = discord.Embed(
            title = "Are you sure you want to close this ticket?",
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

@tree.command(name="ping", description="Lets play ping pong")
async def ping(interaction: discord.Interaction):

    '''
    Pings the user
    '''

    await interaction.response.send_message(
        f'Pong! {round(bot.latency, 1)}',
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

####################################################################################

# kick and ban
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

    except discord.HTTPException:
        logger.warning("UNSENT KICK MESSAGE")

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
################################ Giveaway Command ##################################

#TODO logic for all

@app_commands.default_permissions(administrator=True)
class giveaway(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name="giveaway"
        self.description="Giveaway commands"

    @app_commands.command(name="create", description="Create giveaway")
    async def giveaway_create(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="reroll",description="Rerolls user")
    async def giveaway_reroll(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="edit",description="Edits giveaway")
    async def giveaway_change(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="remove",description="Removes giveaway.")
    async def giveaway_remove(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="list",description="Lists all running Giveaways.")
    async def giveaway_list(self,interaction:discord.Interaction):
        pass
tree.add_command(giveaway())

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
            gconfig.set(interaction.user.id,"Appearance","color",color)
            await interaction.response.send_message(
                content=f"Setted value {str(color)}",
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
    async def conf_user_lang(self,interaction:discord.Interaction,language:str):
        try:
            gconfig.set(interaction.user.id,"Appearance","language",language)
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

class Help(app_commands.Group):
    def __init__(self):
        super().__init__()
        self.name = "help"
        self.description = "Help command"

    @app_commands.command(name="user", description="User Help")
    async def help_user(self, interaction: discord.Interaction):
        embeds = help_user
        view = Help_Pages(embeds=embeds)
        await view.send_initial_message(interaction)

    @app_commands.command(name="configure",description="Configuring help")
    async def help_configure(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="admin",description="Admin help")
    async def help_admin(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="other",description="Other/test commands")
    async def help_other(self,interaction:discord.Interaction):
        pass


tree.add_command(Help())
####################################################################################

@tree.command(name="user-info",description="Info about user")
async def user_info(interaction: discord.Interaction, member:discord.User):
    logger.debug(member.display_avatar.key)
    embed = discord.Embed(title="Info about", color=discord.Color.blurple())
    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(
        name="Username",
        value=member.name,
        inline=True,
    )

    embed.add_field(
        name="Display Name",
        value=member.display_name,
        inline=True,
    )

    embed.add_field(
        name="ID",
        value=member.id,
        inline=True,
    )

    embed.add_field(
        name="Joined Discord",
        value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=True,
    )

    embed.add_field(
        name="Joined Server",
        value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=True,
    )

    embed.add_field(
        name="Roles",
        value=", ".join([role.name for role in member.roles]),
        inline=False,
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )

if __name__=="__main__":
    with open(".secret.key") as key:
        token = key.read()
    bot.run(token=token)
