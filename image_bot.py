import discord
from discord.ext.commands import Bot
import main
import datetime

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
    print("{} sent an image.".format(str(message.author)))
    if message.attachments:
        for a in message.attachments:
            filename = a['filename']
            if filename.split('.')[-1].lower() in ["png", "jpg", "jpeg"]:
                result, star = main.process_image(str(message.author), a)
                if result:
                    thumbnail_url = \
                        "https://cdn.discordapp.com/icons/220661132938051584/c4a8d173a5453075db64264387413fff.png"
                    embed = discord.Embed(title="List of Toons in Platoon", colour=discord.Colour(0x000000),
                                          description="List of toons detected + players that own that toon at "
                                                      "**{}** Star. "
                                                      "(Player names displayed only if we have less than or eqal to "
                                                      "10)."
                                          .format(star),
                                          timestamp=datetime.datetime.now())

                    embed.set_thumbnail(url=thumbnail_url)
                    embed.set_footer(text="Hogtown Bot", icon_url=thumbnail_url)
                    for k, v in result.items():
                        if len(v.get('players')) < v.get('needed'):
                            markdown_type = 'c\n#'
                        else:
                            markdown_type = 'css\n'
                        if len(v.get('players')) > 10:
                            embed.add_field(name="{}x {}".format(v.get('needed'), k),
                                            value="```{} Number of players: {}```"
                                            .format(markdown_type, len(v.get('players'))),
                                            inline=True)
                        else:
                            embed.add_field(name="{}x {}".format(v.get('needed'), k),
                                            value="```{} Number of players: {} \n {}```"
                                            .format(markdown_type, len(v.get('players')),
                                                    " \n ".join(v.get('players'))),
                                            inline=True)

                    await client.send_message(message.channel, embed=embed)


client.run("MzcxNzY5OTgwNTU3MTk3MzI1.DM6dUw.igwuz1R0hWfTNQPh5Ery94Lrfs4")
