import discord

class MyClient(discord.Client):
    # prints something, if the bot is ready
    async def on_ready(self):
        print('Logged on as {0}'.format(self.user))

    # prints the message on the console that the bot gets in Discord 
    async def on_message(self, message):
        print('Message from {0.author}({0.author.id}):{0.content}'.format(message))

client = MyClient()
# run the bot on the server
client.run('NTkzMDU4MTI5NzIyMjEyMzY0.XRIWbA.yAmZ1vhg_j9rV1OklbxA9ZjL4J8')