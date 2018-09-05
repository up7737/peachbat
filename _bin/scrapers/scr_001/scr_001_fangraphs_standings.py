import os
from collections import defaultdict

import lxml.html




class MetaScraper(type):
    def __new__(self, classname, class_super, classdict):
        classname = os.path.basename(__file__).replace('.py', '')
        return type.__new__(self, classname, class_super, classdict)


class scr_001(metaclass=MetaScraper):
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'fgadp=1',
        'Host': 'www.fangraphs.com',
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

    def get_text_from_tr(self, tr_obj, child='th'):
        return [i.text_content().strip() for i in tr_obj.cssselect(child)]
        

    def run(self):
        DATA = defaultdict(list)
        DATA['source'] = 'fangraphs'
        DATA['desc'] = 'standings'
        DATA['url'] = 'https://www.fangraphs.com/depthcharts.aspx?position=Standings'
        DATA['headers'].extend(['[TEAM]', '[RS(G * RA/G)]'])
        
        self.get(DATA['url'])

        tree = lxml.html.fromstring(self.response.text)
        main_table, *_ = tree.cssselect('table.tablesoreder,.depth_chart')
        headers_row = self.get_text_from_tr(main_table.cssselect('tr')[1], 'th')
        data_rows = [self.get_text_from_tr(row, 'td') for row in main_table.cssselect('tr')[2:]]

        def rs_value_from_str(games_left, ra_g):
            return round(int(games_left) * float(ra_g), 2)
        
        team_rs_rows = [[i[0], rs_value_from_str(i[8], i[14])] for i in data_rows]

        [DATA['rows'].append(dict(zip(DATA['headers'], row))) for row in team_rs_rows]

        return DATA




if __name__ == '__main__':
    print('SCRAPERS FOLDER:', scr_001.__name__)
