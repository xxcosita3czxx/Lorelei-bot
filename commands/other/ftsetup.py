import logging

import discord
import pytz
from discord import app_commands
from discord.ext import commands

from utils.configmanager import uconfig

logger = logging.getLogger("ftsetup")

#TODO Here could be first time setup for server also

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="force-ftsetup", description="First time setup for user configuration DONT USE, TESTING ONLY")  # noqa: E501
    async def ftsetup(self, interaction: discord.Interaction):
        await interaction.response.send_message("Starting first time setup...")
        await interaction.user.send(
            embed=discord.Embed(
                title="Welcome!",
                description="It looks like you haven't set up your user configuration yet. Would you like to do it now?",  # noqa: E501
                color=discord.Color.blue(),
            ).add_field(name="Why?", value="Setting up your user config lets you personalize your experience, such as setting your timezone."),  # noqa: E501
        )

    #event listener
    # event listener for slash command completion
    @commands.Cog.listener()
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


        class FTSetupView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)
                self.value = None

            @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
            async def yes(self, interaction_button: discord.Interaction, button: discord.ui.Button):  # noqa: E501
                # Start the setup wizard with the first stage (timezone)
                await interaction_button.response.edit_message(
                    embed=discord.Embed(
                        title="Step 1/3: Set Your Timezone",
                        description="Please select your timezone.",
                        color=discord.Color.blurple(),
                    ),
                    view=TimezoneSetupView(interaction_button.user),
                )

            @discord.ui.button(label="Later", style=discord.ButtonStyle.gray)
            async def later(self, interaction_button: discord.Interaction, button: discord.ui.Button):  # noqa: E501
                await interaction_button.response.edit_message(
                    embed=discord.Embed(
                        title="First Time Setup Deferred",
                        description="You can configure your user settings at any time with /userconfig. You will get the message next time you'll try out the bot :3",  # noqa: E501
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


        # --- Setup Wizard Views ---
        class TimezoneSetupView(discord.ui.View):
            def __init__(self, user, data=None):
                super().__init__(timeout=180)
                self.user = user
                self.data = data or {}
                options = [
                    discord.SelectOption(label=tz, value=tz)
                    for tz in pytz.common_timezones[:25]
                ]
                self.add_item(self.TimezoneDropdown(options, self))

            class TimezoneDropdown(discord.ui.Select):
                def __init__(self, options, parent):
                    super().__init__(
                        placeholder="Select your timezone...",
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
                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            title="Step 2/3: Notification Preferences",
                            description="Would you like to enable notifications?",
                            color=discord.Color.blurple(),
                        ).add_field(name="Timezone", value=tz, inline=False),
                        view=NotifSetupView(self.parent.user, self.parent.data),
                    )

        class NotifSetupView(discord.ui.View):
            def __init__(self, user, data=None):
                super().__init__(timeout=180)
                self.user = user
                self.data = data or {}
                self.add_item(self.YesButton(self))
                self.add_item(self.NoButton(self))

            class YesButton(discord.ui.Button):
                def __init__(self, parent):
                    super().__init__(label="Enable Notifications", style=discord.ButtonStyle.success)  # noqa: E501
                    self.parent = parent
                async def callback(self, interaction: discord.Interaction):
                    self.parent.data['notifications'] = True
                    uconfig.set(
                        id=interaction.user.id,
                        title="FUN",
                        key="notifications-enabled",
                        value=True,
                    )
                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            title="Step 3/3: Profile Visibility",
                            description="Who can see your profile?",
                            color=discord.Color.blurple(),
                        ).add_field(name="Timezone", value=self.parent.data.get('timezone', 'Not set'), inline=False)  # noqa: E501
                         .add_field(name="Notifications", value="Enabled", inline=False),  # noqa: E501
                        view=ProfileSetupView(self.parent.user, self.parent.data),
                    )

            class NoButton(discord.ui.Button):
                def __init__(self, parent):
                    super().__init__(label="Disable Notifications", style=discord.ButtonStyle.danger)  # noqa: E501
                    self.parent = parent
                async def callback(self, interaction: discord.Interaction):
                    self.parent.data['notifications'] = False
                    uconfig.set(
                        id=interaction.user.id,
                        title="FUN",
                        key="notifications-enabled",
                        value=False,
                    )
                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            title="Step 3/3: Profile Visibility",
                            description="Who can see your profile?",
                            color=discord.Color.blurple(),
                        ).add_field(name="Timezone", value=self.parent.data.get('timezone', 'Not set'), inline=False)  # noqa: E501
                         .add_field(name="Notifications", value="Disabled", inline=False),  # noqa: E501
                        view=ProfileSetupView(self.parent.user, self.parent.data),
                    )

        class ProfileSetupView(discord.ui.View):
            def __init__(self, user, data=None):
                super().__init__(timeout=180)
                self.user = user
                self.data = data or {}
                options = [
                    discord.SelectOption(label="Public", value="public"),
                    discord.SelectOption(label="Friends Only", value="friends"),
                    discord.SelectOption(label="Private", value="private"),
                ]
                self.add_item(self.ProfileDropdown(options, self))

            class ProfileDropdown(discord.ui.Select):
                def __init__(self, options, parent):
                    super().__init__(
                        placeholder="Select profile visibility...",
                        options=options,
                        min_values=1,
                        max_values=1,
                    )
                    self.parent = parent
                async def callback(self, interaction: discord.Interaction):
                    vis = self.values[0]
                    self.parent.data['profile_visibility'] = vis
                    uconfig.set(
                        id=interaction.user.id,
                        title="FUN",
                        key="profile-visibility",
                        value=vis,
                    )
                    # Show summary
                    summary = (
                        f"Timezone: {self.parent.data.get('timezone', 'Not set')}\n"
                        f"Notifications: {'Enabled' if self.parent.data.get('notifications') else 'Disabled'}\n"  # noqa: E501
                        f"Profile Visibility: {vis.capitalize()}"
                    )
                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            title="Setup Complete!",
                            description="Your first time setup is complete. You can always change your settings with /userconfig.\n\n**Summary:**\n" + summary,  # noqa: E501
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

        embed = discord.Embed(
            title="Welcome!",
            description="It looks like you haven't set up your user configuration yet. Would you like to do it now?",  # noqa: E501
            color=discord.Color.blue(),
        )
        embed.add_field(name="Why?", value="Setting up your user config lets you personalize your experience, such as setting your timezone.")  # noqa: E501
        await interaction.followup.send(
            embed=embed,
            view=FTSetupView(),
            ephemeral=True,
        )

async def setup(bot: commands.Bot):
    cog = Setup(bot)
    await bot.add_cog(cog)
