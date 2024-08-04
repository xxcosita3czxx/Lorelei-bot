#############################
#    By Cosita              #
#############################
#TODO Welcome system
#TODO Giveaway logic
#TODO !!! Coging and cleaning !!! TODO



import asyncio
import logging
import os

import coloredlogs
import discord
import discord.ext
import discord.ext.commands
from discord import app_commands

import config
import utils.help_embeds as help_pages
from utils.configmanager import gconfig, lang, uconfig

coloredlogs.install(
    level=config.loglevel,
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
conflang=config.language

logger = logging.getLogger(__name__)

async def load_cogs(directory,bot):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                cog_path = os.path.relpath(os.path.join(root, file), directory)
                module_name = cog_path.replace(os.sep, '.').replace('.py', '')
                try:
                    await bot.load_extension(f'{directory}.{module_name}')
                    logger.info(f"Loaded {module_name}")
                except Exception as e:
                    logger.error(f'Failed to load {module_name}: {e}')

async def change_status() -> None:
    while True:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="Some Chords...",
            ),
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
                name="/info",
            ),
            status=config.status,
        )
        logging.debug(lang.get(conflang,"Bot","debug_status_chng"))
        await asyncio.sleep(5)

#########################################################################################

class aclient(discord.ext.commands.Bot):

    '''
    Main Client proccess

    This connects the bot to discord
    '''

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents = intents,command_prefix=".")
        self.synced = False
        self.added = False

    async def on_ready(self) -> None:

        await self.wait_until_ready()

        if not self.synced:
            # Not sure if it should be also on start?
            await bot.tree.sync()
            await load_cogs(bot=self,directory="commands")
            await bot.tree.sync()
            logger.info("Synced!")
            self.synced = True

        if not self.added:
            logger.info("Added views")
            self.added = True

        await change_status()
        logger.info(lang.get(conflang,"Bot","info_logged").format(user=self.user))

bot = aclient()
tree = bot.tree
# just to be sure bcs context commands with this version of client also works
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
            logging.debug("anti-links disabled")
@bot.event
async def on_member_join(member:discord.Member):
    logging.debug("on_member_join was triggered!")
    logging.debug(str(member.guild) + " / " + str(member.guild.id))
    if gconfig.get(str(member.guild.id),"MEMBERS","autorole-enabled") is True:
        role_id = gconfig.get(str(member.guild.id),"MEMBERS","autorole-role")
        logging.debug("Role_id:"+str(role_id))
        role = member.guild.get_role(role_id)
        await member.add_roles(role)

############################ Basic ##############################################

############################# Admin Essentials #####################################


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
        duration:int,
        winners:int,
        title:str,
        description:str,
    ):
        view = giveaway_open()
        await view.create(interaction,channel,title,description,winners)
        await interaction.response.send_message(
            content="Giveaway created!",
            ephemeral=True,
        )

    @app_commands.command(name="reroll",description="Rerolls user")
    async def giveaway_reroll(
        self,
        interaction:discord.Interaction,
        message:str,
    ):
        pass

    @app_commands.command(name="edit",description="Edits giveaway")
    async def giveaway_edit(
        self,
        interaction:discord.Interaction,
        message:str,
        title:str,
        description:str,
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
        embeds = help_pages.help_user
        view = Help_Pages(embeds=embeds)
        await view.send_initial_message(interaction)

    @app_commands.command(name="other",description="Other/test commands")
    async def help_other(self,interaction:discord.Interaction):
        pass

@tree.command(name="help", description="User Help")
async def help_user(interaction: discord.Interaction):
    embeds = help_pages.help_user
    view = Help_Pages(embeds=embeds)
    await view.send_initial_message(interaction)

tree.add_command(Help())

############################### discord.Views ######################################

class giveaway_open(discord.ui.View):
    def __init__(self) -> None:  # noqa: ANN101
        super().__init__(timeout = None)

    async def create(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title,
        desc,
        win,
    ):
        embed = discord.Embed(
            title = title,
            description = desc,
        )
        embed.add_field(
            name="Winners",
            value=str(win),
        )
        await channel.send(embed=embed, view=self)

    @discord.ui.button(
        label = "Join",
        style = discord.ButtonStyle.blurple,
        custom_id = "join",
    )
    async def join_giv(self,interaction: discord.Interaction, button: discord.Button): # noqa: E501
        await interaction.response.send_message(content="Joined!",ephemeral=True)

########################## Main Runner #############################################


if __name__=="__main__":
    with open(".secret.key") as key:
        token = key.read()
    bot.run(token=token)
