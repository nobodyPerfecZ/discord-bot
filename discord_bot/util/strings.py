import re


def remove_emojis(s: str) -> str:
    """
    Remove emojis from a string.

    Args:
        s (str):
            The string to remove emojis from

    Returns:
        str:
            The string without emojis
    """
    pattern = re.compile(
        pattern="["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002700-\U000027bf"  # Dingbats
        "\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
        "\U00002600-\U000026ff"  # Misc symbols
        "\U0001fa70-\U0001faff"  # Extended symbols
        "\U000025a0-\U000025ff"  # Geometric shapes
        "]+",
        flags=re.UNICODE,
    )
    words = s.split(" ")
    new_words = []
    for word in words:
        new_word = pattern.sub(r"", word)
        if new_word:
            new_words.append(new_word)
    return " ".join(new_words)


def truncate(s: str, length: int) -> str:
    """
    Truncate a string to a certain length.

    Args:
        s (str):
            The string to truncate

        length (int):
            The length to truncate to

    Returns:
        str:
            The truncated string with length + 3
    """
    if len(s) > length:
        return s[:length] + "..."
    return s
