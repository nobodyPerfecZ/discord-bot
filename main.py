"""Starting point of the bot."""

import asyncio
import logging
import os

import discord
import yaml
from discord.ext import commands

from discord_bot.command import Disconnect, Manager, Music


async def main(client: commands.Bot, **kwargs):
    """Starting point of the bot."""
    async with client:
        await client.add_cog(Music(client, **kwargs["music"]))
        await client.add_cog(Manager(client, **kwargs["manager"]))
        await client.add_cog(Disconnect(client, **kwargs["disconnect"]))
        await client.start(token=os.environ["TOKEN"])


if __name__ == "__main__":
    # Enable logging of the bot
    discord.utils.setup_logging(level=logging.WARNING)

    # Get all intents
    intents = discord.Intents.all()

    # Create the bot
    bot = commands.Bot(
        command_prefix=os.environ["COMMAND_PREFIX"],
        intents=intents,
        help_command=None,
    )

    # Create the configuration
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # Run the bot on the server
    asyncio.run(main(bot, **config))
