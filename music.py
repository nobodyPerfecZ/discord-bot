import discord
from discord.ext import commands
import youtube_dl


class VoiceState():
    def __init__(self, client :commands.Bot, ctx :commands.Context):
        self._client = client
        self._ctx = ctx
        self._next = Event()
        self._songs = Queue()

        self._audio_player = client.loop.create_task(self.audio_player_task())

        async def audio_player_task(self):
            while True:
                self._songs.clear()
                current = await self._songs.get()
                current.start()
                await self._next.wait()



class music(commands.Cog):
    def __init__(self, client :commands.Bot):
        self._client = client

    
    @commands.command(aliases=['connect'])
    async def join(self, ctx :commands.Context):
        if ctx.author.voice is None:
            await ctx.send('You are not in a voice channel!')
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command(aliases=['disconnect'])
    async def leave(self, ctx :commands.Context):
        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            await ctx.voice_client.disconnect()
        
    @commands.command(aliases=[])
    async def play(self, ctx :commands.Context, url :str):
        await self.join(ctx)
        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format':"bestaudio", 'default_search':"ytsearch"}
        vc = ctx.voice_client
        
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                vc.play(source)
            except Exception:
                await ctx.send('Not supported URL')
    
    @commands.command(aliases=[])
    async def stop(self, ctx :commands.Context):
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send('Stopped')
    
    @commands.command(aliases=[])
    async def pause(self, ctx :commands.Context):
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send('Paused')
    
    @commands.command(aliases=['continue'])
    async def resume(self, ctx :commands.Context):
        if ctx.voice_client is not None and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send('Resume')


    @commands.command(aliases=[])
    async def volume(self, ctx :commands.Context, volume :int):
        vc = ctx.voice_client
        if vc is None or 0 < volume > 100:
            return await ctx.send("Not connected to a voice channel")
        print(ctx.voice_client.source.volume)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f'Changed volume to {volume}')
        
    
    @commands.command(aliased=['commands'])
    async def list(self, ctx :commands.Context):
        return 0
        
def setup(client):
    client.add_cog(music(client))
        