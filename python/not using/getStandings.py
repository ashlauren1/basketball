from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os

REQUESTS_PER_MINUTE = 20
ONE_MINUTE = 60

@sleep_and_retry
@limits(calls=REQUESTS_PER_MINUTE, period=ONE_MINUTE)
def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

conferences_info = {
    "confs": ("E", "W")
}

base_path = r"C:\Users\ashle\Documents\Projects\basketball"
file_paths = {
    "standings": os.path.join(base_path, "standings.csv"),
}

standings_data = []

for group, (eastern_conference, western_conference) in conferences_info.items():
    url = "https://www.basketball-reference.com/leagues/NBA_2025.html"
    
    try:
        print(f"Processing {group}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')
    
        for conference in [eastern_conference, western_conference]:
            table_selector = f"#{group}_standings_{conference}"
            table = soup.select_one(table_selector)
            if table:
                df = pd.read_html(StringIO(str(table)))[0]
                
                standings_data.append(df)

        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for group {group}: {e}")
    except Exception as e:
        print(f"Error processing data for group {group}: {e}")

# Save all collected data to CSV files by appending
if standings_data:
    pd.concat(standings_data, ignore_index=True).to_csv(file_paths['standings'], index=False, encoding='utf-8', mode='a', header=not os.path.exists(file_paths['standings']))
    print(f"Data successfully appended")

if not any([standings_data]):
    print("No data collected.")