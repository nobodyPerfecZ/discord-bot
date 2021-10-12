import random
from asyncio import Queue, Event, TimeoutError
from async_timeout import timeout
import itertools

import discord
from discord.ext import commands

class VoiceError(Exception):
    pass

class SongQueue(Queue):
    
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]
    


class VoiceState():
    def __init__(self, client :commands.Bot, ctx :commands.Context):
        self._client = client
        self._ctx = ctx

        self._current = None
        self._voice = None
        self._next = Event()
        self._songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self._skip_votes = set()

        self._audio_player = client.loop.create_task(self.audio_player_task())

        def __del__(self):
            self.audio_player.cancel()
        
        @property
        def loop(self):
            return self._loop
        
        @loop.setter
        def loop(self, value :bool):
            self._loop = value
        
        @property
        def volume(self):
            return self._volume
        
        @volume.setter
        def volume(self, value :float):
            self._volume = value

        @property
        def is_playing(self):
            return self._voice and self._current

        async def audio_player_task(self):
            while True:
                self._next.clear()

                if not self.loop:
                    try:
                        async with timeout(180):
                            self._current = await self._songs.get()
                    except TimeoutError:
                        self._client.loop.create_task(self.stop())
                        return
                
                self._current.source.volume = self._volume
                self._voice.play(self._current.source, after=self.play_next_song)
                await self._current.source.channel.send(embed=self._current.create_embed())

                await self.next.wait()
            
        def play_next_song(self, error=None):
            if error:
                raise VoiceError(str(error))

            self._next.set()
        
        def skip(self):
            self._skip_votes.clear()

            if self.is_playing:
                self._voice.stop()
        
        async def stop(self):
            self._voice.clear()

            if self._voice:
                await self._voice.disconnect()
                self._voice = None
