import requests


def get_platoons_from_rpc(file_path):
    data = open(file_path, 'rb').read()
    res = requests.post('https://ck-47.herokuapp.com/platoons', data=data,
                        headers={'Content-Type': 'application/octet-stream'})
    return res.json()


def analyze_platoon_json(res):
    # we should have 2 keys, platoons and side. side is useless.
    res = res['platoons']
    # then we have a list of territories.
    platoons = {}
    for ter in res:
        # name is something like phase01_conflict01_recon01
        name = ter['name']
        name = name.split('_')
        name = [n for n in name if n not in ['hoth', 'empire']]
        if not platoons.get(name[0]):
            platoons[name[0]] = {}
        platoons[name[0]][name[1]] = {}
        # for each territory, we have a list of platoons.
        for p in ter['platoons']:
            plat_name = p['name']
            members = []
            for s in p['squads']:
                members += s['members']
            platoons[name[0]][name[1]][plat_name] = members
    return platoons

# analyze_platoon_json(get_platoons_from_rpc(r'C:\Users\Daniel\Downloads\platoons\rpc'))
