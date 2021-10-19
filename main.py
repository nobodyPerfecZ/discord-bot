import discord
from discord.ext import commands
import music

client = commands.Bot(command_prefix='!', intents= discord.Intents.all(), help_command=None)

cogs = [music]

for i in range(len(cogs)):
    cogs[i].setup(client)

# run the bot on the server
client.run('NTkzMDU4MTI5NzIyMjEyMzY0.XRIWbA.yAmZ1vhg_j9rV1OklbxA9ZjL4J8')