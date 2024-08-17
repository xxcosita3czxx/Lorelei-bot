import logging
import time
from collections import deque

import discord
from discord import app_commands
from discord.ext import commands

import config

last_logs = deque(maxlen=50)
class LastLogsHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        last_logs.append(log_entry)

# Add the custom handler to the root logger
handler = LastLogsHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(handler)

class BugReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="bugreport",description="Here you can report bug")
    @app_commands.checks.cooldown(1, 45, key=lambda i: (i.guild_id, i.user.id))
    async def bugreport(self,interaction: discord.Interaction, command:str,explanation:str):  # noqa: E501
        if config.bugreport:
            try:
                local_time = time.localtime()
                formatted_time = time.strftime("%Y-%m-%d_%H-%M-%S", local_time)
                with open(f"data/bug-reports/bugreport-{interaction.guild.id}-{interaction.user.id}-{formatted_time}.txt", mode="w") as f:  # noqa: E501
                    f.write(f"Reported by: {interaction.user.name}\n")
                    f.write(f"Reported at: {time.localtime()}\n")
                    f.write(f"Command: {command}\n")
                    f.write(f"User explanation: {explanation}\n")
                    f.write("\n")
                    f.write("Last 30 logs\n")
                    for line in last_logs:
                        f.write(line+"\n")
                    f.write("End of logs.\n")
                    f.write(f"Happened on server: {interaction.guild.name}\n")
                    f.write(f"Channel: {interaction.channel.id}\n")
                    f.write(f"User permissions: {interaction.user.guild_permissions}\n")  # noqa: E501
                    f.write(f"Bots permissions on server: {interaction.app_permissions}\n")  # noqa: E501
                    f.write("End of report.\n")
            except Exception as e:
                await interaction.response.send_message(f"There was error while making bugreport. Please report on Support server or github. \nError: {e}",ephemeral=True)  # noqa: E501
        else:
            await interaction.response.send_message("Bug reports disabled in config.", ephemeral=True)  # noqa: E501

async def setup(bot:commands.Bot):
    cog = BugReport(bot=bot)
    await bot.add_cog(cog)
