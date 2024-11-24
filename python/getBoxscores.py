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
    "202411180DET": ("DET", "CHI"),
    "202411180MIA": ("MIA", "PHI"),
    "202411180NYK": ("NYK", "WAS"),
    "202411180TOR": ("TOR", "IND"),
    "202411180MIL": ("MIL", "HOU"),
    "202411180PHO": ("PHO", "ORL"),
    "202411180SAC": ("SAC", "ATL"),
    "202411180LAC": ("LAC", "GSW"),
    "202411190BOS": ("BOS", "CLE"),
    "202411190BRK": ("BRK", "CHO"),
    "202411190MEM": ("MEM", "DEN"),
    "202411190DAL": ("DAL", "NOP"),
    "202411190SAS": ("SAS", "OKC"),
    "202411190LAL": ("LAL", "UTA"),
    "202411200CLE": ("CLE", "NOP"),
    "202411200MIL": ("MIL", "CHI"),
    "202411200HOU": ("HOU", "IND"),
    "202411200MEM": ("MEM", "PHI"),
    "202411200OKC": ("OKC", "POR"),
    "202411200GSW": ("GSW", "ATL"),
    "202411200PHO": ("PHO", "NYK"),
    "202411200LAC": ("LAC", "ORL"),
    "202411210CHO": ("CHO", "DET"),
    "202411210TOR": ("TOR", "MIN"),
    "202411210SAS": ("SAS", "UTA"),
    "202411210LAL": ("LAL", "ORL"),
    "202411220PHI": ("PHI", "BRK"),
    "202411220WAS": ("WAS", "BOS"),
    "202411220MIL": ("MIL", "IND"),
    "202411220CHI": ("CHI", "ATL"),
    "202411220HOU": ("HOU", "POR"),
    "202411220NOP": ("NOP", "GSW"),
    "202411220DEN": ("DEN", "DAL"),
    "202411220LAC": ("LAC", "SAC"),
    "202411230UTA": ("UTA", "NYK"),
    "202411230ORL": ("ORL", "DET"),
    "202411230CHI": ("CHI", "MEM"),
    "202411230HOU": ("HOU", "POR"),
    "202411230MIL": ("MIL", "CHO"),
    "202411230SAS": ("SAS", "GSW"),
    "202411230LAL": ("LAL", "DEN"),

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
                player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr th[data-append-csv]")]
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
