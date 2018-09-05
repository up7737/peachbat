import os
from collections import defaultdict

import lxml.html




VERBOSE_OUTPUT_TO_TERMINAL = True


class MetaScraper(type):
    def __new__(self, classname, class_super, classdict):
        classname = os.path.basename(__file__).replace('.py', '')
        return type.__new__(self, classname, class_super, classdict)


class scr_009(metaclass=MetaScraper):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
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

    def check_if_player_or_projected(self, player):
        return 'PROJECTED LINEUP' if not self.el_text_stripped(player) else self.el_text_stripped(player)

    def run(self):
        DATA = defaultdict(list)
        DATA['scraper'] = self.__class__.__name__
        DATA['source'] = 'rotogrinders'
        DATA['desc'] = 'lineups'
        DATA['url'] = 'https://rotogrinders.com/lineups/mlb?site=fanduel'
        DATA['headers'].extend(['[TEAM_AWAY]',  '[PLAYERS_AWAY]',
                                '[TEAM_HOME]', '[PLAYERS_HOME]',
                                '[TIME_STARTS]', '[DATE]'])

        p('{:>15} {}'.format(DATA['source'], DATA['desc']))
        self.get(DATA['url'])

        tree = lxml.html.fromstring(self.response.text)
        games = tree.cssselect('.blk.crd.lineup')

        for game in games:
            lineups_date = self.el_text_stripped(tree.cssselect('.hdr.content.site h1 span'))
            match_time = self.el_text_stripped(game.cssselect('.weather-status time'))
            
            team_away, team_home = game.cssselect('.teams>span')
            team_away = self.el_text_stripped(team_away.cssselect('.mascot'))
            team_home = self.el_text_stripped(team_home.cssselect('.mascot'))

            players_away = game.cssselect('.blk.away-team ul.players li span a')
            players_home = game.cssselect('.blk.home-team ul.players li span a')
            

            for player_away, player_home in zip(players_away, players_home):
                player_away = self.check_if_player_or_projected(player_away)
                player_home = self.check_if_player_or_projected(player_home)
                
                DATA['rows'].append(
                    self.row_dict_from_list(DATA['headers'], [team_away, player_away, team_home, player_home, match_time, lineups_date])
                )
        
        return DATA
                                            

def p(text):
    if VERBOSE_OUTPUT_TO_TERMINAL:
        print(text)
                 



if __name__ == '__main__':
    print('SCRAPERS FOLDER:', scr_009.__name__)
    import requests
    s = scr_009(requests)
    data = s.run()
