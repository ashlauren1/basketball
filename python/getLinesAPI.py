import requests
import pandas as pd

# API setup
api_key = '2a929a68-7b7a-4f6d-9467-5b2f00198177'
base_url = 'https://api.dailyfantasyapi.io/v1/lines/upcoming'
headers = {
    'x-api-key': api_key
}
params = {
    'sportsbook': 'PrizePicks',
    'league': 'NBA',
    'is_available': 'true'
}

# Initialize an empty list to collect all lines data
all_lines_data = []

# Pagination loop (assuming API returns a "next" key in pagination)
while True:
    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()

        # Check if there are results; if not, break the loop
        if not data:
            break

        # Process data for each item in the JSON response
        for item in data:
            line_changes = item.get('line_changes', [])
            for player in item.get('players', []):
                all_lines_data.append({
                    'Line ID': item.get('line_id'),
                    'Game ID': item.get('game_id'),
                    'Player Name': player.get('name', 'N/A'),
                    'Normalized Name': player.get('normalized_name', 'N/A'),
                    'Team': player.get('team', 'N/A'),
                    'Market': item.get('market'),
                    'Line': item.get('line'),
                    'League': item.get('league'),
                    'Sportsbook': item.get('sportsbook'),
                    'Game Date': item.get('game_date'),
                    'Start Time': item.get('start_time'),
                    'Score': item.get('score'),
                    'Grade': item.get('grade'),
                    'Latest Line Change': line_changes[-1].get('value', 'N/A') if line_changes else 'N/A',
                    'Change Timestamp': line_changes[-1].get('timestamp', 'N/A') if line_changes else 'N/A'
                })

        # Stop if there’s no next page
        # This assumes the API returns pagination info, like a "next" URL or "page" parameter
        # Adjust based on actual pagination fields if available
        if 'next' not in response.links:
            break
        else:
            # Update the URL for the next page if it exists
            base_url = response.links['next']['url']
    else:
        print(f"Error fetching data. Status code: {response.status_code}")
        break

# Save all collected data to CSV
df = pd.DataFrame(all_lines_data)
csv_path = r'C:\Users\ashle\Documents\Projects\basketball\basketball_lines.csv'
df.to_csv(csv_path, index=False)
print(f"Data saved to '{csv_path}' with {len(all_lines_data)} entries.")
