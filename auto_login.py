import mechanicalsoup
browser = mechanicalsoup.StatefulBrowser()
browser.open("https://swgoh.gg/accounts/login/")
browser.select_form('form')
browser['username'] = 'SierraTangoSix'
browser['password'] = 'Darkmoon93'
browser.submit_selected()
browser.open('https://swgoh.gg/u/settings/')
browser.select_form('form')
browser.submit_selected()
