from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os
from datetime import datetime

# Define rate limit parameters
REQUESTS_PER_MINUTE = 20
ONE_MINUTE = 60

@sleep_and_retry
@limits(calls=REQUESTS_PER_MINUTE, period=ONE_MINUTE)
def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def convert_mp_to_decimal(mp_str):
    """Convert MP from 'mm:ss' to decimal minutes."""
    try:
        minutes, seconds = map(int, mp_str.split(':'))
        return minutes + seconds / 60
    except ValueError:
        return None

def extract_date_from_game_id(game_id):
    date_str = game_id[:8]
    return datetime.strptime(date_str, "%Y%m%d").strftime("%m/%d/%Y")

# Define the game IDs, home teams, and away teams
games_info = {
    "202411250CHO": ("CHO", "ORL"),
    "202411250DET": ("DET", "TOR"),
    "202411250IND": ("IND", "NOP"),
    "202411250ATL": ("ATL", "DAL"),
    "202411250BOS": ("BOS", "LAC"),
    "202411250MEM": ("MEM", "POR"),
    "202411250DEN": ("DEN", "NYK"),
    "202411250GSW": ("GSW", "BRK"),
    "202411250SAC": ("SAC", "OKC")
}

# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\basketball"
file_paths = {
    "boxscore": os.path.join(base_path, "basketballRef_Boxscores.csv"),
}

player_columns = [
    "Home", "HomeName", "Away", "AwayName", "Season", "GameID", "Date", "Game", "Player", "PlayerID", "Team", "TeamName", "Is_Home", "Opp", "OppName", "PTS", "REB", "AST", "STL", "BLK", "TOV", "MP", "OffREB", "DefREB", "FG", "FGA", "3P", "3PA", "FT", "FTA", "PF"
]

# Initialize lists to collect data
boxscore_data = []

for game_id, (home_team, away_team) in games_info.items():
    url = f"https://www.basketball-reference.com/boxscores/{game_id}.html"

    try:
        print(f"Processing game ID {game_id} - Home Team: {home_team}, Away Team: {away_team}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get full team names
        home_team_section = soup.select_one(f"#box-{home_team}-game-basic_sh")
        away_team_section = soup.select_one(f"#box-{away_team}-game-basic_sh")
        home_team_name = home_team_section.find("h2").get_text(strip=True) if home_team_section else "Unknown"
        away_team_name = away_team_section.find("h2").get_text(strip=True) if away_team_section else "Unknown"
        
        # Extract table
        for team, team_name, is_home in [
            (home_team, home_team_name, True),
            (away_team, away_team_name, False),
        ]:
            table_selector = f"#box-{team}-game-basic"
            table = soup.select_one(table_selector)
            if table:
                # Extract the correct header row (second row in the <thead>)
                header_row = table.select("thead tr")[1]
                headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
                
                headers[0] = "Player"
                
                rows = table.select("tbody tr:not([data-stat='reason'])")
                
                consolidated_rows = []
                for row in rows:
                    # Skip section headers like "Starters" and "Reserves"
                    if "Starters" in row.get_text(strip=True) or "Reserves" in row.get_text(strip=True):
                        continue
                    consolidated_rows.append(row)
                
                consolidated_html = '<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>'.format(
                    ''.join(f'<th>{header}</th>' for header in headers),
                    ''.join(str(row) for row in consolidated_rows)
                )
                df = pd.read_html(StringIO(consolidated_html), encoding="utf-8")[0]
                
                # Map and clean up column names
                column_mapping = {
                    "TRB": "REB",
                    "ORB": "OffREB",
                    "DRB": "DefREB",
                }
                df = df.rename(columns=column_mapping)
                
                # Keep only relevant columns
                df = df[["Player", "PTS", "REB", "AST", "STL", "BLK", "TOV", "MP", "OffREB", "DefREB", "FG", "FGA", "3P", "3PA", "FT", "FTA", "PF"]]
                
                # Convert MP to decimal
                if "MP" in df.columns:
                    df["MP"] = df["MP"].apply(convert_mp_to_decimal)
                
                # Insert metadata columns        
                df.insert(0, "Home", home_team)
                df.insert(1, "HomeName", home_team_name)
                df.insert(2, "Away", away_team)
                df.insert(3, "AwayName", away_team_name)
                df.insert(4, "Season", "2024-25")
                df.insert(5, "GameID", game_id)
                df.insert(6, "Date", extract_date_from_game_id(game_id))
                df.insert(7, "Game", f"{home_team} vs {away_team}")
                
                # Extract Player IDs from 'data-append-csv' attribute in <th> tags
                player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr th[data-append-csv]")]
                df["Player ID"] = player_ids + [None] * (len(df) - len(player_ids))  # Handle rows without Player IDs
                df.insert(df.columns.get_loc("Player") + 1, "PlayerID", player_ids + [None] * (len(df) - len(player_ids)))
                df.insert(df.columns.get_loc("Player") + 2, "Team", home_team if is_home else away_team)
                df.insert(df.columns.get_loc("Player") + 3, "TeamName", home_team_name if is_home else away_team_name)
                df.insert(df.columns.get_loc("Player") + 4, "Is_Home", 1 if is_home else 0)
                df.insert(df.columns.get_loc("Player") + 5, "Opp", away_team if is_home else home_team)
                df.insert(df.columns.get_loc("Player") + 6, "OppName", away_team_name if is_home else home_team_name)
                
                df = df.reindex(columns=player_columns, fill_value=None)

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