from discord import app_commands
import discord
import logging
import utils.cosita_toolkit as ctkit
import coloredlogs

coloredlogs.install(level='INFO', fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

## vars
help_list="""
"""
status=discord.Status.dnd
##
class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        await bot.change_presence(status=status)
        logging.info("Bot ready, logged in!")
bot = aclient()
tree = app_commands.CommandTree(bot)


@tree.command(name="ping", description="Lets play ping pong")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('Pong! {0}'.format(round(bot.latency, 1)))
    
    
@tree.command(name="help", description="All the commands at one place")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(help_list)

@tree.command()
async def setup_ticket_system(ctx):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True)
    }

    category = await ctx.guild.create_category_channel('Tickets', overwrites=overwrites)
    ticket_instructions = await ctx.send("React to this message to open a ticket!")

    await ticket_instructions.add_reaction('🎫')

@tree.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    if str(reaction.emoji) == '🎫':
        category = discord.utils.get(user.guild.categories, name='Tickets')
        ticket_channel = await category.create_text_channel(f'ticket-{user.display_name}')
        await ticket_channel.set_permissions(user, read_messages=True)
        await ticket_channel.send(f'{user.mention}, your ticket has been created!')

with open(".secret.key", "r") as key:
    token = key.read()

bot.run(token=token)
