from collections import OrderedDict
import requests
import json
import urllib.request
import re
import html

HSTR_TEAMS = {
    'PHASE1': [
        {'NAME': 'JTR 1', 'TOONS': ['REYJEDITRAINING', 'BB8', 'RESISTANCETROOPER', 'REY', 'VISASMARR'],
         'GOAL': 4, 'MIN_GP': 80000, 'ZETAS': ['Inspirational Presence']},
        {'NAME': 'JTR 3', 'TOONS': ['REYJEDITRAINING', 'BB8', 'R2D2_LEGENDARY', 'REY', 'VISASMARR'], 'GOAL': 4,
         'MIN_GP': 80000, 'ZETAS': ['Inspirational Presence']},
        {'NAME': 'JTR 2', 'TOONS': ['REYJEDITRAINING', 'BB8', 'R2D2_LEGENDARY', 'REY', 'RESISTANCETROOPER'],
         'GOAL': 4, 'MIN_GP': 80000, 'ZETAS': ['Inspirational Presence']},
        {'NAME': 'JTR 4', 'TOONS': ['REYJEDITRAINING', 'BB8', 'R2D2_LEGENDARY', 'REY', 'BARRISSOFFEE'], 'GOAL': 4,
         'MIN_GP': 80000, 'ZETAS': ['Inspirational Presence']},
        {'NAME': 'JTR 5', 'TOONS': ['REYJEDITRAINING', 'BB8', 'R2D2_LEGENDARY', 'REY', 'HERMITYODA'], 'GOAL': 4,
         'MIN_GP': 80000, 'ZETAS': ['Inspirational Presence']}
    ],
    'PHASE3': [
        {'NAME': 'Chex Mix with Pao and Chirrut',
         'TOONS': ['COMMANDERLUKESKYWALKER', 'HANSOLO', 'DEATHTROOPER', 'PAO', 'CHIRRUTIMWE'],
         'GOAL': 4, 'MIN_GP': 75000, 'ZETAS': ['Shoots First']},
        {'NAME': 'Chex Mix with JKA and Chirrut',
         'TOONS': ['COMMANDERLUKESKYWALKER', 'HANSOLO', 'DEATHTROOPER', 'ANAKINKNIGHT', 'CHIRRUTIMWE'],
         'GOAL': 4, 'MIN_GP': 75000, 'ZETAS': ['Shoots First']},
        {'NAME': 'Chex Mix with Pao and Rex',
         'TOONS': ['COMMANDERLUKESKYWALKER', 'HANSOLO', 'DEATHTROOPER', 'PAO', 'CT7567'],
         'GOAL': 4, 'MIN_GP': 75000, 'ZETAS': ['Shoots First']},
        {'NAME': 'Chex Mix with JKA and Rex',
         'TOONS': ['COMMANDERLUKESKYWALKER', 'HANSOLO', 'DEATHTROOPER', 'ANAKINKNIGHT', 'CT7567'],
         'GOAL': 4, 'MIN_GP': 75000, 'ZETAS': ['Shoots First']}
    ],
    'PHASE2': [
        {'NAME': 'Big Mix + HODA',
         'TOONS': ['ADMIRALACKBAR', 'HERMITYODA', 'GENERALKENOBI', 'GRANDADMIRALTHRAWN', 'SABINEWRENS3'],
         'GOAL': 3, 'MIN_GP': 80000},
        {'NAME': 'Big Mix + Barriss',
         'TOONS': ['ADMIRALACKBAR', 'BARRISSOFFEE', 'GENERALKENOBI', 'GRANDADMIRALTHRAWN', 'SABINEWRENS3'],
         'GOAL': 3, 'MIN_GP': 80000},
        {'NAME': 'Pathfinder\'s Training with Leia',
         'TOONS': ['PRINCESSLEIA', 'HERMITYODA', 'SCARIFREBEL', 'GRANDADMIRALTHRAWN', 'SABINEWRENS3'],
         'GOAL': 3, 'MIN_GP': 80000, 'ZETAS': ['Do or Do Not']},
        {'NAME': 'Pathfinder\'s Training',
         'TOONS': ['COMMANDERLUKESKYWALKER', 'HERMITYODA', 'SCARIFREBEL', 'EZRABRIDGERS3', 'SABINEWRENS3'],
         'GOAL': 3, 'MIN_GP': 80000, 'ZETAS': ['Do or Do Not']},
        {'NAME': 'Kenobi Swamp',
         'TOONS': ['GENERALKENOBI', 'HERMITYODA', 'WAMPA', 'GRANDADMIRALTHRAWN', 'SABINEWRENS3'],
         'GOAL': 5, 'MIN_GP': 80000, 'zetas': ['Strength Flows From the Force']},
        {'NAME': 'Boba lead Wampa',
         'TOONS': ['BOBAFETT', 'GRANDADMIRALTHRAWN', 'SABINEWRENS3', 'R2D2_LEGENDARY', 'WAMPA'],
         'GOAL': 3, 'MIN_GP': 80000},
        {'NAME': 'GK lead Wampa',
         'TOONS': ['GENERALKENOBI', 'GRANDADMIRALTHRAWN', 'SABINEWRENS3', 'R2D2_LEGENDARY', 'WAMPA'],
         'GOAL': 2, 'MIN_GP': 80000},
        {'NAME': 'Lumi lead Wampa',
         'TOONS': ['LUMINARAUNDULI', 'GRANDADMIRALTHRAWN', 'SABINEWRENS3', 'R2D2_LEGENDARY', 'WAMPA'],
         'GOAL': 2, 'MIN_GP': 80000},
        {'NAME': 'JTR 1', 'TOONS': ['REYJEDITRAINING', 'BB8', 'R2D2_LEGENDARY', 'REY', 'RESISTANCETROOPER'],
         'GOAL': 3.5, 'MIN_GP': 80000, 'ZETAS': ['Inspirational Presence']},
        {'NAME': 'JTR 2', 'TOONS': ['REYJEDITRAINING', 'BB8', 'R2D2_LEGENDARY', 'REY', 'VISASMARR'], 'GOAL': 3.5,
         'MIN_GP': 80000, 'ZETAS': ['Inspirational Presence']},
        {'NAME': 'JTR 3', 'TOONS': ['REYJEDITRAINING', 'BB8', 'R2D2_LEGENDARY', 'REY', 'BARRISSOFFEE'], 'GOAL': 3.5,
         'MIN_GP': 80000, 'ZETAS': ['Inspirational Presence']},
        {'NAME': 'JTR 4', 'TOONS': ['REYJEDITRAINING', 'BB8', 'R2D2_LEGENDARY', 'REY', 'HERMITYODA'], 'GOAL': 3.5,
         'MIN_GP': 80000, 'ZETAS': ['Inspirational Presence']},
        {'NAME': 'Phoenix', 'TOONS': ['HERASYNDULLAS3', 'SABINEWRENS3', 'ZEBS3', 'EZRABRIDGERS3', 'KANANJARRUSS3'],
         'GOAL': 2, 'MIN_GP': 80000},
        {'NAME': 'Phoenix zetad',
         'TOONS': ['HERASYNDULLAS3', 'SABINEWRENS3', 'ZEBS3', 'EZRABRIDGERS3', 'KANANJARRUSS3'],
         'GOAL': 4, 'MIN_GP': 80000,
         'ZETAS': ['Demolish', 'Total Defense', 'Flourish', 'Staggering Sweep', 'Play to Strengths']},
        {'NAME': 'Ewoks', 'TOONS': ['CHIEFCHIRPA', 'WICKET', 'EWOKELDER', 'EWOKSCOUT', 'LOGRAY'], 'GOAL': 0.5,
         'MIN_GP': 80000, 'ZETAS': ['Simple Tactics']},
        {'NAME': 'Sith + Vader', 'TOONS': ['MAUL', 'DARTHNIHILUS', 'SITHTROOPER', 'SITHASSASSIN', 'VADER'], 'GOAL': 0.5,
         'MIN_GP': 80000, 'ZETAS': ['Dancing Shadows']},
        {'NAME': 'Sith + Marauder', 'TOONS': ['MAUL', 'DARTHNIHILUS', 'SITHTROOPER', 'SITHASSASSIN', 'SITHMARAUDER'],
         'GOAL': 0.5,
         'MIN_GP': 80000, 'ZETAS': ['Dancing Shadows']},
        {'NAME': 'Sith + Marauder', 'TOONS': ['MAUL', 'DARTHNIHILUS', 'SITHTROOPER', 'SITHASSASSIN', 'DARTHSION'],
         'GOAL': 0.5, 'MIN_GP': 80000, 'ZETAS': ['Dancing Shadows']},
        {'NAME': 'Sith + Marauder',
         'TOONS': ['MAUL', 'DARTHNIHILUS', 'SITHTROOPER', 'SITHASSASSIN', 'EMPERORPALPATINE'], 'GOAL': 0.5,
         'MIN_GP': 80000, 'ZETAS': ['Dancing Shadows']},
        {'NAME': 'Sith + Marauder', 'TOONS': ['MAUL', 'DARTHNIHILUS', 'SITHTROOPER', 'SITHASSASSIN', 'COUNTDOOKU'],
         'GOAL': 0.5, 'MIN_GP': 80000, 'ZETAS': ['Dancing Shadows']},
        {'NAME': 'Sith + Marauder', 'TOONS': ['MAUL', 'DARTHNIHILUS', 'SITHTROOPER', 'SITHASSASSIN', 'SAVAGEOPRESS'],
         'GOAL': 0.5, 'MIN_GP': 80000, 'ZETAS': ['Dancing Shadows']},
        {'NAME': 'Sith + Marauder', 'TOONS': ['MAUL', 'DARTHNIHILUS', 'SITHTROOPER', 'SITHASSASSIN', 'DARTHSIDIOUS'],
         'GOAL': 0.5, 'MIN_GP': 80000, 'ZETAS': ['Dancing Shadows']},
        {'NAME': 'Thrawnpers without DT',
         'TOONS': ['GRANDADMIRALTHRAWN', 'VEERS', 'COLONELSTARCK', 'SHORETROOPER', 'SNOWTROOPER'],
         'GOAL': 0.5, 'MIN_GP': 80000, 'ZETAS': ['Aggressive Tactician']},
    ],
    'PHASE4_WITH_DN': [
        {'NAME': 'Nightsisters with MT and Zombie 1',
         'TOONS': ['ASAJVENTRESS', 'DAKA', 'TALIA', 'NIGHTSISTERZOMBIE', 'MOTHERTALZIN'], 'GOAL': 15,
         'MIN_GP': 80000, 'ZETAS': ['Nightsister Swiftness']},
        {'NAME': 'Nightsisters with MT and Zombie 2',
         'TOONS': ['ASAJVENTRESS', 'DAKA', 'NIGHTSISTERACOLYTE', 'NIGHTSISTERZOMBIE', 'MOTHERTALZIN'], 'GOAL': 15,
         'MIN_GP': 80000, 'ZETAS': ['Nightsister Swiftness']},
        {'NAME': 'Nightsisters with MT',
         'TOONS': ['ASAJVENTRESS', 'DAKA', 'TALIA', 'NIGHTSISTERACOLYTE', 'MOTHERTALZIN'], 'GOAL': 10,
         'MIN_GP': 80000, 'ZETAS': ['Nightsister Swiftness']},
        {'NAME': 'Nightsisters with Zombie',
         'TOONS': ['ASAJVENTRESS', 'DAKA', 'TALIA', 'NIGHTSISTERACOLYTE', 'NIGHTSISTERZOMBIE'], 'GOAL': 10,
         'MIN_GP': 80000, 'ZETAS': ['Nightsister Swiftness']},
        {'NAME': 'Nightsisters',
         'TOONS': ['ASAJVENTRESS', 'DAKA', 'TALIA', 'NIGHTSISTERACOLYTE', 'NIGHTSISTERINITIATE'], 'GOAL': 5,
         'MIN_GP': 80000, 'ZETAS': ['Nightsister Swiftness']},
    ]
}


