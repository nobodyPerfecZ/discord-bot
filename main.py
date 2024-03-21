import asyncio
import logging.handlers

import discord
from discord.ext import commands

from discord_bot.command.music import Music


async def main(client: commands.Bot, **kwargs):
    async with client:
        await client.add_cog(Music(client, **kwargs))
        await client.start(
            token="NTkzMDU4MTI5NzIyMjEyMzY0.GV6RIa.0eC8FvlomgpOKk1xDOEPsDyCp8X_MglWZULc7s",
        )

if __name__ == "__main__":
    # Enable logging of the bot
    discord.utils.setup_logging(level=logging.WARNING)  # logging.DEBUG for debugging

    # Get all intents
    intents = discord.Intents.all()

    # Change the default behavior of !help by disabling parameter descriptions
    help_command = commands.DefaultHelpCommand(show_parameter_descriptions=False)

    # Create the bot
    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
        help_command=help_command,
    )

    # Run the bot on the server
    asyncio.run(main(bot, disconnect_timeout=600, volume=50))
