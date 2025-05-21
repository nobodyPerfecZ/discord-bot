"""Chat commands for the Discord bot."""

import asyncio
from typing import AsyncIterator

from discord.ext import commands
from ollama import AsyncClient, ChatResponse

from discord_bot.checks import (
    check_author_voice_channel,
    check_author_whitelisted,
    check_bot_voice_channel,
    check_same_voice_channel,
    check_text_channel_whitelisted,
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

    async def _before_chat(self, ctx: commands.Context, message: str):
        """Checks for the chat command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_whitelisted(ctx, manager.wroles),
            check_text_channel_whitelisted(ctx, manager.wtext_channels),
            check_author_voice_channel(ctx),
            check_bot_voice_channel(ctx),
            check_same_voice_channel(ctx),
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
        Sends a message to the Ollama chat model and returns the response.

        Args:
            ctx (commands.Context):
                The discord context

            message (str):
                The message to send to the chat model
        """
        async with ctx.typing():
            message = " ".join(message)
            await self._before_chat(ctx, message)
            response = await self._chat_response(message)
            await ctx.send(content=response)
