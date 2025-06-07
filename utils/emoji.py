import emoji
from discord import PartialEmoji


def string2emoji(emoji_string: str):
    if emoji_string.startswith("<:") and emoji_string.endswith(">"):  # Custom emoji
        # Extract name and ID from the custom emoji string
        parts = emoji_string.strip("<:>").split(":")
        name = parts[0]
        emoji_id = int(parts[1])
        return PartialEmoji(name=name, id=emoji_id)
    else:  # Standard Unicode emoji
        return emoji.emojize(emoji_string)

def emoji2string(emoji_obj: PartialEmoji | str):
    if isinstance(emoji_obj, PartialEmoji):  # Custom emoji
        return f"<:{emoji_obj.name}:{emoji_obj.id}>"
    else:  # Standard Unicode emoji
        return emoji.demojize(emoji_obj)
