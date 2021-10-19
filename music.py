from asyncio import Queue, Event

import discord
from discord.ext import commands, tasks
import youtube_dl


class VoiceState():
    def __init__(self, client :commands.Bot, ctx :commands.Context):
        self._client = client
        self._ctx = ctx
        self._next = Event()
        self._songs = Queue()
        self._audio_player = self._client.loop.create_task(self.audio_player_task())
    
    def __del__(self):
        self.audio_player_task.cancel()
        
    #
    # @tasks.loop()
    async def audio_player_task(self):
        print('I am a new task!')
        while True:
            self._next.clear() # Internal flag is set to false -> All threads are blocked if the calling wait()
            print('I am waiting for a new song ...')
            current = await self._songs.get()
            print('Got a new song!')
            vc = self._ctx.voice_client
            vc.play(current[2], after=self.toogle_next)
            print('I am waiting that the song is finished ...')
            await self._next.wait() # Thread is blocked until set() is called
            print('Waiting finished!')
        
    def toogle_next(self, error=None):
        self._next.set()

    async def play_next_song(self, error=None):
        vc = self._ctx.voice_client
        if self._songs.empty():
            await self._ctx.send('Queue is empty')
        else:
            next = await self._songs.get()
            vc.stop()
            vc.play(next[2], after=self.toogle_next)
            await self._ctx.send('Skipped')
    
    async def add_song(self, source :discord.player.FFmpegOpusAudio):
        await self._songs.put(source)
        print('Add is finished')
        print(f'Queue: {self._songs}')

    async def join(self):
        if self._ctx.author.voice is None:
            await self._ctx.send('You are not in a voice channel!')
        voice_channel = self._ctx.author.voice.channel
        if self._ctx.voice_client is None:
            await voice_channel.connect()
            
        else:
            await self._ctx.voice_client.move_to(voice_channel)

    async def leave(self):
        if self._ctx.voice_client is not None and self._ctx.voice_client.is_connected():
            await self._ctx.voice_client.disconnect()

    async def play(self, url :str):
        await self.join()
        #ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format':"bestaudio", 'default_search':"ytsearch"}
        vc = self._ctx.voice_client
        
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            print(info['thumbnail'])
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            await self.add_song([info['title'], info['thumbnail'], source, url])

    async def clear(self):
        if self._ctx.voice_client is not None and not self._songs.empty():
            vc = self._ctx.voice_client
            for i in range(self._songs.qsize()):
                self._songs.get_nowait()
                self._songs.task_done()
            print(f'Queue: {self._songs}')
            await self._ctx.send('Queue is cleared')

    async def pause(self):
        if self._ctx.voice_client is not None and self._ctx.voice_client.is_playing():
            self._ctx.voice_client.pause()
            await self._ctx.send('Paused')
    
    async def resume(self):
        if self._ctx.voice_client is not None and self._ctx.voice_client.is_paused():
            self._ctx.voice_client.resume()
            await self._ctx.send('Resume')
    
    async def queue(self):
        if self._songs.empty():
            await self._ctx.send('Waiting queue is empty')
        else:
            for i in range(min(self._songs.qsize(),3)):
                song = self._songs.get_nowait()
                songList = discord.Embed(title=f'{i+1}. position', description='', color=0x00ff00)
                songList.add_field(name=str(f'{song[0]}'), value=str(f'{song[3]}'), inline=False)
                songList.set_image(url=song[1])
                song = self._songs.put_nowait(song)
                await self._ctx.send(embed=songList)


    async def help(self):
        commandList = discord.Embed(title="Command list", description="List of all commands", color=0x00ff00)
        for command in self._client.commands:
            commandList.add_field(name=str(f'{self._ctx.prefix}{command.name}'), value=str(command.brief), inline=False)
        await self._ctx.send(embed=commandList)


class music(commands.Cog):
    def __init__(self, client :commands.Bot):
        self._client = client
        self._voicestates = {}


    def getVoiceState(self, ctx :commands.Context):
        state = self._voicestates.get(ctx.guild.id)
        if not state:
            state = VoiceState(self._client, ctx)
            self._voicestates[ctx.guild.id] = state
        return state

    async def cog_before_invoke(self, ctx :commands.Context):
        self.getVoiceState(ctx)


    @commands.command(aliases=['connect'], brief='The player joins to your voice channel.', description='The player joins to your voice channel. If you are currently not in a voice channel than it will do nothing.')
    async def join(self, ctx :commands.Context):
        await self.getVoiceState(ctx).join()


    @commands.command(aliases=['disconnect'], brief='The Player disconnects from the voice channel.', description='The Player disconnects from the voice channel. If the player is not connected than it will do nothing.')
    async def leave(self, ctx :commands.Context):
        await self.getVoiceState(ctx).leave()


    @commands.command(aliases=[], brief='Plays a new song or storing it in the waiting queue.', description='Plays a new song if currently no song is played or storing it in the waiting queue.')
    async def play(self, ctx :commands.Context, url :str):
        await self.getVoiceState(ctx).play(url)
    

    @commands.command(aliases=[], brief='Clears all the songs in the waiting queue.', description='Clears all the songs in the waiting queue, but the current played song does not stop. If the Queue is empty, than it will do nothing.')
    async def clear(self, ctx :commands.Context):
        await self.getVoiceState(ctx).clear()
    

    @commands.command(aliases=['stop'], brief='Pause the current played song.', description='Pause the current played song. If no song is played, than it will do nothing.')
    async def pause(self, ctx :commands.Context):
        await self.getVoiceState(ctx).pause()
    

    @commands.command(aliases=['continue'], brief='Resume the current paused song.', description='Resume the current paused song. If no song is paused, than it will do nothing.')
    async def resume(self, ctx :commands.Context):
        await self.getVoiceState(ctx).resume()
    
    @commands.command(aliases=[], brief='Skip the current played song to next song from the waiting queue.', description='Skip the current played song to next song from the waiting queue. If the waiting queue is empty than it will do nothing.')
    async def skip(self, ctx :commands.Context):
        await self.getVoiceState(ctx).play_next_song()


    @commands.command(aliases=['sound'], brief='Sets the volume of the player from 0 to 100.', description='Sets the volume of the player from 0 to 100. If the player is not playing a song or the volume value is invalid than it will do nothing.')
    async def volume(self, ctx :commands.Context, volume :int):
        vc = ctx.voice_client
        if vc is None or 0 < volume > 100:
            return await ctx.send("Not connected to a voice channel")
        print(ctx.voice_client.source.volume)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f'Changed volume to {volume}')
        
    @commands.command(aliases=['songs'], brief='Display the waiting queue for songs.', description='Display the waiting queue for songs.')
    async def queue(self, ctx :commands.Context):
        await self.getVoiceState(ctx).queue()

    @commands.command(aliases=['commands', 'list'], brief='Display a list of comments, that can be used to use the player.', description='Display a list of comments, that can be used to use the player.')
    async def help(self, ctx :commands.Context):
        await self.getVoiceState(ctx).help()
        
def setup(client):
    client.add_cog(music(client))
        