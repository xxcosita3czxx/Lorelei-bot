import discord
from discord import app_commands
from discord.ext import commands


class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@app_commands.command(name="clear", description="Clear n messages specific user")
@app_commands.default_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount:int, member: discord.Member = None):  # noqa: E501
    try:
        await interaction.response.defer()
        channel = interaction.channel

        if member is None:
            await channel.purge(limit=amount)
            await interaction.followup.send(
                embed=discord.Embed(
                    description=f"Successfully deleted {amount} messages.",
                    color=discord.Color.green(),
                ),
            )

        elif member is not None:
            await channel.purge(limit=amount)
            await interaction.followup.send(
                embed=discord.Embed(
                    description=f"Successfully deleted {amount} messages from {member.name}",  # noqa: E501
                    color=discord.Color.green(),
                ),
            )
        else:
            await interaction.followup.send(
                content="INTERACTION FAILED",
                ephemeral=True,
            )
    except discord.errors.NotFound:
        await interaction.followup.send(
            content="Removed all that we could, but exception happened",
        )
    except Exception as e:
        await interaction.followup.send(
            content=f"Clear failed!: {e}",
            ephemeral=True,
        )

async def setup(bot:commands.Bot):
    await bot.add_cog(Clear(bot))
