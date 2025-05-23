"""Chat commands for the Discord bot."""

import asyncio
from typing import AsyncIterator

from discord.ext import commands
from ollama import AsyncClient, ChatResponse

from discord_bot.checks import (
    check_author_id_blacklisted,
    check_author_role_blacklisted,
    check_text_channel_blacklisted,
    check_voice_channel_blacklisted,
)


class Chat(commands.Cog):
    """
    A suite of commands to control a chat bot in a Discord Server.

    Attributes:
        bot (commands.Bot):
            The discord client to handle the commands

        host (str):
            The host of the Ollama chat model

        kwargs:
            Additional keyword arguments
    """

    def __init__(
        self,
        bot: commands.Bot,
        host: str = "http://localhost:11434",
        model: str = "gemma3:1b",
        **kwargs,
    ):
        self.bot = bot
        self.host = host
        self.model = model
        self.kwargs = kwargs

    async def _before_chat(self, ctx: commands.Context):
        """Checks for the chat command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_id_blacklisted(ctx, manager.users),
            check_author_role_blacklisted(ctx, manager.roles),
            check_text_channel_blacklisted(ctx, manager.text_channels),
            check_voice_channel_blacklisted(ctx, manager.voice_channels),
        )

    async def _chat_response(self, message: str) -> AsyncIterator[ChatResponse]:
        """
        Send a message to the Ollama chat model and return the response.

        Args:
            message (str):
                The message to send to the chat model

        Returns:
            str:
                The response from the chat model
        """
        client = AsyncClient(host="http://localhost:11434")
        response = await client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer every question using one short sentence, no longer "
                        "than 20 characters. Do not use lists."
                    ),
                },
                {"role": "user", "content": message},
            ],
            stream=False,
        )
        return response["message"]["content"]

    @commands.command(aliases=["Chat"])
    async def chat(self, ctx: commands.Context, *message):
        """
        Chats with the bot.

        It sends a message to an Ollama model and returns the response.

        Args:
            ctx (commands.Context):
                The discord context

            message (str):
                The message to send to the chat model
        """
        async with ctx.typing():
            message = " ".join(message)
            await self._before_chat(ctx)
            response = await self._chat_response(message)
            await ctx.send(content=response)
