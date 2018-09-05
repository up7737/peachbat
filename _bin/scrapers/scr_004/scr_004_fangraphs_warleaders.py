import os
import datetime
import csv
from collections import defaultdict

import lxml.html




class MetaScraper(type):
    def __new__(self, classname, class_super, classdict):
        classname = os.path.basename(__file__).replace('.py', '')
        return type.__new__(self, classname, class_super, classdict)


class scr_004(metaclass=MetaScraper):
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
    
    def get_rows_dicts_list_from_response(self, decoded_content):
        headers, *data_rows = [self.data_row_to_column(row) for row in decoded_content.split('\r\n') if row.strip()]
        return [dict(zip(headers, row)) for row in data_rows]

    def data_row_to_column(self, row_text):
        return row_text.replace('"', '').split(',')

    def run(self):
        DATA = defaultdict(list)
        DATA['source'] = 'fangraphs'
        DATA['desc'] = 'warleaders'
        DATA['url'] = 'https://www.fangraphs.com/warleaders.aspx?season={}&team=all&type=0'.format(self.current_year)
        DATA['headers'].extend(['[NAME]', '[TEAM]', '[PRIMARY_WAR]', '[TOTAL_WAR]'])

        self.pd['WARBoard1$rcbSeason'] = self.pd['WARBoard1$rcbSeason'].replace('2018', str(self.current_year))
        self.post(DATA['url'])

        players_rows =  self.get_rows_dicts_list_from_response(self.decode_content())

        [DATA['rows'].append(dict(zip(DATA['headers'], [row['Name'], row['Team'], row['Primary WAR'], row['Total WAR']]))) for row in players_rows]

        return DATA




if __name__ == '__main__':
    print('SCRAPERS FOLDER:', scr_004.__name__)
