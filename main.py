import pandas as pd
from lxml import html
import os
import urllib.request
import json
from string import ascii_uppercase
import xlwt
import requests
from requests.exceptions import *
import datetime
import swgoh_leader_tool.swgoh_leader_tool as tool
from tabulate import tabulate
import math
import difflib
from data import TOON_DATA
import redis
from settings import REDIS_CONN_INFO, GUILD_ID
from get_platoons_json import *

r = redis.StrictRedis(host=REDIS_CONN_INFO.get('host'), port=REDIS_CONN_INFO.get('port'), db=REDIS_CONN_INFO.get('db'))

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
    https://swgoh.gg/api/guilds/<guild_id>/units/
    :return:
    """
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

    url = "https://swgoh.gg/api/guilds/{}/units/".format(GUILD_ID)
    headers = {'User-Agent': user_agent, }

    request = urllib.request.Request(url, None, headers)  # The assembled request
    response = urllib.request.urlopen(request)
    data = json.loads(response.read().decode(), )  # The data u need

    return data


def get_characters_media():
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

    url = "https://swgoh.gg/api/characters/?format=json"
    headers = {'User-Agent': user_agent, }

    request = urllib.request.Request(url, None, headers)  # The assembled request
    response = urllib.request.urlopen(request)
    data = json.loads(response.read().decode(), )  # The data u need

    return data


def get_ships_media():
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

    url = "https://swgoh.gg/api/ships/?format=json"
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


def get_split_csv(df):
    return df.to_csv(sep=';')


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


def get_who_has_generic(unit, star=0):
    keys = []
    for k in TOON_DATA.keys():
        aliases = TOON_DATA.get(k).get('alias')
        aliases.append(k)
        if difflib.get_close_matches(unit, aliases, 1, 0.9):
            keys.append(k)
    if not keys:
        return []
    data = get_data()
    results = []
    for k in keys:
        results.append({'name': TOON_DATA[k].get('name'), 'result': [d for d in data[k] if d.get('rarity') >= star],
                        'icon': TOON_DATA[k].get('icon')})
    return results


def get_toon_list():
    return list(toons.values())


def get_ship_list():
    return list(ships.values())


def process_image(author, attachment):
    url = attachment['url']
    # img_type in ['tickets', 'platoons', False]
    img_type, result, star = tool.read_and_classify_image(str(author), url, mode='remote')
    if img_type == 'platoons':
        new_dict = {}
        for k, v in result.items():
            new_dict[k] = {'needed': v}
            results = get_who_has_generic(k, star)
            name = results[0].get('name')
            new_dict[k]['players'] = results[0].get('result')
            icon = results[0].get('icon')
        return new_dict, star
    return img_type, None


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
    merged = tickets1.reset_index().merge(tickets2.reset_index(), how='outer', left_on="index", right_on="index") \
        .set_index('index').fillna(0)
    merged.loc[:, 'diff'] = merged[date1].astype(int) - merged[date2].astype(int)
    merged['diff'] = merged['diff'].abs()
    return merged


def plot_guild_gp():
    gp_list = r.lrange('guildgp:values:{}'.format(GUILD_ID), 0, -1)
    date_list = r.lrange('guildgp:dates:{}'.format(GUILD_ID), 0, -1)
    gp_list = [int(i) for i in gp_list]
    date_list = [d.decode('utf-8') for d in date_list]
    resp = dict()
    if len(gp_list) > 1:
        resp['mean'] = [t - s for s, t in zip(gp_list, gp_list[1:])]
        resp['mean'] = sum(resp['mean']) / float(len(resp['mean']))
    resp['df'] = pd.DataFrame(gp_list, index=date_list, columns=['Guild GP'])
    return resp


def get_toon_count_per_rarity(guild_data, star):
    toons = {}
    for toon_name, players in guild_data.items():
        sub_list = [player for player in players if player['rarity'] >= star]
        if not sub_list:
            toons[toon_name] = 0
            continue
        df = pd.DataFrame(sub_list)
        df = df.sort_values('power', ascending=False).drop_duplicates(subset='player', keep='first')
        sub_list = list(df.T.to_dict().values())
        toons[toon_name] = len(sub_list)
    return toons


def get_toons_with_rarity(rarity):
    toon_media = get_characters_media()
    ship_media = get_ships_media()
    data = get_data()
    toon_res = []
    ship_res = []
    for t in toon_media:
        if t['base_id'] in data.keys():
            sub_list = data[t['base_id']]
            c = len([item for item in sub_list if item['rarity'] >= rarity])
        else:
            c = 0
        if c < 8:
            t['need'] = 8 - c
            toon_res.append(t)
    for t in ship_media:
        if t['base_id'] in data.keys():
            sub_list = data[t['base_id']]
            c = len([item for item in sub_list if item['rarity'] >= rarity])
        else:
            c = 0
        if c < 8:
            t['need'] = 8 - c
            ship_res.append(t)
    return toon_res, ship_res


def analyze_platoons(file_path):
    platoons = analyze_platoon_json(get_platoons_from_rpc(file_path))
    guild_data = get_data()
    star = 2
    computed = {}
    for phase_name, conflicts in platoons.items():
        toon_count = get_toon_count_per_rarity(guild_data, star)
        computed[phase_name] = {}
        for platoon_num, platoon_list in conflicts.items():
            for plat, required in platoon_list.items():
                for toon in required:
                    if toon_count.get(toon):
                        toon_count[toon] -= 1
                    else:
                        toon_count[toon] = -1
        computed[phase_name] = {x: y for x, y in toon_count.items() if y < 0}
        star += 1
    return computed


def convert_to_media_name(platoon_list, toons_media, ships_media):
    for i in range(len(platoon_list)):
        for j in range(len(platoon_list[i])):
            data = [t for t in toons_media if t.get('base_id') and t['base_id'] == platoon_list[i][j]]
            if not data:
                data = [t for t in ships_media if t.get('base_id') and t['base_id'] == platoon_list[i][j]]
            platoon_list[i][j] = data[0]['name']
    return platoon_list


def create_template_for_spreadsheet(file_path):
    platoons = analyze_platoon_json(get_platoons_from_rpc(file_path))
    toons_media = get_characters_media()
    ships_media = get_ships_media()
    df = pd.DataFrame(
        columns=['Phase', 'refresh', '#1', '1', 'recommended 1', 'void 1', '#2', '2', 'recommended 2', 'void 2', '#3',
                 '3', 'recommended 3', 'void 1', '#4', '4',
                 'recommended 4', 'void 4', '#5', '5', 'recommended 5', 'void 5', '#6', '6', 'recommended 6', 'void 6'])
    idx = 0
    for phase, conflicts in platoons.items():
        phase_num = phase[-1]
        for conflict, platoons in conflicts.items():
            first = True
            platoon_list = []
            for platoon_name, platoon in platoons.items():
                platoon_list.append(platoon)
            platoon_list = convert_to_media_name(platoon_list, toons_media, ships_media)
            for j in range(len(platoon_list[0])):
                row = []
                if first:
                    row += [phase_num]
                    first = False
                else:
                    row += ['']
                row += ['']
                for i in range(6):
                    row += [j + 1, platoon_list[i][j], '', '']
                df.loc[idx] = row
                idx += 1
            df.loc[idx] = [''] * len(row)
            idx += 1
            df.loc[idx] = [''] * len(row)
            idx += 1
            df.loc[idx] = ['', '', '#', 'Platoon 1', 'Recommended', '', '#', 'Platoon 2', 'Recommended', '', '#',
                           'Platoon 3', 'Recommended', '', '#', 'Platoon 4', 'Recommended', '', '#', 'Platoon 5',
                           'Recommended', '', '#', 'Platoon 6', 'Recommended', '']
            idx += 1
    df.to_clipboard()
    return df


def analyze_roster(url):
    try:
        page = requests.get(url)
    except MissingSchema:
        return None
    player_id = url.split('/')[-2]
    tree = html.fromstring(page.content)
    aside = tree.xpath('//div[contains(@class, "content-container-aside")]')
    pguild = aside[0].xpath('.//p[.//text()="Guild "]')
    guild_url = pguild[0].xpath('.//a/@href')[0]
    guild_id = guild_url.split('/')[2]
    guild_url = 'https://swgoh.gg/api/guilds/{}/units/'.format(guild_id)
    roster_data = requests.get(guild_url)
    roster_data = roster_data.json()

    char_media = get_characters_media()
    teams = {}
    teams['Phase 1 - JTR'] = ['REYJEDITRAINING', 'BB8', 'R2D2_LEGENDARY', 'REY', 'RESISTANCETROOPER']
    teams['Phase 3 - Chex Mix'] = ['COMMANDERLUKESKYWALKER', 'HANSOLO', 'DEATHTROOPER', 'CHIRRUTIMWE', 'PAO']
    teams['Phase 4 - NS'] = ['ASAJVENTRESS', 'DAKA', 'NIGHTSISTERACOLYTE', 'TALIA', 'NIGHTSISTERINITIATE']

    global_data = {}
    for k, v in teams.items():
        player_data = {}
        icon = ''
        for unit in v:
            temp = roster_data.get(unit)
            toon_media = [c for c in char_media if c['base_id'] == unit][0]
            if not icon:
                icon = toon_media['image']
            player_toon_data = [t for t in temp if player_id in t['url']]
            if player_toon_data:
                player_data[unit] = [t for t in temp if player_id in t['url']][0]
            else:
                player_data[unit] = {}
            player_data[unit]['name'] = toon_media['name']
            if player_toon_data:
                player_data[unit]['completion'] = player_data[unit]['power'] / toon_media['power'] * 100.0
            else:
                player_data[unit]['completion'] = 0.0
        global_data[k] = player_data
        global_data[k]['icon'] = icon
    return global_data


def add_rotation(channel_id, players):
    if os.path.exists('rotations/{}'.format(channel_id)):
        with open(r'rotations/{}'.format(channel_id)) as f:
            rot = json.load(f)
            max_keys = max([int(k) for k in rot.keys()])
            rot[max_keys + 1] = players
    else:
        with open('rotations/master_channel_list.txt') as f:
            file = f.read()
        if file:
            new_line = '\n{}'.format(channel_id)
        else:
            new_line = channel_id
        with open("rotations/master_channel_list.txt", "a") as f:
            f.write(new_line)
        rot = dict()
        rot[1] = players
    with open(r'rotations/{}'.format(channel_id), 'w') as outfile:
        json.dump(rot, outfile)

    example = '{:%m/%d/%y}: '.format(datetime.datetime.today())
    tomorrow = '{:%m/%d/%y}: '.format(datetime.datetime.today() + datetime.timedelta(days=1))
    i = 1
    j = 1
    for k, values in rot.items():
        tom_vals = values[1:] + [values[0]]
        for v in values:
            example += '{}) {}, '.format(i, v)
            i += 1
        for v in tom_vals:
            tomorrow += '{}) {}, '.format(j, v)
            j += 1
    return example[:-2], tomorrow[:-2]


def del_rotation(channel_id):
    try:
        with open('rotations/master_channel_list.txt') as f:
            file = f.read()
        file = file.replace(channel_id, '').replace('\n\n', '\n')
        if file[-2:] == '\n':
            file = file[:-2]
        with open('rotations/master_channel_list.txt', "w") as f:
            f.write(file)
        os.remove(r'rotations/{}'.format(channel_id))
    except:
        return False
    return True


def get_rotation(channel_id):
    today = datetime.datetime.today().strftime('%m/%d/%y')
    with open(r'rotations/{}'.format(channel_id)) as f:
        rot = json.load(f)
    i = 1
    text = "{}: ".format(today)
    new_json = {}
    for k, vals in rot.items():
        for v in vals:
            text += "{}) {}, ".format(i, v)
            i += 1
    text = text[:-2]
    return text


# if __name__ == '__main__':
#     writer = ExcelWriter(os.path.join(os.getcwd(), 'farm_guide.xls'))
#     toons_df = create_toons_df(formula=True)
#     ships_df = create_ships_df(formula=True)
#     toons_df.to_excel(writer, 'toons')
#     ships_df.to_excel(writer, 'ships')
#     writer.save()
