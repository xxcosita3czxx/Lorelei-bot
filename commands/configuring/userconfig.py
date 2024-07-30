class GuildConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    class configure_user(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name="userconfig"
            self.description="User Config"

        @app_commands.command(name="color",description="Default color bot will respond for you")  # noqa: E501
        @app_commands.autocomplete(color=autocomplete_color)
        async def conf_user_def_color(self,interaction:discord.Interaction, color:str):
            try:
                uconfig.set(interaction.user.id,"Appearance","color",color)
                await interaction.response.send_message(
                    content=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"Responds","value_set").format(values=color),
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )

        @app_commands.command(
            name="language",
            description="Language the bot will respond to you",
        )
        @app_commands.autocomplete(language=autocomplete_lang)
        async def conf_user_lang(self,interaction:discord.Interaction,language:str):
            try:
                uconfig.set(interaction.user.id,"Appearance","language",language)
                await interaction.response.send_message(
                    content=f"Setted value {str(language)}",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )

    tree.add_command(configure_user())