import mechanicalsoup
import redis
import datetime
from settings import REDIS_CONN_INFO

r = redis.StrictRedis(host=REDIS_CONN_INFO.get('host'), port=REDIS_CONN_INFO.get('port'), db=REDIS_CONN_INFO.get('db'))
GUILD_ID = 27003


if __name__ == "__main__":
    today = datetime.datetime.now().strftime('%Y%m%d')
    browser = mechanicalsoup.StatefulBrowser()
    guild_page = browser.get("https://swgoh.gg/g/{}/hogtown-knights/".format(GUILD_ID))
    gp_div = guild_page.soup.find("div", {'class': 'stat-item-value'})
    guild_gp = int(gp_div.contents[0].replace(',', ''))
    r.sadd("guildgp:values:{}".format(GUILD_ID), guild_gp)
    r.sadd("guildgp:dates:{}".format(GUILD_ID), today)
    members_table = guild_page.soup.find("table", {'class': 'table'})
    members_table_tds = members_table.find_all('td')
    # dic = {}
    temp_name = ''
    for td in members_table_tds:
        if temp_name:
            r.sadd("membergp:{}:{}".format(GUILD_ID, temp_name), td.contents[0])
            # dic[temp_name] = td.contents[0]
            # temp_name = ''
        if 'data-sort-value' in str(td):
            temp_name = td.find('strong').contents[0]
        continue
    browser.close()
    # print(dic)
