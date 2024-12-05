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

years_info = {
    "2025",
    "2024",
    "2023",
    "2022",
    "2021",
    "2020",
    "2019",
    "2018",
    "2017",
    "2016",
    "2015",
    "2014"
}

base_path = r"C:\Users\ashle\Documents\Projects\basketball"
file_paths = {
    "leaders": os.path.join(base_path, "seasonLeaders.csv"),
}

leaders_data = []

for year in years_info:
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_totals.html#totals_stats::pts"
    
    try:
        print(f"Processing {year}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')
    
        table_selector = f"#totals_stats"
        table = soup.select_one(table_selector)
        if table:
            df = pd.read_html(StringIO(str(table)))[0]
            df.insert(0, "Season", year)
            
            player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr td[data-append-csv]")]
            df["Player ID"] = player_ids + [None] * (len(df) - len(player_ids))
            
            leaders_data.append(df)

        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for year {year}: {e}")
    except Exception as e:
        print(f"Error processing data for year {year}: {e}")

# Save all collected data to CSV files by appending
if leaders_data:
    pd.concat(leaders_data, ignore_index=True).to_csv(file_paths['leaders'], index=False, encoding='utf-8', mode='a', header=not os.path.exists(file_paths['leaders']))
    print(f"Data successfully appended")

if not any([leaders_data]):
    print("No data collected.")