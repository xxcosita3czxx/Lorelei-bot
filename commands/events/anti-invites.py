import logging

import discord
from discord.ext import commands

from utils.configmanager import gconfig, lang, uconfig


class AntiInvites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


@commands.Cog.listener()
async def on_message(self,message:discord.Message):
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
            if message.author == self.bot.user:
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
            if message.author == self.bot.user:
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

async def setup(bot:commands.Bot):
    await bot.add_cog(AntiInvites(bot))
