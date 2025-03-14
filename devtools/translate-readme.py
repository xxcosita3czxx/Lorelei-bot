import re
import subprocess
import os

README_FILE = "README.md"
TRANSLATION_SCRIPT = "devtools/translate-check.py"

print("Current directory:", os.getcwd())
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
        new_table +="<!-- PLEASE DONT EDIT, GETS GENERATED AUTOMATICALY -->\n\n"
        new_table += "| Language | Progress |\n|----------|----------|\n"
        for lang, percent in sorted_languages:
            new_table += f"| {lang} | {percent:.2f}% |\n"

        # Replace existing table or add if not present
        table_pattern = re.compile(r"(### Translation Progress\n\n\| Language \| Progress \|.*?\n\n)", re.DOTALL)  # noqa: E501
        if table_pattern.search(content):
            new_content = table_pattern.sub(new_table + "\n", content)
        else:
            print("Translation table not found in README.")  # noqa: T201
            return False  # Don't modify anything if no table exists

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
