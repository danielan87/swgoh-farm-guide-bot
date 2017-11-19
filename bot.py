import discord
import logging
from discord.ext.commands import Bot
import main
import re
import time
import os
import datetime
from settings import BOT_TOKEN
import matplotlib
matplotlib.rc('axes.formatter', useoffset=False)
matplotlib.use('Agg')

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

Client = discord.Client()
bot_prefix = "?"
client = Bot(command_prefix=bot_prefix)


@client.event
async def on_ready():
    """
    Print this when bot is initialized
    :return:
    """
    print("Bot online!")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))


@client.command(pass_context=True)
async def ping(ctx):
    """
    check if bot is up!
    :param ctx:
    :return:
    """
    print("{} pinged!".format(str(ctx.message.author)))
    await client.say("Pong!")


@client.command(pass_context=True)
async def cmdlist(ctx):
    """
    list of commands available
    :param ctx:
    :return:
    """
    print("{} asked for the command list!".format(str(ctx.message.author)))
    embed = discord.Embed(title="List of Commands", colour=discord.Colour(0x000000),
                          timestamp=datetime.datetime.now())

    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/220661132938051584/c4a8d173a5453075db64264387413fff.png")
    embed.set_footer(
        text="Hogtown Bot",
        icon_url="https://cdn.discordapp.com/icons/220661132938051584/c4a8d173a5453075db64264387413fff.png")

    embed.add_field(name="?ping", value="Check if the bot is running.", inline=False)
    embed.add_field(name="?cmdlist", value="List all available commands.", inline=False)
    embed.add_field(name="?toonlist", value="List of available toons. Values used by **\"?whohas\"**.",
                    inline=False)
    embed.add_field(name="?shiplist", value="List of available ships. Values used by **\"?whohas\"**.",
                    inline=False)
    embed.add_field(name="?whohas <UNIT-NAME> (optional: <MIN-STAR>)",
                    value="List players that have this toon at a certain number of stars.\n**Example:** ?whohas CUP 7",
                    inline=False)
    embed.add_field(name="OFFICERS ONLY", value="**The following commands are only available to officers:**",
                    inline=False)
    embed.add_field(name="?tickets <DATE>",
                    value="Gives the number of tickets of each player at the last date available or on a certain date "
                          "in a formatted table. Also returns an Excel attachment.\nDate format must be **YYYYMMDD**.",
                    inline=False)
    embed.add_field(name="?ticketsxls <DATE>",
                    value="Gives the number of tickets of each player at the last date available or on a certain date "
                          "in an \"xls\" format (separated by \";\"). Also returns an Excel attachment."
                          "\nDate format must be **YYYYMMDD**.", inline=False)
    embed.add_field(name="?ticket_dates",
                    value="Returns the list of all the available dates where ticket numbers are stored "
                          "(used by **?tickets**, **?ticketdates** and **?diff**)", inline=False)
    embed.add_field(name="?diff <DATE_1> <DATE_2>",
                    value="Gives the difference of tickets between two dates. \nDate format must be **YYYYMMDD**.",
                    inline=False)
    embed.add_field(name="?register discord_id", value="Register a player as an officer. discord_id is case sensitive!",
                    inline=False)

    await client.say(embed=embed)


@client.command(pass_context=True)
async def toonlist(ctx):
    """
    List of toons that we can query. It's limited to our needs
    :param ctx:
    :return:
    """
    await client.say("Command disabled.")
    return
    result = main.get_toon_list()
    print("{} asked for the toon list (result: {})".format(str(ctx.message.author), ", ".join(result)))
    await client.say(", ".join(result))


@client.command(pass_context=True)
async def shiplist(ctx):
    """
        List of ships that we can query. It's limited to our needs
        :param ctx:
        :return:
        """
    await client.say("Command disabled.")
    return
    result = main.get_ship_list()
    print("{} asked for the ship list (result: {})".format(str(ctx.message.author), ", ".join(result)))
    await client.say(", ".join(result))


