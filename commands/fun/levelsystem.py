#TODO Default profile theme finsih seccond part + colors

import logging
import math
from io import BytesIO

import discord
import requests
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

import config
from utils.configmanager import gconfig, themes

DEFAULT_IMAGE_PATH = config.def_image

def eval_fstring(s, context):
    """Evaluate a string expression as an f-string with the given context."""
    if not s:
        return s
    try:
        # Use eval to evaluate the f-string directly with context
        return eval(f"f'''{s}'''", globals(), context)  # noqa: S307
    except Exception as e:
        logging.error(f"Failed to evaluate f-string {s}: {e}")
        return s

def profile_gen(interaction:discord.Interaction,theme:str="Default"):  # noqa: C901, E501
    logging.debug(themes.config)

    # Vars
    bg = themes.get(theme,"Data","bg")
    fixed_size = (710, 800)  # Fixed size for the profile image
    objects = themes.get(theme,"Text", "objects")
    font = themes.get(theme,"Text","font")

    context = {
        'interaction': interaction,
    }
    # Load and resize the background image
    if bg.startswith("#"):
        background = Image.new('RGB', fixed_size, color=bg)
    else:
        background = Image.open(bg)
        background = background.resize(fixed_size, Image.ANTIALIAS)

    draw = ImageDraw.Draw(background)
    logging.debug(objects)
    for obj in objects:
        logging.debug(obj)

        # Directly check for "text" key
        if obj.get("text"):
            text = obj["text"]
            # Use defaults where fields might be missing
            position = tuple(text.get('position', [0, 0]))
            content = text.get('content', '')
            size = text.get('size', 20)  # Default font size 20 if missing
            color = tuple(text.get('color', [255, 255, 255]))  # Default color white

            draw.text(position, content, font=ImageFont.truetype(font, size), fill=color)  # noqa: E501

        # Directly check for "img" key
        elif obj.get("img"):
            img = obj["img"]
            img_path = eval_fstring(img.get('image'), context=context)

            if not img_path:
                logging.warning(f"Image path not provided for object {obj}")
                continue

            try:
                # Attempt to load the image (URL or local file)
                if img_path.startswith("http://") or img_path.startswith("https://"):
                    response = requests.get(img_path, timeout=60)
                    image = Image.open(BytesIO(response.content))
                else:
                    image = Image.open(img_path)

            except Exception as e:
                logging.error(f"Failed to process image {img_path}: {e}")
                logging.warning("Replacing image with default image.")

                # Replace the img object with a default one

                try:
                    image = Image.open(DEFAULT_IMAGE_PATH)  # Load default image
                except Exception as default_error:
                    logging.error(f"Failed to load default image: {default_error}")
                    continue  # Skip if even the default fails

            # Resize the image if width and height are provided
            width = img.get('width')
            height = img.get('height')
            if width and height:
                image = image.resize((width, height), Image.ANTIALIAS)

            # Get the position to paste the image
            position = tuple(img.get('position', [0, 0]))

            # Paste the image onto the background
            background.paste(image, position)
            logging.debug(f"Pasted image {img_path} at {position}")

        elif obj.get("rect"):
            rect = obj["rect"]

            # Center of the rectangle
            center = tuple(rect.get('position', [100, 100]))

            # Width and height of the rectangle
            width = rect.get('size', [100, 50])[0]  # Default width
            height = rect.get('size', [100, 50])[1]  # Default height

            top_left = (center[0] - width // 2, center[1] - height // 2)
            bottom_right = (center[0] + width // 2, center[1] + height // 2)

            # Color of the rectangle
            color = tuple(rect.get('color', [255, 255, 255]))  # Default white

            # Corner rounding radius (optional, default to 0 for no rounding)
            corner_radius = rect.get('corner_radius', 0)

            # Draw the rounded rectangle
            draw.rounded_rectangle([top_left, bottom_right], radius=corner_radius, fill=color)  # noqa: E501
            logging.debug(f"Drew rectangle at {top_left} with size {bottom_right} and color {color}")  # noqa: E501

        # Handling "circle" objects
        elif obj.get("circle"):
            circle = obj["circle"]
            center = tuple(circle.get('position', [50, 50]))  # Center of the circle
            radius = circle.get('radius', 50)  # Radius of the circle
            color = tuple(circle.get('color', [255, 255, 255]))  # Default white
            bounding_box = [  # Define the bounding box for the circle
                (center[0] - radius, center[1] - radius),
                (center[0] + radius, center[1] + radius),
            ]
            draw.ellipse(bounding_box, fill=color)
            logging.debug(f"Drew circle at {center} with radius {radius} and color {color}")  # noqa: E501

        # Handling "triangle" objects
        elif obj.get("triangle"):
            triangle = obj["triangle"]
            center = tuple(triangle.get('position', [100, 100]))
            radius = triangle.get('radius', 50)  # Radius of the triangle
            color = tuple(triangle.get('color', [255, 255, 255]))  # Default white

            # Optional rotation (in degrees)
            rotation = triangle.get('rotation', 0)  # Default to 0 degrees

            # Calculate the three vertices of the equilateral triangle
            points = []
            for i in range(3):
                angle_deg = 120 * i + rotation
                angle_rad = math.radians(angle_deg)
                x = center[0] + radius * math.cos(angle_rad)
                y = center[1] + radius * math.sin(angle_rad)
                points.append((x, y))

            # Draw the triangle
            draw.polygon(points, fill=color)
            logging.debug(f"Drew triangle at {center} with radius {radius}, color {color}, and rotation {rotation}")  # noqa: E501

        else:
            logging.warning(f"Unsupported or invalid object {obj} in theme {theme}, ignoring...")  # noqa: E501


    # Save the image
    if interaction is not None:
        if interaction.guild.id:
            background.save(f".cache/{interaction.user.id}-{interaction.guild.id}.png")
            return f".cache/{interaction.user.id or 'lorem-user'}-{interaction.guild.id or 'lorem-id'}.png"  # noqa: E501
        else:
            background.save(f".cache/{interaction.user.id}.png")
            return f".cache/{interaction.user.id}.png"
    elif interaction is None:
        logging.warning("Well be saving as testing file. If running the bot THIS IS A BUG")  # noqa: E501
        background.save(".cache/lorem.png")
        return ".cache/lorem.png"
    else:
        logging.error("Failed to make profile: Interaction is wrong type")

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="global-leaderboard",description="Level Leaderboard")
    async def global_leaderboard(self,interaction:discord.Interaction):
        pass

    @app_commands.command(name="leaderboard",description="Server Leaderboard")
    async def leaderboard(self, interaction:discord.Interaction):
        if gconfig.get(interaction.guild.id,""):
            pass

    @app_commands.command(name="profile",description="Your profile")
    async def profile(self,interaction: discord.Interaction, minimal:bool=False):
        if not minimal:
            image = profile_gen(interaction=interaction,bg="data/prof-bgs/Default.png")  # noqa: E501
            embed = discord.Embed(title=f"Profile of {interaction.user.name}")
            file = discord.File(image, filename="profile.png")
            embed.set_image(url="attachment://profile.png")
            await interaction.response.send_message(embed=embed,file=file)
        else:
            embed = discord.Embed(title=f"Profile of {interaction.user.name}")
            embed.add_field(name="Level: {lorem ipsum}")
            interaction.response.send_message(embed=embed)

async def setup(bot:commands.Bot):
#    cog = LevelSystem(bot)
#    await bot.add_cog(cog)
    pass
