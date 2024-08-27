import discord


async def respEmbed(interaction:discord.Interaction,content:str,ephemeral:bool=False):  # noqa: E501
    embed = discord.Embed(
        description=content,
    )
    interaction.response.send_message(embed=embed,ephemeral=ephemeral)
