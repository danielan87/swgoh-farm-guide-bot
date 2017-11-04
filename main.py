import pandas as pd
from pandas import ExcelWriter
import os
import urllib.request
import json
from string import ascii_uppercase
import xlwt
import requests
import datetime
import swgoh_leader_tool.swgoh_leader_tool as tool
from tabulate import tabulate
import math


toons = {'CORUSCANTUNDERWORLDPOLICE': 'CUP',
         'KITFISTO': 'KitFisto',
         'LOBOT': 'Lobot',
         'LOGRAY': 'Logray',
         'PAO': 'Pao',
         'PAPLOO': 'Paploo',
         'PLOKOON': 'PloKoon',
         'UGNAUGHT': 'Ugnaught',
         'WICKET': 'Wicket',
         'FULCRUMAHSOKA': 'ATF'
         }

ships = {'UWINGSCARIF': 'BistanUWing',
         'UWINGROGUEONE': 'CassianUWing',
         'ARC170CLONESERGEANT': 'CloneArc',
         'TIEFIGHTERFIRSTORDER': 'FOTFTie',
         'GAUNTLETSTARFIGHTER': 'GauntletStarfighter',
         'GEONOSIANSTARFIGHTER3': 'GeoSpyStarfighter',
         'GHOST': 'Ghost',
         'COMMANDSHUTTLE': 'KyloCommandShuttle',
         'PHANTOM2': 'PhantomII',
         'BLADEOFDORIN': 'PloKoonStarfighter',
         'XWINGBLACKONE': 'PoeXwing',
         'XWINGRESISTANCE': 'ResistanceXwing',
         'ARC170REX': 'RexArc',
         'GEONOSIANSTARFIGHTER1': 'SunFacStarfighter',
         'TIEREAPER': 'TieReaper',
         'MFALCONEP7': 'MF'
         }

data = None


def read_dict_and_concat_to_main(dict_id, data, model_type):
    if dict_id not in data.keys():
        return pd.DataFrame()
    temp = pd.DataFrame(data[dict_id])
    temp = temp.set_index('player')
    temp = temp.drop(['combat_type', 'level', 'power'], 1)
    transco = toons
    if model_type == 'ships':
        transco = ships
    temp = temp.rename(columns={'rarity': transco[dict_id]})
    return temp


def get_data():
    """
    retrieve data from swgoh
    https://swgoh.gg/api/guilds/27003/units/
    :return:
    """
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

    url = "https://swgoh.gg/api/guilds/27003/units/"
    headers = {'User-Agent': user_agent, }

    request = urllib.request.Request(url, None, headers)  # The assembled request
    response = urllib.request.urlopen(request)
    data = json.loads(response.read().decode(), )  # The data u need

    return data


def create_toons_df(formula=False):
    data = get_data()
    result = None
    for k in toons.keys():
        if result is None:
            result = read_dict_and_concat_to_main(k, data, 'toons')
        else:
            temp = read_dict_and_concat_to_main(k, data, 'toons')
            result = result.join(temp, how='outer')
            result = result.fillna(0)
    result = result.astype(int)
    result = result.reindex(sorted(result.index, key=lambda x: x.lower()))
    if formula:
        result = add_star_count_to_df(result)
    return result


def create_ships_df(formula=False):
    data = get_data()
    result = None
    for k in ships.keys():
        if result is None:
            result = read_dict_and_concat_to_main(k, data, 'ships')
        else:
            temp = read_dict_and_concat_to_main(k, data, 'ships')
            result = result.join(temp, how='outer')
            result = result.fillna(0)
    result = result.astype(int)
    result = result.reindex(sorted(result.index, key=lambda x: x.lower()))
    if formula:
        result = add_star_count_to_df(result)
    return result


def add_star_count_to_df(df):
    nbplayers = df.shape[0]
    for i in range(8):
        addrow = pd.DataFrame([xlwt.Formula('COUNTIF({}2:{}{},"={}")'.format(x, x, nbplayers, i)) for x in
                               ascii_uppercase[1:df.shape[1] + 1]]).T
        addrow.columns = df.columns
        df = df.append(addrow).rename({0: '{} STAR'.format(i)})
    return df


