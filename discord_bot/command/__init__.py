from discord_bot.command.disconnect import Disconnect
from discord_bot.command.help import Help
from discord_bot.command.manager import Manager
from discord_bot.command.music import Music

del disconnect  # type: ignore[name-defined] # noqa: F821
del help  # type: ignore[name-defined] # noqa: F821
del manager  # type: ignore[name-defined] # noqa: F821
del music  # type: ignore[name-defined] # noqa: F821

__all__ = [
    "Disconnect",
    "Help",
    "Manager",
    "Music",
]

assert __all__ == sorted(__all__)