def get_characters_media():
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

    url = "https://swgoh.gg/api/characters/?format=json"
    headers = {'User-Agent': user_agent, }

    request = urllib.request.Request(url, None, headers)  # The assembled request
    response = urllib.request.urlopen(request)
    data = json.loads(response.read().decode(), )  # The data u need

    return data


def create_guild_dict(data):
    """
    Returns a dict of type:
    {'player_name': {
            {{keys: [name,base_id,pk,url,image,power,description,combat_type]}, ...}
        }
    }
    :param data:
    :return:
    """
    d = {}
    for toon_id, rosters in data.items():
        for roster in rosters:
            if roster['rarity'] < 7:
                continue
            if roster['player'] not in d.keys():
                d[roster['player']] = {}
            d[roster['player']][toon_id] = roster
    return d


def get_guild_zetas(url):
    zetas = {}
    title_zeta_tag = 'title="'
    zeta_url = "{}zetas/".format(url)
    r = requests.get(zeta_url)
    content = r.text.split('\n')
    player_name = ""
    for c in content:
        if 'data-sort-value' in c:
            player_name = html.unescape(c.split('"')[1])
            zetas[player_name] = []
        if 'guild-member-zeta-ability' in c:
            zetas[player_name].append(c[c.index(title_zeta_tag) + len(title_zeta_tag):-2])
    return zetas


