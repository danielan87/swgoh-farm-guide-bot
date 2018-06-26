import asyncio
import discord
import json
import traceback
from crontab import CronTab
from settings import BOT_TOKEN
import datetime
client = discord.Client()

INTERVAL = '* * * * *'


async def speak(interval):
    await client.wait_until_ready()
    cron = CronTab(interval)
    while True:
        await asyncio.sleep(cron.next())
        channel = client.get_channel('461007062118170624')
        await client.send_message(channel, '<@288399728524263424>')


@client.event
async def on_ready():
        try:
            client.loop.create_task(speak(INTERVAL))
        except:
            print('Could not schedule task.')
            traceback.format_exc()


client.run(BOT_TOKEN)
# try:
#     client.run(os.environ['DISCORD_CRON_USER'], os.environ['DISCORD_CRON_PASS'])
# except KeyError:
#     client.run(BOT_TOKEN)