@client.command(pass_context=True)
async def whohas(ctx):
    """
    returns who possesses a toon or ship
    :param ctx:
    :return:
    """
    arguments = ctx.message.content.split(' ')
    if len(arguments) == 1:
        await client.say("Usage: ?whohas <UNIT-NAME> (optional: <MIN-STAR>")
        await client.say("Usage: ?whohas shiplist for the list of ships")
        await client.say("Usage: ?whohas toonlist for the list of toons")
        return
    else:
        if len(arguments) > 2 and represents_int(arguments[-1]):

            results = main.get_who_has_generic(" ".join(arguments[1:-1]), int(arguments[-1]))
            print("{} asked who has {} at {} stars"
                  .format(str(ctx.message.author), " ".join(arguments[1:-1]), int(arguments[-1])))
        else:
            results = main.get_who_has_generic(" ".join(arguments[1:]))
            print("{} asked who has {}"
                  .format(str(ctx.message.author), " ".join(arguments[1:-1])))
    if not results:
        await client.say("No player found or unit not found...")
    else:
        for r in results:
            name = r.get('name')
            result = r.get('result')
            if not result:
                await client.say("No one has {}".format(name))
                return
            icon = r.get('icon')
            embed = discord.Embed(colour=discord.Colour(0x000000),
                                  timestamp=datetime.datetime.now(),
                                  description="List of players ordered by GP")

            if not icon:
                icon = ''
            embed.set_thumbnail(
                url=icon)
            embed.set_footer(text="Hogtown Bot",
                             icon_url="https://cdn.discordapp.com/icons/220661132938051584/c4a8d173a5453075db64264387413fff.png")
            embed.add_field(name=name, value="\n".join(
                ["{} ({})".format(p.get('player'), p.get('power')) for p in sorted(result, key=lambda k: k['power'])]))

            await client.say(embed=embed)


@client.command(pass_context=True)
async def tickets(ctx):
    """
    Analyzes stored screenshots (the screenshots' data is actually extracted beforehand now) of a specific day and
    returns a table of players and their respective tickets
    :param ctx:
    :return:
    """
    message, str_result, result = generate_tickets(ctx, mode='tabulate')
    if message:
        await client.say(message)
    if str_result and type(str_result) == list:
        for s in str_result:
            await client.say(s)
    if not result.empty:
        filename = '{}-tickets.xls'.format(str(ctx.message.author))
        result.to_excel(filename, sheet_name="tickets")
        await client.upload(filename)
        os.remove(filename)


@client.command(pass_context=True)
async def ticketsxls(ctx):
    """
    Analyzes stored screenshots (the screenshots' data is actually extracted beforehand now) of a specific day and
    returns a table of players and their respective tickets
    :param ctx:
    :return:
    """
    message, str_result, result = generate_tickets(ctx, mode='csv')
    if message:
        await client.say(message)
    if str_result:
        if type(str_result) == list:
            for s in str_result:
                await client.say(s)
        else:
            await client.say(str_result)
    if not result.empty:
        filename = '{}-tickets.xls'.format(str(ctx.message.author))
        result.to_excel(filename, sheet_name="tickets")
        await client.upload(filename)
        os.remove(filename)


def generate_tickets(ctx, mode='tabulate'):
    if not main.is_registered_guild_leader(str(ctx.message.author)):
        print("{} tried to use tickets while not being registered as guild leader".format(
            str(ctx.message.author)))
        return "Command reserved to registered guild leaders.", []
    arguments = ctx.message.content.split(' ')
    if len(arguments) >= 2:
        if len(arguments[1]) == 8 and represents_int(arguments[1]):
            print("{} is calling tickets with date {}.".format(str(ctx.message.author), arguments[1]))
            result, date = main.compute_tickets(str(ctx.message.author), arguments[1])
        else:
            return "Wrong date format. Usage: ?tickets (optional: <YYYYMMDD>", []
    else:
        print("{} is calling tickets without date.".format(str(ctx.message.author)))
        result, date = main.compute_tickets(str(ctx.message.author))
    if result.empty:
        print("{} is calling tickets but no result..".format(str(ctx.message.author)))

        return "Error processing images.", []
    else:
        if mode == 'tabulate':
            split = main.get_split_tabulate_df(result)
        elif mode == 'csv':
            split = main.get_split_csv(result)
        message = "{} Tickets:\n".format(date)
        return message, split, result


