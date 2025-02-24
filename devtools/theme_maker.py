import os
import sys
from unittest.mock import MagicMock, patch

import click

script_dir = os.path.dirname(os.path.abspath(__file__))
commands_dir = os.path.join(script_dir, '..')
if commands_dir not in sys.path:
    sys.path.insert(0, commands_dir)

from commands.fun.levelsystem import profile_gen  # noqa: E402


@click.group()
def main():
    pass

@click.command()
@click.option('--kitty', is_flag=True, help='Generates a picture inside kitty terminal.')  # noqa: E501
@click.argument("theme")
def gen(kitty,theme):
    mock_user = MagicMock()
    mock_user.name = 'Lorem Ipsum'
    mock_user.id = 'user12345'
    mock_guild = MagicMock()
    mock_guild.id = 'guild12345'

    mock_interaction = MagicMock()
    mock_interaction.user = mock_user
    mock_interaction.guild = mock_guild

    with patch('discord.Interaction', new_callable=lambda: mock_interaction):  # noqa: E501
        var = profile_gen(interaction=mock_interaction, theme=theme)
        click.echo(f"Saved at: {var}")  # noqa: T201
        if kitty:
            os.system(command=f"kitty icat {var}")

@click.command()
def new():
    click.echo("not yet")

@main.result_callback()
def handle_empty_command(ctx, *args, **kwargs):
    if ctx and ctx.invoked_subcommand is None:
        click.echo('Error: No subcommand provided.')
        click.echo(ctx.get_help())
main.add_command(gen)
main.add_command(new)

if __name__ == '__main__':
    main()
