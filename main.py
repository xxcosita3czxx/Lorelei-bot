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

@tree.command(name="Setup Ticket System", description="Setups ticket system")
async def setup_ticket_system(interaction: discord.Interaction):
    pass  

with open(".secret.key", "r") as key:
    token = key.read()

bot.run(token=token)
