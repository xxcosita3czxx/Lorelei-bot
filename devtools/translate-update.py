import click
import toml


def sync_keys(data, defaults, hard=False):
    if hard:
        # Remove keys not in defaults
        keys_to_remove = [key for key in data if key not in defaults]
        for key in keys_to_remove:
            del data[key]

    # Fill missing keys from defaults
    for key, value in defaults.items():
        if key not in data:
            data[key] = value
        elif isinstance(value, dict):
            if not isinstance(data[key], dict):
                data[key] = value
            else:
                sync_keys(data[key], value, hard)
    return data

@click.command()
@click.argument('default_file', type=click.Path(exists=True))
@click.argument('target_file', type=click.Path(exists=True))
@click.option('--hard', is_flag=True, help="Remove keys not present in the default file")  # noqa: E501
def main(default_file, target_file, hard):
    """Sync keys in a target TOML file with a default TOML file."""
    # Read the default toml file
    with open(default_file, encoding='utf-8') as f:
        default_data = toml.load(f)

    # Read the target toml file
    with open(target_file, encoding='utf-8') as f:
        target_data = toml.load(f)

    # Sync keys: fill missing keys and optionally remove extra keys
    updated_data = sync_keys(target_data, default_data, hard)

    # Write back to the target toml file
    with open(target_file, 'w', encoding='utf-8') as f:
        toml.dump(updated_data, f)

    click.echo(f"Synced {target_file} with {default_file}. {'Hard mode enabled.' if hard else ''}")  # noqa: E501

if __name__ == "__main__":
    main()
