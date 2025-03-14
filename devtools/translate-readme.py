import os
import re
import subprocess

README_FILE = "README.md"
TRANSLATION_SCRIPT = "devtools/translate-check.py"

print("Current directory:", os.getcwd())  # noqa: T201

def get_translation_percentages():
    """Runs the translation script and extracts percentages for each language."""
    result = subprocess.run(["python", TRANSLATION_SCRIPT], capture_output=True, text=True)  # noqa: E501, S603
    percentages = {}

    for line in result.stdout.splitlines():
        match = re.match(r"^([\w-]+): (\d+\.\d+)%", line)  # Match "xx: YY.YY%"
        if match:
            lang, percent = match.groups()
            percentages[lang.upper()] = float(percent)  # Store percentage as a float for sorting  # noqa: E501
    return percentages

def update_readme(percentages):
    """Updates the README with the new translation percentages."""
    with open(README_FILE, "r+", encoding="utf-8") as f:
        content = f.read()

        # Sort languages first by percentage, then alphabetically
        sorted_languages = sorted(percentages.items(), key=lambda x: (-x[1], x[0]))

        # New translation table
        new_table = "### Translation Progress\n\n"
        new_table += "<!-- PLEASE DONT EDIT, GETS GENERATED AUTOMATICALLY -->\n\n"
        new_table += "| Language | Progress |\n|----------|----------|\n"
        for lang, percent in sorted_languages:
            new_table += f"| {lang} | {percent:.2f}% |\n"

        # Replace existing table or add if not present
        table_pattern = re.compile(r"(### Translation Progress.*?\| Language \| Progress \|.*?\n\n)", re.DOTALL)  # noqa: E501
        if table_pattern.search(content):
            new_content = table_pattern.sub(new_table + "\n", content)
        else:
            # If no translation table exists, insert it below the title and before the translations  # noqa: E501
            print("Translation table not found, adding a new one.")  # noqa: T201
            new_content = content.split("###")  # Split at the first "###"
            if len(new_content) > 1:
                new_content = new_content[0] + "### Translation Progress\n\n" + new_table + "\n" + "###" + new_content[1]  # noqa: E501
            else:
                new_content = content + "\n" + new_table

        # Only update if content changed
        if new_content != content:
            f.seek(0)
            f.write(new_content)
            f.truncate()
            return True  # Indicate change happened
    return False  # No changes

if __name__ == "__main__":
    percentages = get_translation_percentages()
    changed = update_readme(percentages)
    if changed:
        print("README updated with new translation percentages.")  # noqa: T201
