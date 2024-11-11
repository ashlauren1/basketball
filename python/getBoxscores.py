from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os

# Define rate limit parameters
REQUESTS_PER_MINUTE = 20
ONE_MINUTE = 60

@sleep_and_retry
@limits(calls=REQUESTS_PER_MINUTE, period=ONE_MINUTE)
def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# Define the game IDs, home teams, and away teams
games_info = { 
    "202411100DET": ("DET", "HOU"),
    "202411100MIL": ("MIL", "BOS"),
    "202411100IND": ("IND", "NYK"),
    "202411100ORL": ("ORL", "WAS"),
    "202411100MIN": ("MIN", "MIA"),
    "202411100OKC": ("OKC", "GSW"),
    "202411100PHI": ("PHI", "CHO"),
    "202411100DEN": ("DEN", "DAL"),
    "202411100PHO": ("PHO", "SAC"),
    "202411100POR": ("POR", "MEM"),
    "202411100LAL": ("LAL", "TOR")
}



# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\basketball"
file_paths = {
    "boxscore": os.path.join(base_path, "boxscores.csv"),
}

# Initialize lists to collect data
boxscore_data = []

for game_id, (home_team, away_team) in games_info.items():
    url = f"https://www.basketball-reference.com/boxscores/{game_id}.html"

    try:
        print(f"Processing game ID {game_id} - Home Team: {home_team}, Away Team: {away_team}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract table
        for team in [away_team, home_team]:
            table_selector = f"#box-{team}-game-basic"
            table = soup.select_one(table_selector)
            if table:
                # Read table into DataFrame, excluding footer rows if present
                df = pd.read_html(StringIO(str(table)))[0]

                # Keep only rows within tbody (skip footer by limiting rows if needed)
                df = df.iloc[:table.select("tbody tr").__len__()]

                # Insert metadata columns
                df.insert(0, "Game ID", game_id)
                df.insert(1, "Home Team", home_team)
                df.insert(2, "Away Team", away_team)

                # Extract Player IDs from 'data-append-csv' attribute in <td> tags
                player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr td[data-append-csv]")]
                df["Player ID"] = player_ids + [None] * (len(df) - len(player_ids))  # Handle rows without Player IDs

                boxscore_data.append(df)

        # Wait to avoid rate limiting
        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for game ID {game_id}: {e}")
    except Exception as e:
        print(f"Error processing data for game ID {game_id}: {e}")

# Save all collected data to CSV files by appending
if boxscore_data:
    pd.concat(boxscore_data, ignore_index=True).to_csv(file_paths['boxscore'], index=False, encoding='utf-8', mode='a', header=not os.path.exists(file_paths['boxscore']))
    print(f"Boxscore data successfully appended to {file_paths['boxscore']}")

if not any([boxscore_data]):
    print("No data collected.")
