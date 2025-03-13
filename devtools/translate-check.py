import toml
import os

def load_toml_file(file_path):
    """Load a TOML file and return its data."""
    with open(file_path, 'r', encoding='utf-8') as f:
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
        if not lang_value or lang_value.strip() == "" or lang_value.strip() == master_value.strip():
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

def list_language_completions(folder_path, master_file_name):
    """List all languages and their translation completion percentage, and print untranslated strings."""
    language_files = {}
    master_file = None

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.toml'):
            if file_name == master_file_name:
                master_file = os.path.join(folder_path, file_name)
            else:
                lang_code = file_name.split('.')[0]  # Assuming the file is named like 'en.toml'
                language_files[lang_code] = os.path.join(folder_path, file_name)

    if not master_file:
        print("Master file not found!")
        return

    master_data = load_toml_file(master_file)

    # Calculate translation completion for each language
    for lang_code, lang_file in language_files.items():
        lang_data = load_toml_file(lang_file)
        completion = calculate_translation_completion(master_data, lang_data)

        print(f"\n{lang_code}: {completion:.2f}%")

        # Find untranslated strings
        untranslated = find_untranslated_strings(master_data, lang_data)

        if untranslated:
            # Get the first 5 untranslated strings
            first_five = list(untranslated.items())[:5]
            for key, value in first_five:
                print(f"  [{key}] = {value}")

            # If there are more, print how many more
            more_count = len(untranslated) - 5
            if more_count > 0:
                print(f"  and {more_count} more...")
        else:
            print("No untranslated strings found.")

# Example usage
folder_path = 'data/lang'  # Folder containing all your .toml files
master_file_name = 'en.toml'  # Name of the master language file (e.g., en.toml)

list_language_completions(folder_path, master_file_name)
