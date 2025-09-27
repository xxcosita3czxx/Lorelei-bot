import logging

import discord
import pytz
from discord import app_commands
from discord.ext import commands

from utils.configmanager import lang, uconfig

logger = logging.getLogger("ftsetup")

#TODO Here could be first time setup for server also


# --- Setup Wizard Views ---
class FTSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.value = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes(self, interaction_button: discord.Interaction, button: discord.ui.Button):  # noqa: E501
        # Start the setup wizard with the first stage (timezone)
        await interaction_button.response.edit_message(
            embed=discord.Embed(
                title="Step 1/3: Which Language you speak?",
                description="Please select your Language.",
                color=discord.Color.blurple(),
            ),
            view=LanguageSetupView(interaction_button.user),
        )

    @discord.ui.button(label="Later", style=discord.ButtonStyle.gray)
    async def later(self, interaction_button: discord.Interaction, button: discord.ui.Button):  # noqa: E501
        await interaction_button.response.edit_message(
            embed=discord.Embed(
                title="First Time Setup Deferred",
                description="You will get the message next time you'll try out the bot :3",  # noqa: E501
                color=discord.Color.blurple(),
            ),
            view=None,
        )

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, interaction_button: discord.Interaction, button: discord.ui.Button):  # noqa: E501
        uconfig.set(
            id=interaction_button.user.id,
            title="APPEARANCE",
            key="ftsetup",
            value=True,
        )
        await interaction_button.response.edit_message(
            embed=discord.Embed(
                title="First Time Setup Skipped",
                description="You can always configure your user settings later with /userconfig.",  # noqa: E501
                color=discord.Color.orange(),
            ),
            view=None,
        )


class LanguageSetupView(discord.ui.View):
    def __init__(self, user, data=None):
        super().__init__(timeout=180)
        self.user = user
        self.data = data or {}
        options = []
        for code, lang_data in lang.config.items():
            name = lang_data.get("LANGUAGE", {}).get("name", code)
            options.append(discord.SelectOption(label=name, value=code))
        self.add_item(self.LanguageDropdown(options, self))

    class LanguageDropdown(discord.ui.Select):
        def __init__(self, options, parent):
            super().__init__(
                placeholder="Select your Language...",
                options=options,
                min_values=1,
                max_values=1,
            )
            self.parent = parent
        async def callback(self, interaction: discord.Interaction):
            lang_code = self.values[0]
            lang_name = next((opt.label for opt in self.options if opt.value == lang_code), lang_code)  # noqa: E501
            self.parent.data['language'] = lang_code
            uconfig.set(
                id=interaction.user.id,
                title="Appearance",
                key="language",
                value=lang_code,
            )
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Step 2/4: Select Your Continent",
                    description="Please select your continent for timezone.",
                    color=discord.Color.blurple(),
                ).add_field(name="Language", value=lang_name, inline=False),
                view=ContinentTimezoneView(self.parent.user, self.parent.data),
            )


# --- New: Continent and City/State Timezone Selection ---

class ContinentTimezoneView(discord.ui.View):
    def __init__(self, user, data=None):
        super().__init__(timeout=180)
        self.user = user
        self.data = data or {}
        # Get unique continents from pytz.common_timezones
        continents = set()
        for tz in pytz.common_timezones:
            if '/' in tz:
                continent = tz.split('/')[0]
                continents.add(continent)
        options = [discord.SelectOption(label=cont, value=cont) for cont in sorted(continents)]  # noqa: E501
        self.add_item(self.ContinentDropdown(options, self))

    class ContinentDropdown(discord.ui.Select):
        def __init__(self, options, parent):
            super().__init__(
                placeholder="Select your continent...",
                options=options,
                min_values=1,
                max_values=1,
            )
            self.parent = parent
        async def callback(self, interaction: discord.Interaction):
            continent = self.values[0]
            self.parent.data['continent'] = continent
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Step 3/4: Select Your City/Region",
                    description=f"Please select your city/region in {continent}.",
                    color=discord.Color.blurple(),
                ).add_field(name="Language", value=self.parent.data.get('language', 'Not set'), inline=False)  # noqa: E501
                .add_field(name="Continent", value=continent, inline=False),
                view=CityTimezoneView(self.parent.user, self.parent.data),
            )