@client.command(pass_context=True)
async def ticket_dates(ctx):
    """
        List of available dates for tickets for an author.
        :param ctx:
        :return:
        """
    if not main.is_registered_guild_leader(str(ctx.message.author)):
        print("{} tried to use ticket_dates while not being registered as guild leader".format(
            str(ctx.message.author)))
        await client.say("Command reserved to registered guild leaders.")
        return
    result = main.get_available_ticket_dates(str(ctx.message.author))
    print("{} asked for the list of ticket dates (result: {})".format(str(ctx.message.author), ", ".join(result)))
    await client.say(", ".join(result))


@client.command(pass_context=True)
async def diff(ctx):
    """
    Compare ticket counts between 2 dates
    :param ctx:
    :return:
    """
    if not main.is_registered_guild_leader(str(ctx.message.author)):
        print("{} tried to use diff while not being registered as guild leader".format(
            str(ctx.message.author)))
        await client.say("Command reserved to registered guild leaders.")
        return
    arguments = ctx.message.content.split(' ')
    if len(arguments) < 3:
        await client.say("Error! diff usage: ?diff <DATE_1> <DATE_2> (date format: YYYYMMDD)")
        return
    date1 = arguments[1]
    date2 = arguments[2]
    try:
        time.strptime(date1, "%Y%m%d")
        time.strptime(date2, "%Y%m%d")
    except ValueError:
        await client.say("Error! date format should be YYYYMMDD")
        return
    date_list = main.get_available_ticket_dates(str(ctx.message.author))
    if date1 not in date_list or date2 not in date_list:
        await client.say("Error! One of the given dates does not have data stored.")
        await client.say("Available dates: {}".format(", ".join(date_list)))
        return
    result = main.compute_diff(str(ctx.message.author), date1, date2)
    splitted = main.get_split_tabulate_df(result)
    for s in splitted:
        await client.say(s)


@client.command(pass_context=True)
async def register(ctx):
    """
        List of available dates for tickets for an author.
        :param ctx:
        :return:
        """
    if not main.is_registered_guild_leader(str(ctx.message.author)):
        print("{} tried to use register while not being registered as guild leader".format(
            str(ctx.message.author)))
        await client.say("Command reserved to registered guild leaders.")
        return
    arguments = ctx.message.content.split(' ')
    if len(arguments) >= 2:
        to_register = arguments[1]
        pattern = re.compile('.+#\d+')
        if pattern.match(to_register):
            main.register_guild_leader(to_register)
            await client.say("{} registered!".format(to_register))
        else:
            await client.say("The given ID is not a discord ID.")


@client.command(pass_context=True)
async def guildgp(ctx):
    """
    Returns a plot of guild gp
    :param ctx:
    :return:
    """
    resp = main.plot_guild_gp()

    plot = resp['df'].plot(colormap='jet', title="Guild Galactic Power Evolution", x_compat=True)
    plot.get_yaxis().get_major_formatter().set_useOffset(False)
    plot.set_xlabel("Dates")
    plot.set_ylabel("GP")
    fig = plot.get_figure()
    filename = 'output.png'
    fig.savefig(filename)
    await client.upload(filename)
    url = ''
    async for message in client.logs_from(ctx.message.channel, limit=1):
        if message.author == client.user and message.attachments:
            url = message.attachments[0]['url']
            await client.delete_message(message)
    os.remove(filename)
    embed = discord.Embed(title="Bispen's Galactic Power Evolution", colour=discord.Colour(0x000000),
                          timestamp=datetime.datetime.now())

    embed.set_image(url=url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/220661132938051584/c4a8d173a5453075db64264387413fff.png")
    embed.set_footer(text="Bispen Bot",
                     icon_url="https://cdn.discordapp.com/icons/220661132938051584/c4a8d173a5453075db64264387413fff.png")

    if resp.get('mean'):
        embed.add_field(name="Guild Average", value="{}GP per day".format(resp['mean']))

    await client.say(embed=embed)


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


client.run(BOT_TOKEN)
