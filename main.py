import asyncio
import logging.handlers

import discord
from discord.ext import commands

from discord_bot.command.music import Music


async def main(bot: commands.Bot):
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(
            token="NTkzMDU4MTI5NzIyMjEyMzY0.GV6RIa.0eC8FvlomgpOKk1xDOEPsDyCp8X_MglWZULc7s",
        )

if __name__ == "__main__":
    # Enable logging of the bot
    discord.utils.setup_logging(level=logging.DEBUG)

    # Create the bot
    intents = discord.Intents.all()

    bot = commands.Bot(command_prefix="!", intents=intents)

    # Run the bot on the server
    asyncio.run(main(bot))
