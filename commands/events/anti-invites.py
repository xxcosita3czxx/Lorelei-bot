
#TODO Anybody with manage-messages permissions shouldnt have deleted invites/links
#TODO Antilinks deleting everything
import logging

import discord
from discord.ext import commands

from utils.configmanager import gconfig, lang, uconfig


class AntiInvites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def antiinvites(self,message:discord.Message):
        try:
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
                    logging.debug(message.author)
                    if message.author == self.bot.user:
                        return
                    #if message.author.guild_permissions.administrator:
                    #    return
                    if 'discord.gg' in message.content:
                        try:
                            await message.delete()
                            await message.author.send(
                                content=lang.get(ulanguage,"Responds","no_invites"),
                            )

                        except discord.Forbidden:
                            await message.channel.send("I dont have permissions to remove invites!")  # noqa: E501
                            logging.debug(f"Anti-invites no permission on {str(message.guild)}")  # noqa: E501
                        except Exception as e:
                            await message.channel.send(f"Unknown error: {e}")
                else:
                    logging.debug("anti-invite disabled")
        except Exception as e:
            logging.warning(f"Unknown error in anti-invites: \n{e}")

    @commands.Cog.listener("on_message")
    async def antilinks(self,message:discord.Message):
        try:
            logging.debug("on_message was triggered")
            ulanguage = uconfig.get(message.author.id,"Appearance","language")
            if message.guild:
                guild_id = message.guild.id
                logging.debug(message.guild)
                logging.debug(guild_id)
                if gconfig.get(str(guild_id),"SECURITY","anti-links") is True:
                    logging.debug("Anti-links Status:"+str(
                        gconfig.get(str(guild_id),"SECURITY","anti-links")),
                    )
                    if message.author == self.bot.user:
                        return
#                    if message.author.guild_permissions.administrator:
#                        return
                    if 'https://' in message.content.lower() or "http://" in message.content.lower() or "www." in message.content.lower():  # noqa: SIM222, E501
                        try:
                            await message.delete()
                            await message.author.send(
                                content=lang.get(
                                    ulanguage,
                                    "Responds",
                                    "no_links",
                                ).format(author=message.author.mention),
                            )

                        except discord.Forbidden:
                            await message.channel.send("I dont have permissions to remove links!")  # noqa: E501
                            logging.debug(f"Anti-links no permission on {str(message.guild)}")  # noqa: E501
                        except Exception as e:
                            await message.channel.send(f"Unknown error: {e}")
                else:
                    logging.debug("anti-links disabled")
        except Exception as e:
            logging.warning(f"Unknown error in anti-links: \n{e}")

async def setup(bot:commands.Bot):
    await bot.add_cog(AntiInvites(bot))
