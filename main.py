import os
import time
import csv

from _bin.engine import Engine
# Someone smart shall make this part dynamic
# __import__ fails for package import (pack.pack)
from _bin.scrapers.scr_001.scr_001_fangraphs_standings import scr_001
from _bin.scrapers.scr_002.scr_002_baseballprospectus_standings import scr_002
from _bin.scrapers.scr_003.scr_003_fangraphs_projections import scr_003
from _bin.scrapers.scr_004.scr_004_fangraphs_warleaders import scr_004
from _bin.scrapers.scr_005.scr_005_baseball_reference_projections import scr_005
from _bin.scrapers.scr_006.scr_006_espn_projections import scr_006
from _bin.scrapers.scr_007.scr_007_baseballprospectus_projections import scr_007
from _bin.scrapers.scr_008.scr_008_mlb_lineups import scr_008
from _bin.scrapers.scr_009.scr_009_rotogrinders_lineups import scr_009
from _bin.scrapers.scr_010.scr_010_baseballpress_lineups import scr_010
from _bin.scrapers.scr_011.scr_011_rotowire_lineups import scr_011




TIME_START = time.time()


class ToolBox:
    @staticmethod
    def make_dir_if_not_exists(dirname):
        if not os.path.exists(dirname):
            os.mkdir(dirname)

    @staticmethod
    def add_quote_if_float(value):
        try:
            float(value)
            return "'{}".format(value)
        except ValueError:
            return value


def dump_to_csv(DATA, scraper_name, default_col_value='-', output_dir='output'):
    """ Move to package with DB class Dump.
    """
    ToolBox.make_dir_if_not_exists(output_dir)
    filename = '{}.csv'.format(scraper_name)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8-sig') as OUT_CSV:
        csv_writer = csv.writer(OUT_CSV, lineterminator='\n', escapechar='\\', delimiter=';', quoting=csv.QUOTE_NONE)
        csv_writer.writerow(DATA['headers'])
        
        for row in DATA['rows']:
            csv_writer.writerow([ToolBox.add_quote_if_float(row.get(header, default_col_value)) for header in DATA['headers']])


def check_scr(scr_obj, engine):
    start = time.time()
    
    print(scr_obj.__name__)
    
    scraper = scr_obj(engine)
    data = scraper.run()
    
    print('Data rows:', len(data['rows']),
          end='\n--- Scraper time: {}\n'.format(time.time() - start))
    
    return data


def main(*scrapers, engine=Engine('requests')):
    
    for scr in scrapers:
        res = check_scr(scr, engine)
        print('--- Overall time:', time.time() - TIME_START, end='\n'*2)
        dump_to_csv(res, scr.__name__)


def main_lineups_determined(*scrapers, engine=Engine('requests'), force_output=True):
    """
    while True:
        determined = [
            lineups for lineups in [check_scr(scr, engine) for scr in scrapers]
                if len(lineups['rows']) == 135 or print(len(lineups['rows']), lineups['source'], lineups['desc'])
        ]
        if not determined: print('{:>15}'.format('TBD, retry lineups')); break
        else: [dump_to_csv(lineups, lineups['scraper']) for lineups in determined]; break
    """
    # temp. remove line and kwarg
    if force_output: [
        dump_to_csv(lineups, lineups['scraper']) for lineups in
            [check_scr(scr, engine) for scr in scrapers if not print('--- Overall time:', time.time() - TIME_START, end='\n'*2)]
    ]

if __name__ == '__main__':
    main(
        scr_001,
        scr_002,
        scr_003,
        scr_004,
        scr_005,
        scr_006,
        scr_007,
    )
    
    main_lineups_determined(
        scr_008,
        scr_009,
        scr_010,
        scr_011,
    )
