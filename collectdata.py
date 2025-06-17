from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team, League, Outcome, Location, OutputType, Position, OutputWriteOption, PeriodType
import pandas as pd
import os
import time
from tqdm import tqdm
import logging
import argparse
from pathlib import Path


logging.basicConfig(filename='debug.log',
                    level=logging.INFO,
                    format=' %(asctime)s - %(levelname)s - %(message)s')

parser = argparse.ArgumentParser()
parser.add_argument('--start_year', type=int, required=False, default=2022,
                    help='Starting season (Year)')
parser.add_argument('--end_year', type=int, required=False, default=2022,
                    help='Final season (Year)')
parser.add_argument('--output_dir', type=str, required=False, default='data',
                    help='Where to save CSV files')
args = parser.parse_args()

output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)

def scrape_daily_box_scores(start_year: int, end_year: int, output_dir: Path):
    """Scrape daily box scores for the specified range of years."""
    for year in range(start_year, end_year + 1):
        logging.info(f"Fetching schedule for season ending {year}")
        try:
            season_schedule = client.get_season_schedule(season_end_year=year)
        except Exception as e:
            logging.error(f"Error retrieving schedule for {year}: {e}")
            continue

        game_days = sorted({game['start_time'].date()
                            for game in season_schedule})

        logging.info(f"Got {len(game_days)} game days for {year}")
        season_player_box = []
        season_team_box = []

        for game_day in tqdm(game_days, desc=f"Fetching box scores for {year}"):
            try:
                player_box = client.get_player_box_scores(day=game_day.day,
                                                          month=game_day.month,
                                                          year=game_day.year)
                for record in player_box:
                    record['game_date'] = game_day.isoformat()
                season_player_box.extend(player_box)

                team_box = client.get_team_box_scores(day=game_day.day,
                                                     month=game_day.month,
                                                     year=game_day.year)
                for record in team_box:
                    record['game_date'] = game_day.isoformat()
                season_team_box.extend(team_box)

                time.sleep(0.7)  # To avoid overloading API

            except Exception as e:
                logging.error(f"Error retrieving box scores for {game_day}: {e}")
                continue

        if season_player_box:
            df = pd.DataFrame(season_player_box)
            fname = output_dir / f"player_box_scores_{year}.csv"
            df.to_csv(fname, index=False)
            logging.info(f"Player box scores for {year} saved to {fname}")

        if season_team_box:
            df = pd.DataFrame(season_team_box)
            fname = output_dir / f"team_box_scores_{year}.csv"
            df.to_csv(fname, index=False)
            logging.info(f"Team box scores for {year} saved to {fname}")

if __name__ == '__main__':
    scrape_daily_box_scores(args.start_year, args.end_year, output_dir)
    logging.info("Done.")
