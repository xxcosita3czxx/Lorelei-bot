import logging
import random

import discord
import requests
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_tags
from utils.configmanager import uconfig
from utils.guildconfig import GuildConfig

logger_e6 = logging.getLogger("nsfw.e621")
class E6_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class e6_commands(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "e6"
            self.description = "e621 Images"
            self.nsfw = True

        @app_commands.command(
            name="random-post",
            description="Gives you random post from e6",
        )
        @app_commands.autocomplete(tags=autocomplete_tags)
        async def e6_random_post(self,interaction:discord.Interaction,tags:str="",web:str=uconfig.get("NSFW","E621","web","https://e621.net")):  # type: ignore  # noqa: E501
            try:
                tags = tags.replace(" ","+")
                if web.endswith("/"):
                    web[:-1]
                if not web.startswith("http"):
                    web = "https://" + web
                url = f"{web}/posts.json?limit=100"
                if tags != "":
                    url += f"&tags={tags}"
                response = requests.get(
                    url,
                    timeout=60,
                    headers={"User-Agent": "Lorelei-bot"},
                )
                data = response.json()
                if not data["posts"]:
                    await interaction.response.send_message(
                        content="Nobody here but us chickens!",
                    )
                #post = random.choice(data["posts"]) # noqa: S311

                posts = data["posts"]
                current_index = random.randint(0, len(posts) - 1)  # Start with a random post  # noqa: E501, S311

                embed, video_url = self.create_embed(posts[current_index])
                file_url = posts[current_index]["file"].get("url")
                if file_url and file_url.endswith((".mp4", ".webm")) and not uconfig.get("NSFW", "E621", "preview", False):  # noqa: E501
                    await interaction.response.send_message(
                        content=f"Video: {file_url}",
                        embed=embed,
                        view=E6_commands.e6_view(posts, current_index),
                    )
                else:
                    await interaction.response.send_message(
                        embed=embed,
                        view=E6_commands.e6_view(posts, current_index),
                    )
            except Exception as e:
                await interaction.response.send_message(content=f"Exception: {e}")

        def create_embed(self, post):
            embed = discord.Embed(
                title=f"Post {post['id']}, by {', '.join(post['tags']['artist'])}",
                url=f"https://e621.net/posts/{post['id']}",
            )
            video_url = None
            file_url = post["file"]["url"]
            if file_url.endswith((".mp4", ".webm")):
                if uconfig.get("NSFW", "E621", "preview", False) is True:
                    video_url = file_url
                    # Discord does not support direct video embedding, but you can use set_image for a preview thumbnail if available  # noqa: E501
                    # If a preview image exists, use it
                    preview_url = post["preview"].get("url") if "preview" in post and post["preview"].get("url") else None  # noqa: E501
                    if preview_url:
                        embed.set_image(url=preview_url)
                    embed.description = f"[Click here to view the video]({video_url})"  # noqa: E501
                else:
                    # put the video as attachment under the embed
                    embed.description = f"[Click here to view the video]({file_url})"  # noqa: E501
            elif file_url.endswith(".swf"):
                embed.description = f"Flash files are no longer supported!\n[Click here to view the post]({file_url})"  # noqa: E501
            else:
                embed.set_image(url=file_url)
            return embed, video_url

    class e6_view(discord.ui.View):
        def __init__(self, posts, index):
            super().__init__()
            self.posts = posts
            self.index = index

        @discord.ui.button(label="Previous", custom_id="prev", style=discord.ButtonStyle.primary)  # noqa: E501
        async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa: E501
            self.index = (self.index - 1) % len(self.posts)
            await self.update_embed(interaction)

        @discord.ui.button(label="Tags")
        async def tags(self,interaction: discord.Interaction, button:discord.Button):  # noqa: E501
            try:
                post = self.posts[self.index]
                tags = post['tags']
                tag_message = "Tags:\n"
                for category, tag_list in tags.items():
                    tag_message += f"**{category.capitalize()}**: {', '.join(tag_list)}\n"  # noqa: E501
                await interaction.response.send_message(content=tag_message, ephemeral=True)  # noqa: E501
            except Exception:
                logger_e6.error("Exception while trying to find tags")

        @discord.ui.button(label="Next", custom_id="next", style=discord.ButtonStyle.primary)  # noqa: E501
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa: E501
            self.index = (self.index + 1) % len(self.posts)
            await self.update_embed(interaction)
            #TODO Add a way to refresh the list of posts so it wont be capped to 100 posts  # noqa: E501

        async def update_embed(self, interaction: discord.Interaction):
            post = self.posts[self.index]
            embed, video_url = E6_commands.e6_commands.create_embed(self, post)
            await interaction.response.edit_message(embed=embed, view=self)  # noqa: E501

async def setup(bot: commands.Bot):
    cog = E6_commands(bot)
    bot.tree.add_command(cog.e6_commands())
    await bot.add_cog(cog)
    configman = GuildConfig()
    configman.set_config_set("user")
    configman.add_setting("NSFW", "E621", "E621 Command options", nsfw=True)  # noqa: E501
    configman.add_option_text(
        "NSFW",
        "E621",
        "web",
        "E621",
        "web",
        "The web URL to use for e621 commands. Default is https://e621.net",  # noqa: E501
    )
