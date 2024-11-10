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
    "202411060CHO": ("CHO", "DET"),
    "202411060IND": ("IND", "ORL"),
    "202411060ATL": ("ATL", "NYK"),
    "202411060BOS": ("BOS", "GSW"),
    "202411060HOU": ("HOU", "SAS"),
    "202411060MEM": ("MEM", "LAL"),
    "202411060NOP": ("NOP", "CLE"),
    "202411060DAL": ("DAL", "CHI"),
    "202411060DEN": ("DEN", "OKC"),
    "202411060PHO": ("PHO", "MIA"),
    "202411060LAC": ("LAC", "PHI"),
    "202411060SAC": ("SAC", "TOR"),
    "202411070CHI": ("CHI", "MIN"),
    "202411070MIL": ("MIL", "UTA"),
    "202411070SAS": ("SAS", "POR"),
    "202411080CHO": ("CHO", "IND"),
    "202411080DET": ("DET", "ATL"),
    "202411080ORL": ("ORL", "NOP"),
    "202411080BOS": ("BOS", "BRK"),
    "202411080CLE": ("CLE", "GSW"),
    "202411080DAL": ("DAL", "PHO"),
    "202411080NYK": ("NYK", "MIL"),
    "202411080MEM": ("MEM", "WAS"),
    "202411080OKC": ("OKC", "HOU"),
    "202411080DEN": ("DEN", "MIA"),
    "202411080MIN": ("MIN", "POR"),
    "202411080LAL": ("LAL", "PHI"),
    "202411080SAC": ("SAC", "LAC")
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
