from tabulate import tabulate

import discord
from discord.ext.commands import Bot
import main
import math
import re

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
    await client.say(
        "?ping, ?cmdlist, ?toonlist, ?shiplist, ?whohas (registered guild leaders: ?compute_tickets, ?ticket_dates, "
        "?register)")


@client.command(pass_context=True)
async def toonlist(ctx):
    """
    List of toons that we can query. It's limited to our needs
    :param ctx:
    :return:
    """
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
            result = main.get_who_has(" ".join(arguments[1:-1]), int(arguments[-1]))
            print("{} asked who has {} at {} stars (result: {})"
                  .format(str(ctx.message.author), " ".join(arguments[1:-1]), int(arguments[-1]), ", ".join(result)))
        else:
            result = main.get_who_has(arguments[1])
            print("{} asked who has {} (result: {})"
                  .format(str(ctx.message.author), " ".join(arguments[1:-1]), ", ".join(result)))
    await client.say(", ".join(result))


@client.command(pass_context=True)
async def compute_tickets(ctx):
    """
    Analyzes stored screenshots (the screenshots' data is actually extracted beforehand now) of a specific day and
    returns a table of players and their respective tickets
    :param ctx:
    :return:
    """
    if not main.is_registered_guild_leader(str(ctx.message.author)):
        print("{} tried to use compute_tickets while not being registered as guild leader".format(
            str(ctx.message.author)))
        await client.say("Command reserved to registered guild leaders.")
        return
    arguments = ctx.message.content.split(' ')
    if len(arguments) >= 2:
        if len(arguments[1]) == 8 and represents_int(arguments[1]):
            print("{} is calling compute_tickets with date {}.".format(str(ctx.message.author), arguments[1]))
            result, date = main.compute_tickets(str(ctx.message.author), arguments[1])
        else:
            await client.say("Wrong date format. Usage: ?compute_tickets (optional: <YYYYMMDD>")
            return
    else:
        print("{} is calling compute_tickets without date.".format(str(ctx.message.author)))
        result, date = main.compute_tickets(str(ctx.message.author))
    if result.empty:
        print("{} is calling compute_tickets but no result..")
        await client.say("Error processing images.")
    else:
        print("{} is calling compute_tickets but no result..")
        await client.say("{} Tickets:".format(date))
        df_str = tabulate(result, headers='keys', tablefmt='psql')
        # we want to split it in n messages of less than 2000 characters
        n = math.ceil(len(df_str) / 2000)
        l = int(len(result) / n)
        for i in range(n):
            max = i * l + l
            if max > len(result):
                max = len(result)
            await client.say(tabulate(result[i * l:max], headers='keys', tablefmt='psql'))


@client.command(pass_context=True)
async def ticket_dates(ctx):
    """
        List of available dates for tickets for an author.
        :param ctx:
        :return:
        """
    if not main.is_registered_guild_leader(str(ctx.message.author)):
        print("{} tried to use compute_tickets while not being registered as guild leader".format(
            str(ctx.message.author)))
        await client.say("Command reserved to registered guild leaders.")
        return
    result = main.get_available_ticket_dates(str(ctx.message.author))
    print("{} asked for the list of ticket dates (result: {})".format(str(ctx.message.author), ", ".join(result)))
    await client.say(", ".join(result))


@client.command(pass_context=True)
async def register(ctx):
    """
        List of available dates for tickets for an author.
        :param ctx:
        :return:
        """
    if not main.is_registered_guild_leader(str(ctx.message.author)):
        print("{} tried to use compute_tickets while not being registered as guild leader".format(
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


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


client.run("MzcxNzY5OTgwNTU3MTk3MzI1.DM6dUw.igwuz1R0hWfTNQPh5Ery94Lrfs4")
