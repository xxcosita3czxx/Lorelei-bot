import os

import click
import toml


def load_toml_file(file_path):
    """Load a TOML file and return its data."""
    with open(file_path, encoding='utf-8') as f:
        return toml.load(f)

def flatten_dict(d, parent_key='', sep='.'):
    """Flatten nested dictionaries into a single dictionary with composite keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def find_untranslated_strings(master_data, language_data):
    """Find all untranslated strings in the language file."""
    untranslated = {}

    # Flatten the dictionaries to handle nested keys
    master_data = flatten_dict(master_data)
    language_data = flatten_dict(language_data)

    for key, master_value in master_data.items():
        lang_value = language_data.get(key)

        # Trim whitespace and check for identical values or missing keys
        if not lang_value or lang_value.strip() == "" or lang_value.strip() == master_value.strip():  # noqa: E501
            untranslated[key] = master_value

    return untranslated

def calculate_translation_completion(master_data, language_data):
    """Calculate the completion percentage for each language."""
    # Flatten the dictionaries
    master_data = flatten_dict(master_data)
    language_data = flatten_dict(language_data)

    # Total keys in master after flattening
    total_keys = len(master_data)
    translated_keys = 0

    for key, master_value in master_data.items():
        # Check if the key exists and is different from the master value
        lang_value = language_data.get(key)

        if lang_value and lang_value.strip() != master_value.strip():
            translated_keys += 1

    # Ensure completion percentage is between 0 and 100
    completion_percentage = (translated_keys / total_keys) * 100
    return min(completion_percentage, 100)

def list_language_completions(folder_path, master_file_name, specific_language=None):  # noqa: C901, E501
    """List all languages and their translation completion percentage, and print untranslated strings."""  # noqa: E501
    language_files = {}
    master_file = None

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.toml'):
            if file_name == master_file_name:
                master_file = os.path.join(folder_path, file_name)
            else:
                lang_code = file_name.split('.')[0]  # Assuming the file is named like 'en.toml'  # noqa: E501
                language_files[lang_code] = os.path.join(folder_path, file_name)

    if not master_file:
        click.echo("Master file not found!")
        return

    master_data = load_toml_file(master_file)

    # If a specific language is provided, check only that one
    if specific_language:
        lang_code = specific_language
        if lang_code not in language_files:
            click.echo(f"Language '{lang_code}' not found!")
            return

        lang_file = language_files[lang_code]
        lang_data = load_toml_file(lang_file)
        completion = calculate_translation_completion(master_data, lang_data)

        click.echo(f"\n{lang_code}: {completion:.2f}%")

        # Find untranslated strings
        untranslated = find_untranslated_strings(master_data, lang_data)

        if untranslated:
            # Get the first 10 untranslated strings
            first_ten = list(untranslated.items())[:10]
            for key, value in first_ten:
                click.echo(f"  [{key}] = {value}")

            # If there are more, print how many more
            more_count = len(untranslated) - 10
            if more_count > 0:
                click.echo(f"  and {more_count} more...")
        else:
            click.echo("No untranslated strings found.")
    else:
        # If no specific language is given, check all languages
        for lang_code, lang_file in language_files.items():
            lang_data = load_toml_file(lang_file)
            completion = calculate_translation_completion(master_data, lang_data)

            click.echo(f"\n{lang_code}: {completion:.2f}%")

            # Find untranslated strings
            untranslated = find_untranslated_strings(master_data, lang_data)

            if untranslated:
                # Get the first 5 untranslated strings
                first_five = list(untranslated.items())[:5]
                for key, value in first_five:
                    click.echo(f"  [{key}] = {value}")

                # If there are more, print how many more
                more_count = len(untranslated) - 5
                if more_count > 0:
                    click.echo(f"  and {more_count} more...")
            else:
                click.echo("No untranslated strings found.")

@click.command()
@click.argument('language', default=None, required=False, type=str)
def cli(language):
    """Command line interface to list language completions."""
    list_language_completions("data/lang", "en.toml", specific_language=language)  # noqa: E501

if __name__ == '__main__':
    cli()
