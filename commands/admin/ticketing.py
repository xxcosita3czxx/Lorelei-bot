import os
from datetime import datetime

import discord
from discord import app_commands, utils
from discord.ext import commands

from utils.configmanager import gconfig, lang, uconfig


class Ticketing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.default_permissions(manage_guild=True)
    class ticketing_group(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name="ticketing"
            self.description="Ticket commands"
        @app_commands.command(name="add",description="Add user or role into ticket")
        @app_commands.describe(user="Member to add")
        @app_commands.describe(role="Role to add")
        async def ticket_add(self,interaction: discord.Interaction, user:discord.member.Member=None, role:discord.role.Role=None):  # noqa: E501
            try:
                overwrites = discord.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True,
                )
                if user is None and role is not None:
                    await interaction.channel.set_permissions(
                        target=role,
                        overwrite=overwrites,
                    )
                    await interaction.response.send_message(
                        content=f"Added role {role} to ticket",
                    )  # noqa: E501
                elif role is None and user is not None:
                    await interaction.channel.set_permissions(
                        target=user,
                        overwrite=overwrites,
                    )
                    await interaction.response.send_message(
                        content=f"Adding user {user} to ticket",
                    )  # noqa: E501
                elif role is not None and user is not None:
                    await interaction.response.send_message(
                        content="You can only use one.",
                    )
                elif role is None and user is None:
                    await interaction.response.send_message(
                        content="You have to choose one stupid.",
                    )
                else:
                    await interaction.response.send_message(
                        content="Unknown error while parsing values",
                    )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Error while running: {e}",
                    ephemeral=True,
                )

        @app_commands.command(name="remove",description="Remove user or role from ticket")  # noqa: E501
        @app_commands.describe(user="Member to remove")
        @app_commands.describe(role="Role to remove")
        async def ticket_remove(self,interaction: discord.Interaction, user:discord.member.Member=None, role:discord.role.Role=None):  # noqa: E501, F811
            try:
                if user is None and role is not None:
                    await interaction.channel.set_permissions(
                        target=role,
                        overwrite=None,
                    )
                    await interaction.response.send_message(
                        content=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"TicketingCommand","remove_role").format(role=role),
                    )  # noqa: E501
                elif role is None and user is not None:
                    await interaction.channel.set_permissions(
                        target=user,
                        overwrite=None,
                    )
                    await interaction.response.send_message(
                        content=f"Removed user {user} from ticket",
                    )  # noqa: E501
                elif role is not None and user is not None:
                    await interaction.response.send_message(
                        content="You can only use one.",
                    )
                elif role is None and user is None:
                    await interaction.response.send_message(
                        content="You have to choose one stupid.",
                    )
                else:
                    await interaction.response.send_message(
                        content="Unknown error while parsing values",
                    )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Error while running: {e}",
                )
        @app_commands.command(name = 'panel', description='Launches the ticketing system')  # noqa: E501
        @app_commands.checks.cooldown(3, 60, key = lambda i: (i.guild_id))
        async def ticketing(self,interaction: discord.Interaction,title:str="Hi! If you need help or have a question, don't hesitate to create a ticket.", text:str=""):  # noqa: E501

            '''
            Ticket command

            This will actually launch the ticket system
            '''

            embed = discord.Embed(
                title = title,
                description = text,
                color = discord.Colour.blurple(),
            )
            await interaction.channel.send(
                embed = embed,
                view = Ticketing.ticket_launcher(),
            )
            embed = discord.Embed(
                title=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"TicketingCommand","panel_launch"),
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral = True,
            )
    class ticket_launcher(discord.ui.View):

        '''
        This will create the ticket
        '''

        def __init__(self) -> None:  # noqa: ANN101
            super().__init__(timeout = None)
            self.cooldown = commands.CooldownMapping.from_cooldown(
                1,
                60,
                commands.BucketType.member,
            )

        @discord.ui.button(
            label = "Open Ticket",
            style = discord.ButtonStyle.blurple,
            custom_id = "ticket_button",
        )
        async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa: E501, ANN201, ANN101

            interaction.message.author = interaction.user
            retry = self.cooldown.get_bucket(
                interaction.message,
            ).update_rate_limit()

            if retry:
                return await interaction.response.send_message(
                    f"Slow down! Try again in {round(retry, 1)} seconds!",
                    ephemeral = True,
                )
            ticket = utils.get(
                interaction.guild.text_channels,
                name = f"ticket-{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}")  # noqa: E501

            if ticket is not None:
                await interaction.response.send_message(
                    f"You already have a ticket open at {ticket.mention}!",
                    ephemeral = True,
                )

            else:
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(
                        view_channel = False,
                    ),
                    interaction.user: discord.PermissionOverwrite(
                        view_channel = True,
                        read_message_history = True,
                        send_messages = True,
                        attach_files = True,
                        embed_links = True,
                    ),
                    interaction.guild.me: discord.PermissionOverwrite(
                        view_channel = True,
                        send_messages = True,
                        read_message_history = True,
                    ),
                }
                try:
                    channel = await interaction.guild.create_text_channel(
                        name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}",  # noqa: E501
                        overwrites = overwrites,
                        reason = f"Ticket for {interaction.user}",
                    )

                except Exception as e:
                    return await interaction.response.send_message(
                        f"Ticket creation failed! Make sure I have `manage_channels` permissions! --> {e}",  # noqa: E501
                        ephemeral = True,
                    )

                await channel.send(
                    f"@everyone, {interaction.user.mention} created a ticket!",
                    view = Ticketing.main(),
                )
                await interaction.response.send_message(
                    f"I've opened a ticket for you at {channel.mention}!",
                    ephemeral = True,
                )
    class main(discord.ui.View):

        '''
        In-Ticket embed
        '''

        def __init__(self) -> None:  # noqa: ANN101
            super().__init__(timeout = None)

        @discord.ui.button(
            label = "Close Ticket",
            style = discord.ButtonStyle.red,
            custom_id = "close",
        )
        async def close(self, interaction:discord.Interaction, button) -> None:  # noqa: ANN101, ANN001

            embed = discord.Embed(
                title = lang.get(
                    uconfig.get(
                        interaction.user.id,
                        "Appearance",
                        "language",
                    ),
                    "TicketingCommand",
                    "ticket_close_confirm",
                ),
                color = discord.Colour.blurple(),
            )
            await interaction.response.send_message(
                embed = embed,
                view = Ticketing.confirm(),
                ephemeral = True,
            )

        @discord.ui.button(
            label="Transcript",
            style=discord.ButtonStyle.blurple,
            custom_id="transcript",
        )
        async def transcript(self, interaction:discord.Interaction, button):
            await interaction.response.defer()

            # Specify the path where the file will be saved
            file_dir = "data/transcripts"

            file_path = os.path.join(file_dir, f"{interaction.channel.id}.md")

            if os.path.exists(file_path):
                return await interaction.followup.send(
                    "A transcript is already being generated!",
                    ephemeral=True,
                )

            try:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(f"# Transcript of {interaction.channel.name}:\n\n")
                    async for message in interaction.channel.history(
                        limit=None,
                        oldest_first=True,
                    ):
                        created = datetime.strftime(
                            message.created_at,
                            "%m/%d/%Y at %H:%M:%S",
                        )

                        if message.edited_at:
                            edited = datetime.strftime(
                                message.edited_at,
                                "%m/%d/%Y at %H:%M:%S",
                            )
                            f.write(
                                f"{message.author} on {created}: {message.clean_content} (Edited at {edited})\n",  # noqa: E501
                            )
                        else:
                            f.write(
                                f"{message.author} on {created}: {message.clean_content}\n",  # noqa: E501
                            )

                    generated = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
                    f.write(
                        f"\n*Generated at {generated} by {interaction.user.name}*\n*Date Formatting: MM/DD/YY*\n*Time Zone: UTC*",  # noqa: E501
                    )

                with open(file_path, 'rb') as f:
                    await interaction.followup.send(
                        file=discord.File(f, f"{interaction.channel.name}.md"),
                        content="Here is the transcript:",
                    )
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
    class confirm(discord.ui.View):

        '''
        Ticket confirm embed
        '''

        def __init__(self) -> None:  # noqa: ANN101
            super().__init__(timeout = None)

        @discord.ui.button(
            label = "Confirm",
            style = discord.ButtonStyle.red,
            custom_id = "confirm",
        )
        async def confirm_button(self, interaction:discord.Interaction, button) -> None:  # noqa: ANN001, ANN101, E501
            embed=discord.Embed(
                title=lang.get(interaction.user.id,"TicketingCommand","embed_review_title"),
                description=lang.get(interaction.user.id,"TicketingCommand","embed_review_description"),
            )
            try:
                await interaction.channel.delete()
                if gconfig.get(interaction.guild.id,"Ticketing","reviews-enabled") is True:  # noqa: E501
                    await interaction.user.send(embed=embed,view=self.reviews(guild=interaction.guild))  # noqa: E501

            except discord.Forbidden :
                await interaction.response.send_message(
                    content="Channel deletion failed! Make sure I have `manage_channels` permissions!",  # noqa: E501
                    ephemeral = True,
                )

        class reviews(discord.ui.View):
            def __init__(self,guild:discord.Interaction.guild) -> None:  # noqa: ANN101
                super().__init__(timeout = None)
                self.guild:discord.Interaction.guild = guild

            def rev_embed(self,interaction:discord.Interaction):
                review_embed = discord.Embed(
                    title=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"TicketingCommand","embed_review_rev_title"),
                    description=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"TicketingCommand","embed_review_rev_desc"),
                )
                return review_embed
            async def disable_all_buttons(self, interaction: discord.Interaction):
                for child in self.children:
                    if isinstance(child, discord.ui.Button):
                        child.disabled = True
                await interaction.response.edit_message(view=self)

            @discord.ui.button(label="1 star")
            async def rev_star1(self, interaction: discord.Interaction, button: discord.Button):  # noqa: E501
                await self.disable_all_buttons(interaction)
                response_embed = discord.Embed(
                    title=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"TicketingCommand","embed_review_resp_title"),
                )
                await interaction.user.send(
                    embed=response_embed,
                )
                channel = self.guild.get_channel(
                    gconfig.get(self.guild.id,"Ticketing","reviews-channel"),
                )
                await channel.send(content=f"Rating: 1\nUser: {interaction.user.name}")  # noqa: E501

            @discord.ui.button(label="2 star")
            async def rev_star2(self, interaction: discord.Interaction, button: discord.Button):  # noqa: E501
                await self.disable_all_buttons(interaction)
                response_embed = discord.Embed(
                    title=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"TicketingCommand","embed_review_resp_title"),
                )
                await interaction.user.send(
                    embed=response_embed,
                )
                channel = self.guild.get_channel(
                    gconfig.get(self.guild.id,"Ticketing","reviews-channel"),
                )
                await channel.send(content=f"Rating: 2\nUser: {interaction.user.name}")  # noqa: E501

            @discord.ui.button(label="3 star")
            async def rev_star3(self, interaction: discord.Interaction, button: discord.Button):  # noqa: E501
                await self.disable_all_buttons(interaction)
                response_embed = discord.Embed(
                    title=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"TicketingCommand","embed_review_resp_title"),
                )
                await interaction.user.send(
                    embed=response_embed,
                )
                channel = self.guild.get_channel(
                    gconfig.get(self.guild.id,"Ticketing","reviews-channel"),
                )
                await channel.send(content=f"Rating: 3\nUser: {interaction.user.name}")  # noqa: E501

            @discord.ui.button(label="4 star")
            async def rev_star4(self, interaction: discord.Interaction, button: discord.Button):  # noqa: E501
                await self.disable_all_buttons(interaction)
                response_embed = discord.Embed(
                    title=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"TicketingCommand","embed_review_resp_title"),
                )
                await interaction.user.send(
                    embed=response_embed,
                )
                channel = self.guild.get_channel(
                    gconfig.get(self.guild.id,"Ticketing","reviews-channel"),
                )
                await channel.send(content=f"Rating: 4\nUser: {interaction.user.name}")  # noqa: E501

            @discord.ui.button(label="5 star")
            async def rev_star5(self, interaction: discord.Interaction, button: discord.Button):  # noqa: E501
                await self.disable_all_buttons(interaction)
                response_embed = discord.Embed(
                    title=lang.get(uconfig.get(interaction.user.id,"Appearance","language"),"TicketingCommand","embed_review_resp_title"),
                )
                await interaction.user.send(
                    embed=response_embed,
                )
                channel = self.guild.get_channel(
                    gconfig.get(self.guild.id,"Ticketing","reviews-channel"),
                )
                await channel.send(content=f"Rating: 5\nUser: {interaction.user.name}")  # noqa: E501

async def setup(bot:commands.Bot):
    cog = Ticketing(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.ticketing_group())
