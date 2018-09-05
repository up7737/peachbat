import os
import datetime
from collections import defaultdict




VERBOSE_OUTPUT_TO_TERMINAL = True


class MetaScraper(type):
    def __new__(self, classname, class_super, classdict):
        classname = os.path.basename(__file__).replace('.py', '')
        return type.__new__(self, classname, class_super, classdict)


class scr_005(metaclass=MetaScraper):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'referer': 'https://www.baseball-reference.com/data/',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    data = {}
    
    def __init__(self, engine):
        self.current_year = datetime.datetime.now().year
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

    def row_to_cols(self, text, _chr=','):
        return text.split(_chr)

    def lists_to_dict(self, l1, l2):
        return dict(zip(l1, l2))

    def text_to_dict_rows(self, text):
        headers, *rows_text = [self.row_to_cols(row) for row in text.split('\n') if row.strip()]
        return [self.lists_to_dict(headers, row) for row in rows_text]

    def get_row_keys_match(self, row, match):
        return [key for key in row if match.lower() in key.lower()]

    def DATA_key(self, *args):
        key = '_'.join(args).upper()
        return '[{}]'.format(key)

    def run(self):
        roles_files = {
            'batters': 'war_daily_bat_year.txt',
            'pitchers': 'war_daily_pitch_year.txt'

        }
        
        DATA = defaultdict(list)
        DATA['source'] = 'baseball-reference'
        DATA['desc'] = 'projections'
        DATA['headers'] = ['[NAME]', '[TEAM]', '[YEAR]']

        projections_collapsed = defaultdict(dict)
        for role, file in roles_files.items():
            p('{:>10}'.format(role))
            url = 'https://www.baseball-reference.com/data/{}'.format(file)
            self.get(url)

            rows = self.text_to_dict_rows(self.response.text)
            keys_common = ['name_common', 'year_ID', 'team_ID'] 
            keys_war = self.get_row_keys_match(rows[0], 'WAR')
            headers_role_war = [self.DATA_key(role, key) for key in keys_war]
            
            DATA['headers'].extend(headers_role_war)

            for row in rows:
                if row['year_ID'] == str(self.current_year - 1): continue
                
                tuple_key = tuple([row[k] for k in keys_common])
                
                projections_collapsed[tuple_key].update(
                    {'[NAME]': row['name_common'], '[TEAM]': row['team_ID']}
                )
                projections_collapsed[tuple_key].update(
                    self.lists_to_dict(headers_role_war, [row[key] for key in keys_war])
                )

        DATA['rows'] = list(projections_collapsed.values())
        
        return DATA
                    

def p(text):
    if VERBOSE_OUTPUT_TO_TERMINAL:
        print(text)
                 



if __name__ == '__main__':
    print('SCRAPERS FOLDER:', scr_005.__name__)
