import asyncio
import discord
import os
import json
import traceback
from crontab import CronTab
from settings import BOT_TOKEN
import datetime
client = discord.Client()


INTERVAL = '49 0 * * *'
channel_list_file = r'rotations/master_channel_list.txt'


async def speak(interval):
    await client.wait_until_ready()
    cron = CronTab(interval)
    while True:
        await asyncio.sleep(cron.next())
        try:
            with open(channel_list_file) as f:
                content = f.readlines()
            content = [x.strip() for x in content]
            today = datetime.datetime.today().strftime('%m/%d/%y')
            for c in content:
                channel = c
                with open(r'rotations/{}'.format(channel)) as f:
                    rot = json.load(f)
                i = 1
                text = "{}: ".format(today)
                new_json = {}
                for key in sorted(rot.keys()):
                    new_rot = rot[key][1:] + [rot[key][0]]
                    new_json[key] = new_rot

                    for v in new_rot:
                        text += "{}) {}, ".format(i, v)
                        i += 1
                text = text[:-2]
                with open(r'rotations/{}'.format(channel), 'w') as outfile:
                    json.dump(new_json, outfile)

                channel = client.get_channel(channel.strip())
                text = text.strip()

                print('Scheduling {} with schedule {}'.format(text, INTERVAL))
                await client.send_message(channel, text)
        except Exception as e:
            print('I could not send rotations :(')
            print(e)


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
