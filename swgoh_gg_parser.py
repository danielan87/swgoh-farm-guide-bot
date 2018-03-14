from lxml import html
import requests
import pandas as pd
import os


def store_guild_roster_gp(guild_link):
    page = requests.get(guild_link)
    tree = html.fromstring(page.content)

    tr = tree.xpath('//table//tr/td[1]')
    player_names = [t.xpath('a/strong/text()')[0] for t in tr]

    tr = tree.xpath('//table//tr/td[2]')
    gps = [t.xpath('text()')[0] for t in tr]

    today = '{:%m-%d-%y}'.format(pd.datetime.today())
    d = {'player_name': player_names, today: gps}
    df = pd.DataFrame(data=d)

    guild_id = guild_link.split('/')[4]
    directory = 'gps/{}/'.format(guild_id)
    csv_filename = 'gps.csv'

    if os.path.exists(directory + csv_filename):
        temp = pd.read_csv(directory + csv_filename)
        if today in list(temp.columns.values):
            temp = temp.drop([today], axis=1)
        df = pd.merge(df, temp, on='player_name', how='outer')
    else:
        os.makedirs(directory)
    df.to_csv(directory + csv_filename, index=False)
    return True
