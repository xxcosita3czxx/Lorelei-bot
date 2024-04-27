import discord, os
from datetime import datetime
from discord import app_commands, utils
from discord.ext import commands
import logging
import coloredlogs
import asyncio
import re
from humanfriendly import format_timespan
coloredlogs.install(level="DEBUG", fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

## vars
help_list="""
# HELP
> Utilities
/help - shows this help
/ping - pings the bot if its alive
> Administrator
/ban <user> <reason> - bans person
/kick - <user <reason> - kicks person
/ticket - Creates ticket panel
/slowmod <time> - sets slowmode
"""
status=discord.Status.dnd
##
time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
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
async def change_status():
    while True:
        await bot.change_presence(activity=discord.Game(name="Some chords"),status=status)
        await asyncio.sleep(5)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="to /help"),status=status)
        await asyncio.sleep(5)
class aclient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents = intents)
        self.synced = False #we use this so the bot doesn't sync commands more than once
        self.added = False
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced: #check if slash commands have been synced 
            await tree.sync() #guild specific: leave blank if global (global registration can take 1-24 hours)
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
    def __init__(self) -> None:
        super().__init__(timeout = None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.member)
    
    @discord.ui.button(label = "Create a Ticket", style = discord.ButtonStyle.blurple, custom_id = "ticket_button")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        interaction.message.author = interaction.user
        retry = self.cooldown.get_bucket(interaction.message).update_rate_limit()
        if retry: return await interaction.response.send_message(f"Slow down! Try again in {round(retry, 1)} seconds!", ephemeral = True)
        ticket = utils.get(interaction.guild.text_channels, name = f"ticket-for-{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}")
        if ticket is not None: await interaction.response.send_message(f"You already have a ticket open at {ticket.mention}!", ephemeral = True)
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
    def __init__(self) -> None:
        super().__init__(timeout = None)
        
    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.red, custom_id = "confirm")
    async def confirm_button(self, interaction, button):
        try: await interaction.channel.delete()
        except: await interaction.response.send_message("Channel deletion failed! Make sure I have `manage_channels` permissions!", ephemeral = True)

class main(discord.ui.View):
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
    await interaction.response.send_message('Pong! {0}'.format(round(bot.latency, 1)))
    
    
@tree.command(name="help", description="All the commands at one place")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(help_list)


@tree.command(name = 'ticket', description='Launches the ticketing system') #guild specific slash command
@app_commands.default_permissions(manage_guild = True)
@app_commands.checks.cooldown(3, 60, key = lambda i: (i.guild_id))
@app_commands.checks.bot_has_permissions(manage_channels = True)
async def ticketing(interaction: discord.Interaction):
    embed = discord.Embed(title = "If you need support, click the button below and create a ticket!", color = discord.Colour.blue())
    await interaction.channel.send(embed = embed, view = ticket_launcher())
    await interaction.response.send_message("Ticketing system launched!", ephemeral = True)


# kick and ban
@tree.command(name="kick", description="Kick a user")
@app_commands.describe(member="User to kick", reason="Reason for kick")
@app_commands.default_permissions(kick_members=True, ban_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    if member == interaction.user or member == interaction.guild.owner:
        return await interaction.response.send_message("You can't kick this user", ephemeral=True)
    if member.top_role >= interaction.guild.me.top_role:
        return await interaction.response.send_message("I can't kick this user", ephemeral=True)
    if member.top_role >= interaction.user.top_role:
        return await interaction.response.send_message("You can't kick this user due to role hierarchy", ephemeral=True)
    try:
        await member.send(embed=discord.Embed(description=f"You have been kicked from {interaction.guild.name}\n**Reason**: {reason}", color=discord.Color.red()))
    except discord.HTTPException:
        pass
    await member.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {member.mention}", ephemeral=True)
    embed = discord.Embed(description=f"{member.mention} has been kicked\n**Reason**: {reason}", color=0x2f3136)
    await interaction.followup.send(embed=embed, ephemeral=False)


@tree.command(name="ban", description="Ban a user")
@app_commands.describe(reason="Reason for ban", time="Duration of ban", member="User to ban")
@app_commands.default_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str , time: app_commands.Transform[str, TimeConverter]=None):
    if member == interaction.user or member == interaction.guild.owner:
        return await interaction.response.send_message("You can't ban this user", ephemeral=True)
    if member.top_role >= interaction.guild.me.top_role:
        return await interaction.response.send_message("I can't ban this user", ephemeral=True)
    if member.top_role >= interaction.user.top_role:
        return await interaction.response.send_message("You can't ban this user due to role hierarchy", ephemeral=True)
    
    try:
        await member.send(embed=discord.Embed(description=f"You have been banned from {interaction.guild.name} for {format_timespan(time)}\n**Reason**: {reason}", color=0x2f3136))
    except discord.HTTPException:
        pass
        
    await interaction.guild.ban(member, reason=reason)
    await interaction.response.send_message(f"Banned {member.mention}", ephemeral=True)
    await interaction.followup.send(embed=discord.Embed(description=f"{member.mention} has been banned for {format_timespan(time)}\n**Reason**: {reason}", color=0x2f3136), ephemeral=False)

@tree.command(name="unban", description="Unban a user")
@app_commands.describe(member="User to unban", reason="Reason for unban")
@app_commands.default_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, member: discord.User, reason: str):
    try:
        await interaction.guild.unban(member, reason=reason)
    except discord.NotFound:
        return await interaction.response.send_message("This user is not banned", ephemeral=True)
    await interaction.response.send_message(f"Unbanned {member.mention}", ephemeral=True)
    embed = discord.Embed(description=f"{member.mention} has been unbanned\n**Reason**: {reason}", color=0x2f3136)
    await interaction.followup.send(embed=embed, ephemeral=False)

@tree.command(name="slowmode", description="Set slowmode for the channel")
@app_commands.describe(time="Slowmod Time")
async def slowmode(interaction: discord.Interaction, time: app_commands.Transform[str, TimeConverter]=None):
    if time <= 0:
        await interaction.channel.edit(slowmode_delay=0)
        await interaction.response.send_message("Slowmode has been disabled", ephemeral=True)
        await interaction.channel.send(embed=discord.Embed(description=f"Slow mode has been disabled by in {interaction.channel.mention}", color=discord.Color.green()))
    elif time > 21600:
        await interaction.response.send_message("Slowmode can't be more than 6 hours", ephemeral=True)
    else:
        await interaction.channel.edit(slowmode_delay=time)
        await interaction.response.send_message(f"Slowmode has been set to {format_timespan(time)} seconds", ephemeral=True)
        await interaction.channel.send(embed=discord.Embed(description=f"Slow mode has been set to {format_timespan(time)} to {interaction.channel.mention}", color=discord.Color.green()))
with open(".secret.key", "r") as key:
    token = key.read()

bot.run(token=token)