def analyze_guild_hstr_readiness(url):
    """
    :param url: type: https://swgoh.gg/g/861/force-is-strong-between-us/
    :return:
    """
    p = re.compile('https:\/\/swgoh\.gg\/g\/\d*\/.*')
    if not p.match(url):
        return "Invalid url"

    guild_id = url.split('/')[4]

    guild_data_url = "https://swgoh.gg/api/guilds/{}/units/".format(guild_id)
    roster_data = requests.get(guild_data_url)
    roster_data = roster_data.json()

    guild_dict = create_guild_dict(roster_data)
    guild_zetas = get_guild_zetas(url)

    readiness = {}
    for phase, teams in HSTR_TEAMS.items():
        total = 100
        if phase == 'PHASE4_WITH_DN':
            total = 95
        readiness[phase] = {'remaining': total, 'teams': []}
        phase_ready = False
        for player_name, player_roster in guild_dict.items():
            if phase_ready:
                break
            teams_left = True
            while teams_left:
                temp = {}
                for team in teams:
                    power = 0
                    IDS = []
                    player_zetas = guild_zetas.get(player_name)
                    team_zetas = team.get('ZETAS')

                    if team_zetas:
                        if not player_zetas:
                            continue
                        if set(team_zetas) - set(player_zetas):
                            continue
                    for toon in team['TOONS']:
                        if not player_roster.get(toon):
                            break
                        player_toon = player_roster[toon]
                        power += player_toon['power']
                        IDS.append(toon)
                    if power > team['MIN_GP']:
                        temp[team['NAME']] = {'power': power, 'IDS': IDS, 'name': team['NAME'], 'goal': team['GOAL']}
                max_gp = 0
                goal = 0
                winner = None
                for team_id, data in temp.items():
                    if data['goal'] > goal:
                        winner = data
                        max_gp = data['power']
                        goal = data['goal']
                    elif data['goal'] == goal and data['power'] > max_gp:
                        winner = data
                        max_gp = data['power']
                if winner:
                    readiness[phase]['remaining'] -= winner['goal']
                    readiness[phase]['teams'].append(
                        {'player_name': player_name, 'team_name': winner['name'], 'goal': winner['goal']})
                    for id in winner['IDS']:
                        del guild_dict[player_name][id]
                    if readiness[phase]['remaining'] <= 0:
                        readiness[phase]['remaining'] = 0
                        phase_ready = True
                        break
                else:
                    teams_left = False

    msg = []
    for k in sorted(readiness.keys()):
        msg.append((k, "{}% ready.".format(100 - readiness[k]['remaining'])))

    leftover_gp = 0
    nb_toons = 0
    for player_name, toons in guild_dict.items():
        for toon_name, toon_data in toons.items():
            if toon_data['power'] > 10000:
                leftover_gp += toon_data['power']
                nb_toons += 1
    msg.append(("Leftover GP for P4 (toons over 10k GP only):", "{:,}".format(leftover_gp)))
    msg.append(("Number of toons left for P4 (toons over 10k GP only):", "{:,}".format(nb_toons)))
    msg.append((
        "Average:",
        "{:,.2f} GP left for P4 per player ({:,.2f} gp per team, toons over 10k GP only).".format(leftover_gp / 50,
                                                                                                  leftover_gp /
                                                                                                  nb_toons * 5)))
    msg.append(("Average:",
                "{:,.2f} toons left for P4 per player ({:,.2f} teams).".format(nb_toons / 50, (nb_toons / 50) / 5)))

    char_media = get_characters_media()

    for phase, phase_data in readiness.items():
        for team in phase_data['teams']:
            for t in HSTR_TEAMS[phase]:
                if t['NAME'] == team['team_name']:
                    temp = t['TOONS']
                    team_str = []
                    for te in temp:
                        team_str.append([c['name'] for c in char_media if c['base_id'] == te][0])
                    team_str[0] = "{} Lead".format(team_str[0])
                    team_str = ", ".join(team_str)
                    team['comp'] = team_str
                    break
    return msg, create_breakdown(readiness)


def create_breakdown(readiness):
    breakdown = {}
    readiness = OrderedDict(sorted(readiness.items()))
    for k, v in readiness.items():
        breakdown[k] = {}
        for t in v['teams']:
            if not breakdown[k].get(t['team_name']):
                breakdown[k][t['team_name']] = {'goal': t['goal'], 'comp': t['comp'], 'players': []}
            breakdown[k][t['team_name']]['players'].append(t['player_name'])
    return breakdown


def get_hstr_teams():
    char_media = get_characters_media()
    result = {}
    for phase, teams in HSTR_TEAMS.items():
        result[phase] = {}
        for team in teams:
            s = ''
            for toon in team['TOONS']:
                s += [c['name'] for c in char_media if c['base_id'] == toon][0] + ', '
            s = s[:-2]
            if team.get('ZETAS'):
                s += '. Mandatory zetas: '
                for z in team['ZETAS']:
                    s += z + ', '
                s = s[:-2]
            s += '. Goal: {}%.'.format(team['GOAL'])
            result[phase][team['NAME']] = s
    return result
