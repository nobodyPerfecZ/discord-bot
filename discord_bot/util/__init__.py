from .strings import remove_emojis, truncate

__all__ = [
    "remove_emojis",
    "truncate",
]

assert __all__ == sorted(__all__), f"__all__ needs to be sorted into {sorted(__all__)}!"
