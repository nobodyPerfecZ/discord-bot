from discord_bot.command.disconnect import Disconnect
from discord_bot.command.manager import Manager
from discord_bot.command.music import Music
from discord_bot.command.chat import Chat

__all__ = ["Chat", "Disconnect", "Manager", "Music"]

assert __all__ == sorted(__all__), f"__all__ needs to be sorted into {sorted(__all__)}!"
