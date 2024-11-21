"""Starting point of the bot."""

import asyncio
import logging.handlers
import os

import discord
import yaml
from discord.ext import commands
from dotenv import load_dotenv

from discord_bot.command import Disconnect, Help, Manager, Music

# Load the environment variables
load_dotenv()


async def main(client: commands.Bot, **kwargs):
    """Starting point of the bot."""
    async with client:
        await client.add_cog(Music(client, **kwargs["music"]))
        await client.add_cog(Manager(client, **kwargs["manager"]))
        await client.add_cog(Disconnect(client, **kwargs["disconnect"]))
        await client.start(token=os.environ["__DISCORD_API_KEY__"])


if __name__ == "__main__":
    # Enable logging of the bot
    # level=logging.DEBUG for debugging
    discord.utils.setup_logging(level=logging.WARNING)

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
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # Run the bot on the server
    asyncio.run(main(bot, **config))
