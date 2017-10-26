import pandas as pd
from pandas import ExcelWriter
import os
import urllib.request, json
from string import ascii_uppercase
import xlwt

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

# if __name__ == '__main__':
#     writer = ExcelWriter(os.path.join(os.getcwd(), 'farm_guide.xls'))
#     toons_df = create_toons_df(formula=True)
#     ships_df = create_ships_df(formula=True)
#     toons_df.to_excel(writer, 'toons')
#     ships_df.to_excel(writer, 'ships')
#     writer.save()
