# How to add custom commands?

```python
import discord
from discord import app_commands
from discord.ext import commands

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Greets")
    async def hello(interaction:discord.Interaction)
        await interaction.response.send_message("Hello!")

async def setup(bot:commands.Bot):
    await bot.add_cog(Slowmode(bot))
```
Dont worry about adding into main.py, as it is added automaticaly after restart if syntax is correct, else it will throw error

KEEP IT INSIDE ONE FOLDER, DONT STACK FOLDERS

(you dont need to use this folder, you can delete it or rename it to your likings)