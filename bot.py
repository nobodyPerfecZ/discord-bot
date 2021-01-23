import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!")

## all events are listed here ## 

# prints something, if the bot is ready
@bot.event
async def on_ready():
    print('Logged on as {0}'.format(bot.user))

# prints a hello message, if the user prints 'Hello' in the discord chat 
@bot.event
async def on_message(message):
    if (message.author == bot.user): # to stop infinite loop it if the bot is sending a message
        return
    if (message.channel.id == 248897274002931722): # channel id of textchannel 'chat'
        if(message.content.startswith('Hello')):
            await message.channel.send('Hello {0.author}'.format(message))
        await bot.process_commands(message) # has to be called for command handler

## all comments are listed here ## 
@bot.command()
async def mute(ctx,arg):
    await ctx.send(arg)

@bot.command()
async def kick(ctx,arg):
    await ctx.send(arg)

@bot.command()
async def move(ctx,arg):
    await ctx.send(arg)

@bot.command()
async def mute(ctx,arg):
    await ctx.send(arg)

@bot.command()
async def ban(ctx,arg):
    await ctx.send(arg)

@bot.command()
async def remove(ctx,arg):
    await ctx.send(arg)

@bot.command()
async def delete(ctx,arg):
    await ctx.send(arg)

# run the bot on the server
bot.run('NTkzMDU4MTI5NzIyMjEyMzY0.XRIWbA.yAmZ1vhg_j9rV1OklbxA9ZjL4J8')