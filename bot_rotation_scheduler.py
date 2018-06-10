import asyncio
import discord
import json
import traceback
from crontab import CronTab
from settings import BOT_TOKEN
import datetime
client = discord.Client()
import os

INTERVAL = '* * * * *'
channel_list_file = r'rotations/master_channel_list.txt'


async def speak(interval):
    await client.wait_until_ready()
    cron = CronTab(interval)
    while True:
        await asyncio.sleep(cron.next())
        try:
            with open(channel_list_file) as f:
                content = f.readlines()
            content = [x.strip().split(';') for x in content if x.strip()]
            today = datetime.datetime.today()
            today_str = today.strftime('%m/%d/%y')
            hour = today.strftime('%H%M')
            to_rotate = [c[0].strip() for c in content if c[1] == hour]

            for c in os.listdir(r'rotations/broadcast'):
                try:
                    if not c.strip():
                        continue
                    channel = c.strip()
                    with open(r'rotations/{}'.format(channel)) as f:
                        rot = json.load(f)
                    i = 1
                    text = "{}: ".format(today_str)
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
                    if not channel:
                        raise ValueError('Error with channel {}: Not found'.format(channel))
                    text = text.strip()

                    print('Scheduling {} with schedule {}'.format(text, INTERVAL))
                    await client.send_message(channel, text)

                    os.remove(r'rotations/broadcast/{}'.format(c))
                except Exception as e:
                    print('I could not send rotations for channel {} :('.format(channel))
                    print(e)

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
