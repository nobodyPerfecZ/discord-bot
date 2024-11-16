"""Help command for the bot."""

from discord.ext import commands


class Help(commands.HelpCommand):
    """To display help information for all cogs and commands."""

    async def send_bot_help(
        self,
        mapping: dict[commands.Cog | None, list[commands.Command]],
        /,
    ):
        """
        Sends the help message for the bot.

        Args:
            mapping (dict[commands.Cog  |  None, list[commands.Command]]):
                A dictionary containing all cogs and commands.
        """
        # Send the embed
        channel = self.get_destination()

        # Iterate through all cogs and commands
        for cog, _ in mapping.items():
            if cog is not None:
                embed = cog.help_information()
                await channel.send(embed=embed)
