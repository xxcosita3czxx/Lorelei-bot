from discord import app_commands
import discord
import logging
import utils.cosita_toolkit as ctkit
logging.basicConfig(filename='bot.log', encoding='utf-8',format='%(asctime)s : %(levelname)s >> %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)


## vars
help_list="""**HELP**
<< UL1T9 >> 
help = /help
ping = /ping
<< T3ST1NG >>
test = /test
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

with open(".secret.key", "r") as key:
    token = key.read()

bot.run(token=token)
