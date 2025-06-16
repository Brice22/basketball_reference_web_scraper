import argparse
import pandas as pd
from basketball_reference_web_scraper.players import regular_season_player_stats

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Path to output CSV.")
    args = parser.parse_args()

    # Retrieve the data
    data = regular_season_player_stats()

    # Save to CSV
    data.to_csv(args.output, index=False)

    print(f"Data successfully saved to {args.output}")

if __name__ == "__main__":
    main()
