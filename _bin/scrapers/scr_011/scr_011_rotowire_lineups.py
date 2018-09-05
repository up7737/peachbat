import os
from collections import defaultdict

import lxml.html




VERBOSE_OUTPUT_TO_TERMINAL = True


class MetaScraper(type):
    def __new__(self, classname, class_super, classdict):
        classname = os.path.basename(__file__).replace('.py', '')
        return type.__new__(self, classname, class_super, classdict)


class scr_011(metaclass=MetaScraper):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.rotowire.com',
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

    def el_text_no_child_normalized(self, text, chrs=['\r', '\n'], replace=''):
        if text and isinstance(text, list):
            el, = text
            text = el.text
            
        for c in chrs:
            text = text.replace(c, replace)
        return text.strip()
    
    def row_dict_from_list(self, *lists):
        return dict(zip(*lists))

    def run(self):
        DATA = defaultdict(list)
        DATA['scraper'] = self.__class__.__name__
        DATA['source'] = 'rotowire'
        DATA['desc'] = 'lineups'
        DATA['url'] = 'https://www.rotowire.com/baseball/daily-lineups.php'
        DATA['headers'].extend(['[TEAM_AWAY]',  '[PLAYERS_AWAY]',
                                '[TEAM_HOME]', '[PLAYERS_HOME]',
                                '[TIME_STARTS]', '[DATE]'])

        p('{:>15} {}'.format(DATA['source'], DATA['desc']))
        self.get(DATA['url'])

        tree = lxml.html.fromstring(self.response.text)
        games = tree.cssselect('div[class="lineup is-mlb"]')

        for game in games:

            game_date = self.el_text_no_child_normalized(tree.cssselect('.page-title__secondary'), chrs=['Starting MLB lineups for '])
            game_time = self.el_text_stripped(game.cssselect('.lineup__time'))
            
            team_away, team_home = game.cssselect('.lineup__matchup div')
            team_away = self.el_text_no_child_normalized(team_away.text)
            team_home = self.el_text_no_child_normalized(team_home.text)

            players_away = game.cssselect('.lineup__list.is-visit li.lineup__player a')
            players_home = game.cssselect('.lineup__list.is-home li.lineup__player a')
            
            for player_away, player_home in zip(players_away, players_home):
                player_away = self.el_text_stripped(player_away)
                player_home = self.el_text_stripped(player_home)
                
                DATA['rows'].append(
                    self.row_dict_from_list(DATA['headers'], [team_away, player_away, team_home, player_home, game_time, game_date])
                )
            
        return DATA
                                            

def p(text):
    if VERBOSE_OUTPUT_TO_TERMINAL:
        print(text)
                 



if __name__ == '__main__':
    print('SCRAPERS FOLDER:', scr_011.__name__)
