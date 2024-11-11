import json
import pandas as pd

# Path to the JSON file
json_file_path = r"C:\Users\ashle\Documents\Projects\basketball\data\prizePicks.json"

# Load the JSON data
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Extract relevant data
projections = data['data']

# Convert JSON data into a flat structure for DataFrame
flattened_data = []
for item in projections:
    entry = {
        'id': item['id'],
        'adjusted_odds': item['attributes'].get('adjusted_odds'),
        'board_time': item['attributes'].get('board_time'),
        'description': item['attributes'].get('description'),
        'line_score': item['attributes'].get('line_score'),
        'odds_type': item['attributes'].get('odds_type'),
        'projection_type': item['attributes'].get('projection_type'),
        'rank': item['attributes'].get('rank'),
        'start_time': item['attributes'].get('start_time'),
        'stat_display_name': item['attributes'].get('stat_display_name'),
        'status': item['attributes'].get('status'),
        'today': item['attributes'].get('today'),
        'updated_at': item['attributes'].get('updated_at'),
        'duration_id': item['relationships']['duration']['data'].get('id') if item['relationships']['duration']['data'] else None,
        'league_id': item['relationships']['league']['data'].get('id') if item['relationships']['league']['data'] else None,
        'player_id': item['relationships']['new_player']['data'].get('id') if item['relationships']['new_player']['data'] else None,
        'projection_type_id': item['relationships']['projection_type']['data'].get('id') if item['relationships']['projection_type']['data'] else None,
        'stat_type_id': item['relationships']['stat_type']['data'].get('id') if item['relationships']['stat_type']['data'] else None
    }
    flattened_data.append(entry)

# Convert to DataFrame
df = pd.DataFrame(flattened_data)

# Specify output path for CSV
csv_file_path = r"C:\Users\ashle\Documents\Projects\basketball\data\prizePicks.csv"

# Save as CSV
df.to_csv(csv_file_path, index=False)

csv_file_path
