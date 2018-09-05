import os
import datetime
import csv
import itertools
from collections import defaultdict

import lxml.html




VERBOSE_OUTPUT_TO_TERMINAL = True


class MetaScraper(type):
    def __new__(self, classname, class_super, classdict):
        classname = os.path.basename(__file__).replace('.py', '')
        return type.__new__(self, classname, class_super, classdict)


class scr_006(metaclass=MetaScraper):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.espn.com',
        'Referer': 'http://www.espn.com/mlb/teams',
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
        roles_and_war_col_name_target = {'batting': 'OWAR', 'pitching': 'WAR', 'fielding': 'DWAR'}
        # hardcoded to save 1 request
        all_teams_short_names = {
            'bal': 'Baltimore Orioles', 'bos': 'Boston Red Sox', 'nyy': 'New York Yankees',
            'tb': 'Tampa Bay Rays', 'tor': 'Toronto Blue Jays', 'atl': 'Atlanta Braves',
            'mia': 'Miami Marlins', 'nym': 'New York Mets', 'phi': 'Philadelphia Phillies',
            'wsh': 'Washington Nationals', 'chw': 'Chicago White Sox', 'cle': 'Cleveland Indians',
            'det': 'Detroit Tigers', 'kc': 'Kansas City Royals', 'min': 'Minnesota Twins',
            'chc': 'Chicago Cubs', 'cin': 'Cincinnati Reds', 'mil': 'Milwaukee Brewers',
            'pit': 'Pittsburgh Pirates', 'stl': 'St. Louis Cardinals', 'hou': 'Houston Astros',
            'laa': 'Los Angeles Angels', 'oak': 'Oakland Athletics', 'sea': 'Seattle Mariners',
            'tex': 'Texas Rangers', 'ari': 'Arizona Diamondbacks', 'col': 'Colorado Rockies',
            'lad': 'Los Angeles Dodgers', 'sd': 'San Diego Padres', 'sf': 'San Francisco Giants'
        }
        
        DATA = defaultdict(list)
        DATA['source'] = 'espn'
        DATA['desc'] = 'projections'
        DATA['headers'].extend(['[NAME]', '[TEAM]', '[BATTING_OWAR]', '[PITCHING_WAR]', '[FIELDING_DWAR]'])

        projections_collapsed = defaultdict(dict)
        for team_short_name, team_name in all_teams_short_names.items():
            p('{:>23}'.format(team_name))

            for role, war_col_name_target in roles_and_war_col_name_target.items():
                url = 'http://www.espn.com/mlb/teams/{}?team={}'.format(role, team_short_name)
                DATA['url'].append(url)

                self.get(url)

                tree = lxml.html.fromstring(self.response.text)
                headers = tree.cssselect('.tablehead tr')[1]
                #code golfing here. refactor to clean methods.
                table_rows = list(
                    itertools.takewhile(
                        lambda el: el.cssselect('td')[0].text_content() != 'Totals',[el for el in tree.cssselect('.tablehead tr')[2:]]
                    )
                )
                table_rows_text = [dict(zip([i.text_content() for i in headers], [i.text_content() for i in row])) for row in table_rows]

                for row in table_rows_text:
                    war_col_name_output = '[{}]'.format('_'.join([role, war_col_name_target]).upper())
                    projections_collapsed[row['NAME']].update(
                        {'[NAME]': row['NAME'], '[TEAM]': team_name, war_col_name_output: row[war_col_name_target]}
                    )

        DATA['rows'] = list(projections_collapsed.values())
        return DATA
                                            

def p(text):
    if VERBOSE_OUTPUT_TO_TERMINAL:
        print(text)
                 



if __name__ == '__main__':
    print('SCRAPERS FOLDER:', scr_007.__name__)
