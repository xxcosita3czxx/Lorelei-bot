import discord


def respEmbed(interaction:discord.Interaction,content:str,ephemeral:bool=False):
    embed = discord.Embed(
        description=content,
    )
    interaction.response.send_message(embed=embed,ephemeral=ephemeral)
