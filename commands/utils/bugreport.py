import logging
import time
from collections import deque

import discord
from discord import app_commands
from discord.ext import commands

import config
from commands.utils.help import HelpManager  # noqa: F401
from utils.configmanager import lang, uconfig

last_logs = deque(maxlen=60)
class LastLogsHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        last_logs.append(log_entry)

# Add the custom handler to the root logger
logger = logging.getLogger("bugreport")
handler = LastLogsHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(handler)

class BugReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="bugreport",description="Here you can report bug")
    @app_commands.checks.cooldown(1, 45, key=lambda i: (i.guild_id, i.user.id))
    async def bugreport(self,interaction: discord.Interaction, command:str,explanation:str):  # noqa: E501
        nosave:bool=False
        if nosave:
            logger.info("-----LAST LOGS-----")
            last_logs_final = last_logs
            for line in list(last_logs_final):
                logger.info(line+"\n")
            logger.info("-----END OF LAST LOGS-----")
            await interaction.response.send_message(lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","report_sent"), ephemeral=True)  # noqa: E501
        elif config.bugreport:
            try:
                local_time = time.localtime()
                formatted_time = time.strftime("%Y-%m-%d_%H-%M-%S", local_time)
                with open(f"data/bug-reports/bugreport-{command}-{interaction.guild.id}-{interaction.user.name}-{interaction.user.id}-{formatted_time}.txt", mode="w") as f:  # type: ignore # noqa: E501
                    f.write(f"Reported by: {interaction.user.name}\n")
                    f.write(f"Reported at: {formatted_time}\n")
                    f.write(f"Command: {command}\n")
                    f.write(f"User explanation: {explanation}\n")
                    f.write("\n")
                    f.write("Last 60 logs\n")
                    for line in last_logs:
                        f.write(line+"\n")
                    f.write("End of logs.\n")
                    f.write(f"Happened on server: {interaction.guild.name}\n") # type: ignore
                    f.write(f"Channel: {interaction.channel.id}\n") # type: ignore
                    f.write(f"User permissions: {interaction.user.guild_permissions}\n")  # type: ignore # noqa: E501
                    f.write(f"Bots permissions on server: {interaction.app_permissions}\n")  # noqa: E501
                    f.write("End of report.\n")
                    f.close()
                await interaction.response.send_message(lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","report_sent"), ephemeral=True)  # noqa: E501
                try:
                    await interaction.client.get_channel(config.bugreport_channel).send(content=f"New bug report submitted by {interaction.user.mention} in server {interaction.guild.name} (ID: {interaction.guild.id}) for command '{command}'. Explanation: {explanation}", file=discord.File(f"data/bug-reports/bugreport-{command}-{interaction.guild.id}-{interaction.user.name}-{interaction.user.id}-{formatted_time}.txt"))  # type: ignore # noqa: E501
                except Exception as e:
                    logger.error(f"Could not send bugreport to channel: {e}")
            except commands.errors.CommandOnCooldown as e:
                await interaction.response.send_message(e)  # noqa: E501
            except Exception as e:
                await interaction.response.send_message(lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","report_error").format(e=e),ephemeral=True)  # noqa: E501
        else:
            await interaction.response.send_message(lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","report_disabled"), ephemeral=True)  # noqa: E501

async def setup(bot:commands.Bot):
    hm = HelpManager()
    hmhelp = hm.new_help("other","bugreport","Report a bug")
    hmhelp.set_help_page(1,"BugReport","This command can be used to report a bug or any feature that is broken.\n There is also a optional flag 'nosave'. Please dont use it to report as it just prints the logs into the console where it gets lost after some time. \n ## Usage \n/bugreport <command> <explanation>")  # noqa: E501
    cog = BugReport(bot=bot)
    await bot.add_cog(cog)
