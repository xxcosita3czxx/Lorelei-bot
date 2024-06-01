import click
import toml


def fill_missing_keys(data, defaults):
    for key, value in defaults.items():
        if key not in data:
            data[key] = value
        elif isinstance(value, dict):
            if not isinstance(data[key], dict):
                data[key] = value
            else:
                fill_missing_keys(data[key], value)
    return data

@click.command()
@click.argument('default_file', type=click.Path(exists=True))
@click.argument('target_file', type=click.Path(exists=True))
def main(default_file, target_file):
    """Fill missing keys in a target TOML file from a default TOML file."""
    # Read the default toml file
    with open(default_file, encoding='utf-8') as f:
        default_data = toml.load(f)

    # Read the target toml file
    with open(target_file, encoding='utf-8') as f:
        target_data = toml.load(f)

    # Fill missing keys without overwriting existing ones
    updated_data = fill_missing_keys(target_data, default_data)

    # Write back to the target toml file
    with open(target_file, 'w', encoding='utf-8') as f:
        toml.dump(updated_data, f)

    click.echo(f"Updated {target_file} with missing keys from {default_file}")

if __name__ == "__main__":
    main()
