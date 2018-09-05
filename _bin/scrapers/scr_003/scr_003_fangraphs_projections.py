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


class scr_003(metaclass=MetaScraper):
    headers = {}
    data = {}
    
    def __init__(self, engine):
        self.engine = engine
        self.response = None
        self.current_year = datetime.datetime.now().year
        self.relative_path = os.path.dirname(__file__)
        self.ph = self.HDparser('_ph.txt')
        self.pd = self.HDparser('_pd.txt')

    def get(self, url, *, headers=None):
        if headers is None:
            headers = self.headers
        self.response = self.engine.get(url, headers=headers)

    def post(self, url, *, headers=None, data=None):
        if headers is None:
            headers = self.ph
        if data is None:
            data = self.pd
        self.response = self.engine.post(url, headers=headers, data=data)

    def HDparser(self, filename):
        rel_path_filename = os.path.join(self.relative_path, filename)
        with open(rel_path_filename) as file:
            data_dict = {}
            for line in file:
                key, *values = line.split(':')
                data_dict[key] = ':'.join(values).strip()
            return data_dict
        
    def decode_content(self, encoding='utf-8-sig'):
        return self.response.content.decode(encoding)
        
    def make_header(self, role, projection):
        header = '[{}_{}]'.format(role, projection)
        header = header.replace(' ', '_')
        return header.upper()

    def get_rows_dicts_list_from_response(self, decoded_content):
        headers, *data_rows = [self.data_row_to_column(row) for row in decoded_content.split('\r\n') if row.strip()]
        return [dict(zip(headers, row)) for row in data_rows]

    def data_row_to_column(self, row_text):
        return row_text.replace('"', '').split(',')

    def name_team_to_key(self, name, team, chrs_clear=['.', ' ']):
        key = ''.join([name, team])
        for c in chrs_clear:
            key = key.replace(c, '')
            
        return key

    def run(self):
        projections = {
            'ZiPS': 'zips',
            'Fans': 'fan',
            'Steamer': 'steamer',
            'Steamer600': 'steamer600',
            'Depth Charts': 'fangraphsdc',
            'ZiPS (RoS)': 'rzips',
            'ZiPS (Update)': 'uzips',
            'Steamer (RoS)': 'steamerr',
            'Steamer (Update)': 'steameru',
            'Steamer600 (Update)': 'steamer600u',
            'Depth Charts (RoS)': 'rfangraphsdc',
        }
        roles = {'Batters': 'bat', 'Pitchers': 'pit'}
        self.pd['__EVENTTARGET'] = 'ProjectionBoard1$cmdCSV'
        DATA = defaultdict(list)
        DATA['source'] = 'fangraphs'
        DATA['desc'] = 'projections'

        projections_title_key = defaultdict(list)
        for projection_title, projection in projections.items():
            for role_name, role in roles.items():
                p('{:>10} {}'.format(role_name, projection_title))
                
                url = 'https://www.fangraphs.com/projections.aspx?pos=all&stats={}&type={}&team=0&lg=all&players=0'.format(role, projection)
                DATA['url'].append(url)
                
                self.post(url)

                header = self.make_header(role_name, projection_title)
                projections_title_key[header] = self.get_rows_dicts_list_from_response(self.decode_content())

        DATA['headers'].extend(['[NAME]', '[TEAM]', *list(projections_title_key.keys())])

        projections_collapse = defaultdict(dict)
        for projection_title, projection in projections_title_key.items():
            for row in projection:
                key = self.name_team_to_key(row['Name'], row['Team'])
                projections_collapse[key].update({'[NAME]': row['Name'], '[TEAM]': row['Team'], projection_title:row['WAR']})
                                            
        DATA['rows'] = list(projections_collapse.values())
                                            
        return DATA
                                            

def p(text):
    if VERBOSE_OUTPUT_TO_TERMINAL:
        print(text)
                 



if __name__ == '__main__':
    print('SCRAPERS FOLDER:', scr_003.__name__)
