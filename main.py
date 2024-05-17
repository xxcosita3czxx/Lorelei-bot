import discord, os
from datetime import datetime
from discord import app_commands, utils
from discord.ext import commands
import logging
import coloredlogs
import asyncio
import config
import re
from humanfriendly import format_timespan
import yt_dlp as youtube_dl
from discord.utils import get
import pyttsx3

coloredlogs.install(level=config.loglevel, fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

help_list="""
# HELP
> Utilities
/help - shows this help
/ping - pings the bot if its alive
/giveaway - starts a giveaway
/ai - ask a question and get an answer
"""

engine = pyttsx3.init()

async def change_status():
    while True:
        await bot.change_presence(activity=discord.Game(name="Some chords"),status=config.status)
        await asyncio.sleep(5)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"),status=config.status)
        await asyncio.sleep(5)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="TESTINGS"),status=config.status)
        await asyncio.sleep(5)

class TimeConverter(app_commands.Transformer):

    async def transform(self, interaction: discord.Interaction, argument: str) -> int:

        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0

        for key, value in matches:

            try:
                time += time_dict[value] * float(key)

            except KeyError:
                raise app_commands.BadArgument(f"{value} is an invalid time key! h|m|s|d are valid arguments")

            except ValueError:
                raise app_commands.BadArgument(f"{key} is not a number!")

        return round(time)

class aclient(discord.Client):

    '''
    Main Client proccess

    This connects the bot to discord
    '''

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        super().__init__(intents = intents)
        self.synced = False
        self.added = False

    async def on_ready(self):

        await self.wait_until_ready()

        if not self.synced:
            await tree.sync()
            self.synced = True

        if not self.added:
            self.add_view(ticket_launcher())
            self.add_view(main())
            self.added = True

        logger.info(f"We have logged in as {self.user}.")
        await change_status()

bot = aclient()
tree = app_commands.CommandTree(bot)

class ticket_launcher(discord.ui.View):

    '''
    This will create the ticket
    '''

    def __init__(self) -> None:
        super().__init__(timeout = None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.member)

    @discord.ui.button(label = "Open Ticket", style = discord.ButtonStyle.blurple, custom_id = "ticket_button")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        interaction.message.author = interaction.user
        retry = self.cooldown.get_bucket(interaction.message).update_rate_limit()

        if retry:
            return await interaction.response.send_message(f"Slow down! Try again in {round(retry, 1)} seconds!", ephemeral = True)
        ticket = utils.get(interaction.guild.text_channels, name = f"ticket-for-{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}")

        if ticket is not None:
            await interaction.response.send_message(f"You already have a ticket open at {ticket.mention}!", ephemeral = True)

        else:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                interaction.user: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True), 
            }
            try: 
                channel = await interaction.guild.create_text_channel(name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}", overwrites = overwrites, reason = f"Ticket for {interaction.user}")

            except Exception as e: 
                return await interaction.response.send_message(f"Ticket creation failed! Make sure I have `manage_channels` permissions! --> {e}", ephemeral = True)

            await channel.send(f"@everyone, {interaction.user.mention} created a ticket!", view = main())
            await interaction.response.send_message(f"I've opened a ticket for you at {channel.mention}!", ephemeral = True)

class confirm(discord.ui.View):

    '''
    Ticket confirm embed
    '''

    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.red, custom_id = "confirm")
    async def confirm_button(self, interaction, button):

        try:
            await interaction.channel.delete()

        except:
            await interaction.response.send_message("Channel deletion failed! Make sure I have `manage_channels` permissions!", ephemeral = True)

class main(discord.ui.View):

    '''
    In-Ticket embed
    '''

    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label = "Close Ticket", style = discord.ButtonStyle.red, custom_id = "close")
    async def close(self, interaction, button):

        embed = discord.Embed(title = "Are you sure you want to close this ticket?", color = discord.Colour.blurple())
        await interaction.response.send_message(embed = embed, view = confirm(), ephemeral = True)

    @discord.ui.button(label = "Transcript", style = discord.ButtonStyle.blurple, custom_id = "transcript")
    async def transcript(self, interaction, button):

        await interaction.response.defer()
        if os.path.exists(f"{interaction.channel.id}.md"):
            return await interaction.followup.send(f"A transcript is already being generated!", ephemeral = True)

        with open(f"{interaction.channel.id}.md", 'a') as f:
            f.write(f"# Transcript of {interaction.channel.name}:\n\n")
            async for message in interaction.channel.history(limit = None, oldest_first = True):

                created = datetime.strftime(message.created_at, "%m/%d/%Y at %H:%M:%S")

                if message.edited_at:
                    edited = datetime.strftime(message.edited_at, "%m/%d/%Y at %H:%M:%S")
                    f.write(f"{message.author} on {created}: {message.clean_content} (Edited at {edited})\n")

                else:
                    f.write(f"{message.author} on {created}: {message.clean_content}\n")

            generated = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
            f.write(f"\n*Generated at {generated} by {bot.user}*\n*Date Formatting: MM/DD/YY*\n*Time Zone: UTC*")

        with open(f"{interaction.channel.id}.md", 'rb') as f:
            await interaction.followup.send(file = discord.File(f, f"{interaction.channel.name}.md"))

        os.remove(f"{interaction.channel.id}.md")

@tree.command(name="ping", description="Lets play ping pong")
async def ping(interaction: discord.Interaction):

    '''
    Pings the user
    '''

    await interaction.response.send_message('Pong! {0}'.format(round(bot.latency, 1)))

@tree.command(name="help", description="All the commands at one place")
async def help(interaction: discord.Interaction):

    '''
    Help command

    Will let user know what all can he do
    '''

    await interaction.response.send_message(help_list)

@tree.command(name="giveaway", description="Start a giveaway")
@app_commands.describe(prize="The prize for the giveaway", duration="Duration of the giveaway in seconds")
async def giveaway(interaction: discord.Interaction, prize: str, duration: int):
    
    '''
    Giveaway command

    Starts a giveaway
    '''

    embed = discord.Embed(title="🎉 Giveaway 🎉", description=f"Prize: **{pr