def clear_data():
    global data
    data = None


def get_split_tabulate_df(df):
    splitted_df = []
    df_str = tabulate(df, headers='keys', tablefmt='psql')
    # we want to split it in n messages of less than 2000 characters
    n = math.ceil(len(df_str) / 2000)
    l = int(len(df) / n)
    for i in range(n):
        max = i * l + l
        if max > len(df):
            max = len(df)
        splitted_df.append(tabulate(df[i * l:max], headers='keys', tablefmt='psql'))
    return splitted_df


def get_who_has(unit, star=0):
    unit = unit.lower()
    toons_df = create_toons_df()
    toons_df.columns = map(str.lower, toons_df.columns)
    ships_df = create_ships_df()
    ships_df.columns = map(str.lower, ships_df.columns)
    if unit in toons_df.columns.tolist():
        result = toons_df[toons_df[unit] >= star][unit].index.tolist()
    elif unit in ships_df.columns.tolist():
        result = ships_df[ships_df[unit] >= star][unit].index.tolist()
    else:
        if unit in [x.lower() for x in list(toons.values())] or unit in [x.lower() for x in list(ships.values())]:
            return ["no one :("]
        return ['unit not found']
    if result:
        return result
    return ["no one :("]


def get_toon_list():
    return list(toons.values())


def get_ship_list():
    return list(ships.values())


def download_image_into_correct_folder(author, attachment):
    url = attachment['url']
    r = requests.get(url)
    now = datetime.datetime.now()
    newpath = os.path.join('images', author)
    if tool.check_if_ticket_image(str(author), url, mode='remote'):
        newpath = os.path.join(newpath, 'tickets')
    newpath = os.path.join(newpath, now.strftime('%Y%m%d'))
    os.makedirs(newpath, exist_ok=True)
    new_file_name = "{}_{}".format(now.strftime('%Y%m%d%H%M%S'), attachment['filename'])
    with open(os.path.join(newpath, new_file_name), 'xb') as outfile:
        outfile.write(r.content)


def compute_tickets(author, date=""):
    """
    Computes the ticket data for a date
    :param author:
    :param date:
    :return:
    """
    image_contents, date = tool.get_ticket_content(author, date)
    if not image_contents:
        print("No data found for tickets (author: {}, date: {}".format(author, date))
        return "No ticket data"
    result = pd.DataFrame()
    for i in image_contents:
        temp = tool.get_tickets_from_image(i)
        if temp.empty:
            print("WARNING: {} returned empty (skipped)".format(i))
            continue
        result = result.reset_index().merge(temp.reset_index(), how='outer', left_on='index', right_on='index')
        if 'Tickets_x' in result.columns.tolist():
            result.loc[:, 'Tickets'] = result['Tickets_x'].fillna(result['Tickets_y'])
        result = result[['index', 'Tickets']].set_index('index')
    print("Tickets computed successfully")
    return result, date


def get_available_ticket_dates(author):
    return tool.get_available_ticket_dates(author)


def register_guild_leader(name):
    return tool.register_guild_leader(name)


def is_registered_guild_leader(author):
    return tool.is_registered_guild_leader(author)


def compute_diff(author, date1, date2):
    tickets1, _ = compute_tickets(author, date1)
    tickets2, _ = compute_tickets(author, date2)
    tickets1.rename(columns={'Tickets': date1}, inplace=True)
    tickets2.rename(columns={'Tickets': date2}, inplace=True)
    merged = tickets1.reset_index().merge(tickets2.reset_index(), how='outer', left_on="index", right_on="index")\
        .set_index('index').fillna(0)
    merged.loc[:, 'diff'] = merged[date1].astype(int) - merged[date2].astype(int)
    merged['diff'] = merged['diff'].abs()
    return merged


# if __name__ == '__main__':
#     writer = ExcelWriter(os.path.join(os.getcwd(), 'farm_guide.xls'))
#     toons_df = create_toons_df(formula=True)
#     ships_df = create_ships_df(formula=True)
#     toons_df.to_excel(writer, 'toons')
#     ships_df.to_excel(writer, 'ships')
#     writer.save()
