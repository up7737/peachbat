import os
from collections import defaultdict

import lxml.html




class MetaScraper(type):
    def __new__(self, classname, class_super, classdict):
        classname = os.path.basename(__file__).replace('.py', '')
        return type.__new__(self, classname, class_super, classdict)


class scr_002(metaclass=MetaScraper):
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
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

    def text_content_and_normalize(self, obj, chrs=['\n'], replace=''):
        text = obj.text_content()
        for c in chrs:
            text = text.replace(c, replace)
        return text

    def run(self):
        DATA = defaultdict(list)
        DATA['source'] = 'baseballprospectus'
        DATA['desc'] = 'standings'
        DATA['url'] = 'https://legacy.baseballprospectus.com/fantasy/dc/'
        DATA['headers'].extend(['[TEAM]', '[RS]'])
        
        self.get(DATA['url'])

        tree = lxml.html.fromstring(self.response.text)
        team_rows_objs = [[i, list(i.itersiblings())[3]] for i in tree.cssselect('td[width="200"]')]
        team_rows_text = [[self.text_content_and_normalize(team), self.text_content_and_normalize(rs)] for team, rs in team_rows_objs]

        [DATA['rows'].append(dict(zip(DATA['headers'], row))) for row in team_rows_text]

        return DATA




if __name__ == '__main__':
    print('SCRAPERS FOLDER:', scr_002.__name__)
