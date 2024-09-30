import asyncio
import logging.handlers
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from discord_bot.command import Help, Music

# Load the environment variables
load_dotenv()


async def main(client: commands.Bot, **kwargs):
    """Starting point of the bot."""
    async with client:
        await client.add_cog(Music(client, **kwargs))
        await client.start(token=os.environ["__DISCORD_API_KEY__"])


if __name__ == "__main__":
    # Enable logging of the bot
    discord.utils.setup_logging(level=logging.WARNING)  # logging.DEBUG for debugging

    # Get all intents
    intents = discord.Intents.all()

    # Create the help command
    help_command = Help()

    # Create the bot
    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
        help_command=help_command,
    )

    # Create the configuration
    config = {
        "whitelisted_roles": [
            "DJ",
            "#ANBU#",
            "Kage",
            "Jonin",
            "Chunin",
            "Genin",
            "#Hafensänger#",
        ],
        "whitelisted_text_channels": ["music🎼", "bottest"],
        "disconnect_timeout": 600,
        "volume": 50,
    }

    # Run the bot on the server
    asyncio.run(main(bot, **config))
