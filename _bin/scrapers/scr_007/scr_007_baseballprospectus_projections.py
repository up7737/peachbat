import os
import datetime
import csv
from collections import defaultdict

import lxml.html




VERBOSE_OUTPUT_TO_TERMINAL = True


class MetaScraper(type):
    def __new__(self, classname, class_super, classdict):
        classname = os.path.basename(__file__).replace('.py', '')
        return type.__new__(self, classname, class_super, classdict)


class scr_007(metaclass=MetaScraper):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'legacy.baseballprospectus.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    data = {}
    
    def __init__(self, engine):
        self.engine = engine
        self.response = None

    def get(self, url, *, headers=None):
        if headers is None:
            headers = self.headers
        self.response = self.engine.get(url, headers=headers)

    def post(self, url, *, headers=None, data=None):
        if headers is None:
            headers = self.headers
        if data is None:
            data = self.data
        self.response = self.engine.post(url, headers=headers, data=data)

    def get_td_text_from_tr(self, tr_object):
        return [el.text_content() for el in tr_object.cssselect('td')]

    def run(self):
        roles = {
            'batters': {'url_id': 1918875, 'WAR': 'BWARP'},
            'pitchers': {'url_id': 2508773, 'WAR': 'PWARP'}
        }

        DATA = defaultdict(list)
        DATA['source'] = 'baseballprospectus'
        DATA['desc'] = 'projections'
        DATA['headers'].extend(['[NAME]', '[BATTERS_BWARP]', '[PITCHERS_PWARP]'])

        projections_collapsed = defaultdict(dict)
        for role, role_cred in roles.items():
            url = 'https://legacy.baseballprospectus.com/sortable/index.php?cid={}'.format(role_cred['url_id'])
            DATA['url'].append(url)

            p('{:>10}'.format(role))
            self.get(url)

            tree = lxml.html.fromstring(self.response.text)
            table_headers, *table_rows = tree.cssselect('#TTdata tr')

            rows = [
                dict(zip(self.get_td_text_from_tr(table_headers), self.get_td_text_from_tr(row))) for row in table_rows
            ]

            for row in rows:
                war_col_header = '[{}]'.format('_'.join([role, role_cred['WAR']]).upper())
                projections_collapsed[row['NAME']].update({'[NAME]': row['NAME'], war_col_header: row[role_cred['WAR']]})

        DATA['rows'] = list(projections_collapsed.values())
        return DATA
                                            

def p(text):
    if VERBOSE_OUTPUT_TO_TERMINAL:
        print(text)
                 



if __name__ == '__main__':
    print('SCRAPERS FOLDER:', scr_007.__name__)
