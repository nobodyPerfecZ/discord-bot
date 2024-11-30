"""Help command for the bot."""

import discord
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

        # Create the embed
        embed = discord.Embed(title="List of commands:", color=discord.Color.blue())
        embed.add_field(
            name="!join", value="Joins the voice channel of the author.", inline=False
        )
        embed.add_field(name="!leave", value="Leaves the voice channel.", inline=False)
        embed.add_field(
            name="!add <url>",
            value="Adds an audio source (YouTube URL) to the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!play",
            value="Starts playing the audio source from the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!pause",
            value="Pauses the currently played audio source.",
            inline=False,
        )
        embed.add_field(
            name="!skip",
            value="Skips the currently played audio source in the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!reset",
            value="Stops the currently played audio source and clears the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!show",
            value="Shows the audio sources from the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!volume <volume>",
            value="Changes the volume of the audio source.",
            inline=False,
        )
        embed.add_field(
            name="!timeout <timeout>",
            value="Changes the timeout of the bot.",
            inline=False,
        )
        embed.add_field(
            name="!whitelisted_roles <command> <role_id1> <role_id2> ...",
            value="Set the specified roles to the whitelist for the given command.",
            inline=False,
        )
        embed.add_field(
            name="!whitelisted_text_channels <command> <text_channel_id1> <text_channel_id2> ...",
            value="Set the specified text channels to the whitelist for the given command.",
            inline=False,
        )
        embed.add_field(
            name="!whitelisted_voice_channels <command> <voice_channel_id1> <voice_channel_id2> ...",
            value="Set the specified voice channels to the whitelist for the given command.",
            inline=False,
        )

        await channel.send(embed=embed)
