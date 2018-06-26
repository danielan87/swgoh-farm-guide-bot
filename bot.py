from collections import OrderedDict
import discord
import logging
from discord.ext.commands import Bot
import main
import hstr_readiness
import re
import time
import os
import datetime
from settings import BOT_TOKEN
import matplotlib
import math

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
client.remove_command("help")

MAX_HSTR_TEAMS_PER_EMBED = 28


@client.event
async def on_ready():
    """
    Print this when bot is initialized
    :return:
    """
    print("Bot online!")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    log("Bot online")
    await client.change_presence(game=discord.Game(name='?h for help'))


@client.command(pass_context=True)
async def ping(ctx):
    """
    check if bot is up!
    :param ctx:
    :return:
    """
    print("{} pinged!".format(str(ctx.message.author)))
    log("{} pinged!".format(str(ctx.message.author)))
    await client.say("Pong!")


@client.command(pass_context=True)
async def h(ctx):
    """
    list of commands available
    :param ctx:
    :return:
    """
    print("{} asked for the command list!".format(str(ctx.message.author)))
    log("{} asked for h".format(str(ctx.message.author)))
    embed = discord.Embed(title="List of Commands", colour=discord.Colour(0x000000),
                          timestamp=datetime.datetime.now())

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
    embed.set_footer(
        text="DSR Bot",
        icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")

    embed.add_field(name="?ping", value="Check if the bot is running.", inline=False)
    embed.add_field(name="?h", value="List all available commands.", inline=False)
    embed.add_field(name="?sithraid",
                    value="Analyze Heroic Sith Raid Readiness for a guild "
                          "(usage: `?sithraid <list of <swgoh.gg url of the guild/player>>)` optional: "
                          "Add \"details\" at the end to get assignments.",
                    inline=False)
    embed.add_field(name="?sithraidteams",
                    value="Teams used to analyze your roster for the raid.",
                    inline=False)
    embed.add_field(name="?add_rotation",
                    value="Bind a rotation to a channel. Usage: `?add_rotation player1 player2 player3 ...`. "
                          "New rotation will be sent everyday at 12:30am EST. Possible to add a second rotation "
                          "behind.",
                    inline=False)
    embed.add_field(name="?del_rotation",
                    value="Remove rotation bound to the current channel.",
                    inline=False)
    embed.add_field(name="?rotation",
                    value="Prints the current channel's rotation.",
                    inline=False)
    embed.add_field(name="?rotate",
                    value="Force a rotation.",
                    inline=False)
    embed.add_field(name="?set_rotation_time",
                    value="Change the rotation time. example: `?set_rotation_time 1959` will give the rotation "
                          "everyday at 19:59 EST.",
                    inline=False)
    embed.add_field(name="For more help or suggestions:",
                    value="Contact JubeiNabeshin#8860",
                    inline=False)
    embed.add_field(name="About DSR:",
                    value="DeathStarRow is an alliance of 4 guilds, from 100m to 160m GP. 2 guilds have HSTR on farm!",
                    inline=False)
    embed.add_field(name="SWA:",
                    value="https://swgoh.gg/g/646/deathstarrow-swa/",
                    inline=False)
    embed.add_field(name="J&J:",
                    value="https://swgoh.gg/g/861/deathstarrow-jj/",
                    inline=False)
    embed.add_field(name="O.D.B.:",
                    value="https://swgoh.gg/g/10294/deathstarrow-odb/",
                    inline=False)
    embed.add_field(name="SOK:",
                    value="https://swgoh.gg/g/27003/deathstarrow-sok/",
                    inline=False)
    embed.add_field(name="Recruitment server:",
                    value="https://discord.gg/AhMvsJT",
                    inline=False)
    embed.add_field(name="To invite the bot in your own server:",
                    value="https://discordapp.com/oauth2/authorize?client_id=436693905736466432&permissions=0&scope=bot",
                    inline=False)

    await client.say(embed=embed)


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
            embed.set_footer(text="DSR Bot",
                             icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
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
    embed = discord.Embed(title="Bespin's Galactic Power Evolution", colour=discord.Colour(0x000000),
                          timestamp=datetime.datetime.now())

    embed.set_image(url=url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
    embed.set_footer(text="Bespin Bot",
                     icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")

    if resp.get('mean'):
        embed.add_field(name="Guild Average", value="{}GP per day".format(resp['mean']))

    await client.say(embed=embed)


@client.command(pass_context=True)
async def farmneeds(ctx):
    """
    Returns a plot of guild gp
    :param ctx:
    :return:
    """
    toons, ships = main.get_toons_with_rarity(7)

    toons = sorted(toons, key=lambda k: k['need'])
    ships = sorted(ships, key=lambda k: k['need'])
    toon_res = ''
    ship_res = ''
    for t in toons:
        toon_res += "{}: {}\n".format(t['name'], t['need'])
    for t in ships:
        ship_res += "{}: {}\n".format(t['name'], t['need'])
    embed = discord.Embed(title="JnJ's Farm Needs", colour=discord.Colour(0x000000),
                          timestamp=datetime.datetime.now())

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
    embed.set_footer(text="DSR Bot",
                     icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")

    embed.add_field(name='Characters:', value=toon_res)
    embed.add_field(name='Ships:', value=ship_res)
    await client.say(embed=embed)


@client.command(pass_context=True)
async def analyze_roster(ctx, url):
    response = main.analyze_roster(url)
    if not response:
        await client.say("invalid url")
        return

    for team_name, values in response.items():
        embed = discord.Embed(title="{} Readiness for HSTR".format(team_name), colour=discord.Colour(0x000000),
                              url=url,
                              timestamp=datetime.datetime.now())
        embed.set_thumbnail(url="https:{}".format(values['icon']))
        embed.set_author(name="DeathStarRow Bot",
                         icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
        embed.set_footer(text="DeathStarRow",
                         icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
        total_completion = 0
        for toon in values.values():
            if isinstance(toon, str):
                continue
            msg = "G{} / {} stars / level {} / {} power / completion: {:.2f}%".format(toon.get('gear_level', 0),
                                                                                      toon.get('rarity', 0),
                                                                                      toon.get('level', 0),
                                                                                      toon.get('power', 0),
                                                                                      toon['completion'])
            total_completion += toon['completion']
            embed.add_field(name=toon['name'], value=msg, inline=True)
        embed.add_field(name="Readiness", value="**{:.2f}%**".format(total_completion / len(values)), inline=False)
        await client.say(embed=embed)


@client.command(pass_context=True)
async def sithraid(ctx, *params):
    details = True if params[-1] == 'details' else False
    log("{} asked for ?sithraid {} {}".format(str(ctx.message.author), params, details))
    urls = params[:-1] if details else params
    url = urls[0]
    messages, breakdown = hstr_readiness.analyze_guild_hstr_readiness(urls)
    if not messages:
        await client.say("invalid url")
        return

    embed = discord.Embed(title="HSTR Readiness", colour=discord.Colour(0x000000),
                          url=url,
                          timestamp=datetime.datetime.now())
    embed.set_author(name="DeathStarRow Bot",
                     icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
    embed.set_footer(text="DeathStarRow",
                     icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
    for msg in messages:
        embed.add_field(name=msg[0], value=msg[1], inline=False)
    await client.say(embed=embed)

    if details:
        breakdown = OrderedDict(sorted(breakdown.items()))
        for phase, teams in breakdown.items():
            if len(teams) < MAX_HSTR_TEAMS_PER_EMBED:
                embed = discord.Embed(title="HSTR {} Assignments".format(phase), colour=discord.Colour(0x000000),
                                      url=url,
                                      timestamp=datetime.datetime.now())
                embed.set_author(name="DeathStarRow Bot",
                                 icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
                embed.set_footer(text="DeathStarRow",
                                 icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
                for team_name, v in teams.items():
                    embed.add_field(name="{} - {} (Goal: {}%) - eligibility: {}".format(team_name, v['comp'], v['goal'],
                                                                                        v['eligibility']),
                                    value=", ".join(v['players']),
                                    inline=False)
                await client.send_message(ctx.message.author, embed=embed)
            else:
                nb = math.ceil(len(teams) / MAX_HSTR_TEAMS_PER_EMBED)
                for i in range(1, nb + 1):
                    embed = discord.Embed(title="HSTR {} Assignments ({}/{})".format(phase, i, nb), colour=discord.Colour(0x000000),
                                          url=url,
                                          timestamp=datetime.datetime.now())
                    embed.set_author(name="DeathStarRow Bot",
                                     icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
                    embed.set_footer(text="DeathStarRow",
                                     icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
                    for team_name, v in list(teams.items())[(i - 1) * MAX_HSTR_TEAMS_PER_EMBED:i * MAX_HSTR_TEAMS_PER_EMBED if i * MAX_HSTR_TEAMS_PER_EMBED < len(teams) else len(teams)]:
                        embed.add_field(
                            name="{} - {} (Goal: {}%) - eligibility: {}".format(team_name, v['comp'], v['goal'],
                                                                                v['eligibility']),
                            value=", ".join(v['players']),
                            inline=False)
                    await client.send_message(ctx.message.author, embed=embed)
        await client.send_message(ctx.message.author, 'Use ?sithraidteams for other eligible team compositions')


@client.command(pass_context=True)
async def sithraidteams(ctx):
    log("{} asked for sithraidteams".format(str(ctx.message.author)))
    messages = hstr_readiness.get_hstr_teams()
    if not messages:
        await client.say("Error retrieving the hstr teams.")
        return

    messages = OrderedDict(sorted(messages.items()))
    for phase, teams in messages.items():
        if len(teams) < MAX_HSTR_TEAMS_PER_EMBED:
            embed = discord.Embed(title="HSTR Teams for {}".format(phase), colour=discord.Colour(0x000000),
                                  timestamp=datetime.datetime.now())
            embed.set_author(name="DeathStarRow Bot",
                             icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
            embed.set_footer(text="DeathStarRow",
                             icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
            for name, msg in teams.items():
                embed.add_field(name=name, value=msg, inline=False)
            await client.send_message(ctx.message.author, embed=embed)
        else:
            nb = math.ceil(len(teams) / MAX_HSTR_TEAMS_PER_EMBED)
            for i in range(1, nb + 1):
                embed = discord.Embed(title="HSTR Teams for {} ({}/{})".format(phase, i, nb),
                                      colour=discord.Colour(0x000000),
                                      timestamp=datetime.datetime.now())
                embed.set_author(name="DeathStarRow Bot",
                                 icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
                embed.set_footer(text="DeathStarRow",
                                 icon_url="https://cdn.discordapp.com/attachments/415589715639795722/417845131656560640/DSR.png")
                for name, msg in list(teams.items())[(i - 1) * MAX_HSTR_TEAMS_PER_EMBED:i * MAX_HSTR_TEAMS_PER_EMBED if i * MAX_HSTR_TEAMS_PER_EMBED < len(teams) else len(teams)]:
                    embed.add_field(name=name, value=msg, inline=False)
                await client.send_message(ctx.message.author, embed=embed)
    await client.say("Teams sent via DM!")


@client.command(pass_context=True)
async def count(ctx):
    if ctx.message.author.display_name != 'JubeiNabeshin' and ctx.message.author.discriminator != '8860':
        await client.say('Unauthorized.')
        return
    await client.say('Number of servers: {}.'.format(len(client.servers)))
    for s in list(client.servers):
        await client.say('Server name: {} / Owner: {}\n'.format(s.name, s.owner))


@client.command(pass_context=True)
async def add_rotation(ctx, *args):
    today, tomorrow = main.add_rotation(ctx.message.channel.id, list(args))
    await client.say('Rotation added! Current rotation: {}.'.format(today))
    await client.say('Tomorrow\'s rotation: {}.'.format(tomorrow))


@client.command(pass_context=True)
async def del_rotation(ctx):
    if main.del_rotation(ctx.message.channel.id):
        await client.say('Rotation removed!')
    else:
        await client.say('No rotation found.')


@client.command(pass_context=True)
async def rotation(ctx):
    await client.say(main.get_rotation(ctx.message.channel.id))


@client.command(pass_context=True)
async def rotate(ctx):
    await client.say(main.rotate(ctx.message.channel.id))


@client.command(pass_context=True)
async def set_rotation_time(ctx, *args):
    t = list(args)
    if len(t) != 1:
        await client.say('Too many arguments. Give an hour in a 4 digit format. Example: `0030`')
        return
    t = args[0]
    if not re.search(r'\d{4}', t):
        await client.say('Bad format. Give an hour in a 4 digit format. Example: `0030`')
        return

    await client.say(main.set_rotation_time(ctx.message.channel.id, t))


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def log(msg):
    filename = "logs/bot-{:%Y%m%d}.log".format(datetime.date.today())
    if os.path.exists(filename):
        append_write = 'a'  # append if already exists
    else:
        append_write = 'w'  # make a new file if not

    f = open(filename, append_write)
    f.write(msg + '\n')
    f.close()


client.run(BOT_TOKEN)
