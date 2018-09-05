import os
from collections import defaultdict

import lxml.html




VERBOSE_OUTPUT_TO_TERMINAL = True


class MetaScraper(type):
    def __new__(self, classname, class_super, classdict):
        classname = os.path.basename(__file__).replace('.py', '')
        return type.__new__(self, classname, class_super, classdict)


class scr_008(metaclass=MetaScraper):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.mlb.com',
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

    def el_text_stripped(self, el):
        if isinstance(el, str): return el
        elif isinstance(el, list):
            el, = el
        return el.text_content().strip()

    def row_dict_from_list(self, *lists):
        return dict(zip(*lists))

    def run(self):
        DATA = defaultdict(list)
        DATA['scraper'] = self.__class__.__name__
        DATA['source'] = 'mlb'
        DATA['desc'] = 'lineups'
        DATA['url'] = 'https://www.mlb.com/starting-lineups'
        DATA['headers'].extend(['[TEAM_HOME]', '[PLAYERS_HOME]', '[TEAM_AWAY]',  '[PLAYERS_AWAY]', '[TIME_STARTS]', '[DATE]'])

        p('{:>15}'.format('mlb lineups'))
        self.get(DATA['url'])

        tree = lxml.html.fromstring(self.response.text)
        games = tree.cssselect('.starting-lineups__matchup')

        for game in games:
            lineups_date = self.el_text_stripped(tree.cssselect('.starting-lineups__date-title--current'))
            match_time = self.el_text_stripped(game.cssselect('.starting-lineups__game-date-time'))
            team_home = self.el_text_stripped(game.cssselect('.starting-lineups__team-name--home'))
            team_away = self.el_text_stripped(game.cssselect('.starting-lineups__team-name--away'))
            
            players_home = game.cssselect('.starting-lineups__teams.starting-lineups__teams--sm.starting-lineups__teams--xl ol.starting-lineups__team--home li')
            players_away = game.cssselect('.starting-lineups__teams.starting-lineups__teams--sm.starting-lineups__teams--xl ol.starting-lineups__team--away li')

            for player_home, player_away in zip(players_home, players_away):
                player_home = self.el_text_stripped(player_home)
                player_away = self.el_text_stripped(player_away)
                
                DATA['rows'].append(
                    self.row_dict_from_list(DATA['headers'], [team_home, player_home, team_away, player_away, match_time, lineups_date])
                )
        
        return DATA
                                            

def p(text):
    if VERBOSE_OUTPUT_TO_TERMINAL:
        print(text)
                 



if __name__ == '__main__':
    print('SCRAPERS FOLDER:', scr_008.__name__)
