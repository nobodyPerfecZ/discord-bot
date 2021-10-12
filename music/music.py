from asyncio import Queue, Event
from voicestate import VoiceState
import discord
from discord.ext import commands
import youtube_dl





class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_states = {}
    
    def get_voice_state(self, ctx :commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.client, ctx)
            self.voice_states[ctx.guild.id] = state
        
        return state

    '''
    ?
    '''
    def cog_unload(self):
        for state in self.voice_states.values():
            self.client.loop.create_task(state.stop())

    '''
    ?
    '''
    def cog_check(self, ctx :commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('this command can\'t be used in DM channels.')
        return True
    
    async def cog_before_invoke(self, ctx :commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    
    async def cog_command_error(self, ctx :commands.Context, error : commands.CommandError):
        await ctx.send('An error ocurred: {}'.format(str(error)))

    @commands.command()
    async def join(self, ctx :commands.Context):
        if ctx.author.voice is None:
            await ctx.send('You are not in a voice channel!')
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def leave(self, ctx :commands.Context):
        await ctx.voice_client.disconnect()
            


    @commands.command(aliases=['pl'])
    async def play(self, ctx :commands.Context, url :str):
        await self.join(ctx)
        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format':"bestaudio", 'default_search':"ytsearch"}
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source, after=None)
                    
    '''
    Pause the current played song.
    '''
    @commands.command(aliases=['pa'])
    async def pause(self, ctx :commands.Context):
        vc = ctx.voice_client
        if vc.is_playing():
            ctx.voice_client.pause()


    '''
    Stops the current played song.
    '''
    @commands.command(aliases=['st'])
    async def stop(self, ctx :commands.Context):
        vc = ctx.voice_client
        if vc.is_playing():
            ctx.voice_client.stop()
    

    '''
    Resumes the current stopped song.
    '''
    @commands.command(aliases=['r'])
    async def resume(self, ctx :commands.Context):
        vc = ctx.voice_client
        if vc.is_paused():
            ctx.voice_client.resume()
    
    '''
    Sets the volume to the new value.
    '''
    @commands.command(aliases=['v'])
    async def volume(self, ctx :commands.Context, volume :int):
        vc = ctx.voice_chat

        if not vc.is_playing():
            return await ctx.send('No music is currently played')
        
        if 0 > volume > 100:
            return await ctx.send('Volume should be between 0 and 100')
        
        vc.volume = volume / 100
        await ctx.send('Volume of the player set to {}%'.format(volume))



    @commands.command()
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now...')
        else:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

    
    @commands.command(aliases=['curr'])
    async def current_song(self, ctx :commands.Context):
        await ctx.send(embed=ctx.voice_state.current.create_embed())
        
        
def setup(client):
    client.add_cog(music(client))
        