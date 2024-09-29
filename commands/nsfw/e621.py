#TODO Logic for Tags

import logging
import random

import discord
import requests
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import autocomplete_tags


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
        async def e6_random_post(self,interaction:discord.Interaction,tags:str="",web:str="https://e621.net"):
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
                    if tags is not None:
                        await interaction.response.send_message(
                            content=f"No images found for these tags: {tags}",
                        )
                    else:
                        await interaction.response.send_message(
                        content="No image found.",
                    )
                #post = random.choice(data["posts"]) # noqa: S311

                posts = data["posts"]
                current_index = random.randint(0, len(posts) - 1)  # Start with a random post  # noqa: E501, S311

                embed, video_url = self.create_embed(posts[current_index])
                await interaction.response.send_message(
                    embed=embed,
                    view=E6_commands.e6_view(posts, current_index),
                )
            except Exception as e:
                await interaction.response.send_message(content=f"Exception: {e}")

        def create_embed(self, post):
            embed = discord.Embed(
                title=f"Post {post['id']}, by {', '.join(post['tags']['artist'])}",
            )
            video_url = None
            if post["file"]["url"].endswith((".mp4", ".webm")):  # If the file is a video  # noqa: E501
                video_url = post["file"]["url"]
                embed.description = f"[Click here to view the video]({video_url})"  # Add video link to description  # noqa: E501
            elif post["file"]["url"].endswith(".swf"):
                embed.description = "Flash files are no longer supported!"
            else:
                embed.set_image(url=post["file"]["url"])
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
                pass
            except Exception:
                logging.error("Exception while trying to find tags")

        @discord.ui.button(label="Next", custom_id="next", style=discord.ButtonStyle.primary)  # noqa: E501
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa: E501
            self.index = (self.index + 1) % len(self.posts)
            await self.update_embed(interaction)


        async def update_embed(self, interaction: discord.Interaction):
            post = self.posts[self.index]
            embed, video_url = E6_commands.e6_commands.create_embed(self, post)
            await interaction.response.edit_message(embed=embed, view=self)  # noqa: E501

async def setup(bot: commands.Bot):
    cog = E6_commands(bot)
    bot.tree.add_command(cog.e6_commands())
    await bot.add_cog(cog)