class CityTimezoneView(discord.ui.View):

    def __init__(self, user, data=None, page=0):
        super().__init__(timeout=180)
        self.user = user
        self.data = data or {}
        self.page = page
        continent = self.data.get('continent')
        # Get all timezones for the selected continent
        tzs = [tz for tz in pytz.common_timezones if tz.startswith(continent + '/')]
        # Only show the city/region part
        options = []
        for tz in tzs:
            city = tz.split('/', 1)[1].replace('_', ' ')
            options.append(discord.SelectOption(label=city, value=tz))
        # Discord only allows up to 25 options per select, so chunk if needed
        chunk_size = 25
        start = self.page * chunk_size
        end = start + chunk_size
        self.tzs = tzs
        self.options = options
        self.add_item(self.CityDropdown(options[start:end], self))
        if self.page > 0:
            self.add_item(self.BackButton(self))
        if end < len(options):
            self.add_item(self.NextButton(self))

    class BackButton(discord.ui.Button):
        def __init__(self, parent):
            super().__init__(label="Back", style=discord.ButtonStyle.secondary)
            self.parent = parent
        async def callback(self, interaction: discord.Interaction):
            await interaction.response.edit_message(
                embed=interaction.message.embeds[0],
                view=CityTimezoneView(self.parent.user, self.parent.data, page=self.parent.page - 1),  # noqa: E501
            )

    class NextButton(discord.ui.Button):
        def __init__(self, parent):
            super().__init__(label="Next Cities", style=discord.ButtonStyle.primary)
            self.parent = parent
        async def callback(self, interaction: discord.Interaction):
            await interaction.response.edit_message(
                embed=interaction.message.embeds[0],
                view=CityTimezoneView(self.parent.user, self.parent.data, page=self.parent.page + 1),  # noqa: E501
            )

    class CityDropdown(discord.ui.Select):
        def __init__(self, options, parent):
            super().__init__(
                placeholder="Select your city/region...",
                options=options,
                min_values=1,
                max_values=1,
            )
            self.parent = parent
        async def callback(self, interaction: discord.Interaction):
            tz = self.values[0]
            self.parent.data['timezone'] = tz
            uconfig.set(
                id=interaction.user.id,
                title="FUN",
                key="current-timezone",
                value=tz,
            )
            # Compose summary so far
            lang_code = self.parent.data.get('language', 'Not set')
            continent = self.parent.data.get('continent', 'Not set')
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Step 4/4: Announcements Preferences",
                    description="How do you want to receive announcements?",
                    color=discord.Color.blurple(),
                ).add_field(name="Language", value=lang_code, inline=False)
                 .add_field(name="Continent", value=continent, inline=False)
                 .add_field(name="Timezone", value=tz, inline=False),
                view=AnnouncementsSetupView(self.parent.user, self.parent.data),
            )


# --- Announcements Setup View ---
class AnnouncementsSetupView(discord.ui.View):
    def __init__(self, user, data=None):
        super().__init__(timeout=180)
        self.user = user
        self.data = data or {}
        self.add_item(self.AlwaysYesButton(self))
        self.add_item(self.AlwaysAskButton(self))
        self.add_item(self.NeverButton(self))

    class AlwaysYesButton(discord.ui.Button):
        def __init__(self, parent):
            super().__init__(label="Always Yes", style=discord.ButtonStyle.success)
            self.parent = parent
        async def callback(self, interaction: discord.Interaction):
            self.parent.data['announcements'] = 'always_yes'
            uconfig.set(
                id=interaction.user.id,
                title="",
                key="",
                value="",
            )
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Setup Complete!",
                    description="You will always receive announcements. You can change this later with /userconfig.",  # noqa: E501
                    color=discord.Color.green(),
                ),
                view=None,
            )
            uconfig.set(
                id=interaction.user.id,
                title="APPEARANCE",
                key="ftsetup",
                value=True,
            )

    class AlwaysAskButton(discord.ui.Button):
        def __init__(self, parent):
            super().__init__(label="Always Ask", style=discord.ButtonStyle.primary)
            self.parent = parent
        async def callback(self, interaction: discord.Interaction):
            self.parent.data['announcements'] = 'always_ask'
            uconfig.set(
                id=interaction.user.id,
                title="",
                key="",
                value="",
            )
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Setup Complete!",
                    description="You will be asked before receiving announcements. You can change this later with /userconfig.",  # noqa: E501
                    color=discord.Color.green(),
                ),
                view=None,
            )
            uconfig.set(
                id=interaction.user.id,
                title="APPEARANCE",
                key="ftsetup",
                value=True,
            )

    class NeverButton(discord.ui.Button):
        def __init__(self, parent):
            super().__init__(label="Never", style=discord.ButtonStyle.danger)
            self.parent = parent
        async def callback(self, interaction: discord.Interaction):
            self.parent.data['announcements'] = 'never'
            uconfig.set(
                id=interaction.user.id,
                title="FUN",
                key="announcements-preference",
                value="never",
            )
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Setup Complete!",
                    description="You will never receive announcements. You can change this later with /userconfig.",  # noqa: E501
                    color=discord.Color.green(),
                ),
                view=None,
            )
            uconfig.set(
                id=interaction.user.id,
                title="APPEARANCE",
                key="ftsetup",
                value=True,
            )



class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="force-ftsetup", description="First time setup for user configuration DONT USE, TESTING ONLY")  # noqa: E501
    async def ftsetup(self, interaction: discord.Interaction):
        await interaction.response.send_message("Starting first time setup... Check your DMs!", ephemeral=True)  # noqa: E501
        embed = discord.Embed(
            title="Hello! Hola! Ahoj!",
            description="It looks like you haven't set up your user configuration yet. Would you like to do it now?",  # noqa: E501
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="Why?",
            value="Setting up your user config lets you personalize your experience, such as setting your language or timezone.",  # noqa: E501
        )
        await interaction.user.send(
            embed=embed,
            view=FTSetupView(),
        )

    #event listener
    # event listener for slash command completion
#    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command):  # noqa: C901, E501
        logger.debug(f"User {interaction.user} ran command: {command.qualified_name}")  # noqa: E501
        # Only check for real users (not bots)
        if interaction.user.bot:
            return
        # Import here to avoid circular import
        # Check if user has completed first-time setup
        ftsetup = uconfig.get(
            id=interaction.user.id,
            title="APPEARANCE",
            key="ftsetup",
            default=False,
        )
        if ftsetup:
            return

        embed = discord.Embed(
            title="Hello! Hola! Ahoj!",
            description="It looks like you haven't set up your user configuration yet. Would you like to do it now?",  # noqa: E501
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="Why?",
            value="Setting up your user config lets you personalize your experience, such as setting your language or timezone. It won't take more than 1 minute.",  # noqa: E501
        )
        await interaction.user.send(
            embed=embed,
            view=FTSetupView(),
        )


async def setup(bot: commands.Bot):
#    cog = Setup(bot)
#    await bot.add_cog(cog)
    pass
