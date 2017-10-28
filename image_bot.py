import discord
from discord.ext.commands import Bot
import main

Client = discord.Client()
bot_prefix = "?"
client = Bot(command_prefix=bot_prefix)


@client.event
async def on_ready():
    print("Bot online!")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))


@client.async_event
async def on_message(message):
    if message.attachments:
        for a in message.attachments:
            filename = a['filename']
            if filename.split('.')[-1] in ["png", "jpg", "jpeg"]:
                main.download_image_into_correct_folder(str(message.author), a)
                # await client.say("{} added".format(filename))


client.run("MzcxNzY5OTgwNTU3MTk3MzI1.DM6dUw.igwuz1R0hWfTNQPh5Ery94Lrfs4")
