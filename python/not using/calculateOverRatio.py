import pandas as pd

# File paths
input_file_path = r"C:\Users\ashle\Documents\Projects\hockey\data\historic.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\hockey\overRatio.csv"

# Define the stat lines to evaluate
lines = {
    'G': [0.5],
    'A': [0.5, 1.5],
    'PTS': [0.5, 1.5, 2.5],
    'SOG': [1.5, 2.5, 3.5, 4.5, 5.5],
    'BLK': [0.5, 1.5, 2.5, 3.5, 4.5],
    'HIT': [0.5, 1.5, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5],
    'TOI': [17.5, 18.5, 18.75, 19, 19.5, 20, 20.25, 20.5, 20.75, 21, 21.25, 21.75, 22.25, 22.5, 22.75, 23, 23.25, 23.5, 23.75, 24, 24.25, 24.5, 24.75, 25, 25.25, 25.5]
}

# Load historical data
data = pd.read_csv(input_file_path, parse_dates=["Date"])

# Function to calculate the over-line ratio for a specific stat and line
def calculate_over_line_ratio(filtered_data, line):
    over_line_count = (filtered_data['#'] > line).sum()
    total_games = len(filtered_data['Gm#'].unique())
    return f"{over_line_count}/{total_games}" if total_games > 0 else "0/0"

# Initialize final results
results = []

# Iterate over each player and stat
for player_id, player_data in data.groupby('PlayerID'):
    for stat, stat_lines in lines.items():
        # Filter data for the specific stat
        stat_data = player_data[player_data['Stat'] == stat].sort_values('Gm#', ascending=False)
        
        # Define subsets for each game range based on unique game numbers
        current_season_data = stat_data[stat_data['Season'] == '2024-25']
        last_5_games = stat_data.groupby('Gm#').head(1).head(5)  # Last 5 unique games for this stat
        last_10_games = stat_data.groupby('Gm#').head(1).head(10)
        last_20_games = stat_data.groupby('Gm#').head(1).head(20)
        last_30_games = stat_data.groupby('Gm#').head(1).head(30)
        previous_season_data = stat_data[stat_data['Season'] == '2023-24']

        for line in stat_lines:
            # Calculate the ratios for each category and line
            row = {
                'PlayerID': player_id,
                'Stat': stat,
                'Line': line,
                '2024-25': calculate_over_line_ratio(current_season_data, line),
                'L5': calculate_over_line_ratio(last_5_games, line),
                'L10': calculate_over_line_ratio(last_10_games, line),
                'L20': calculate_over_line_ratio(last_20_games, line),
                'L30': calculate_over_line_ratio(last_30_games, line),
                '2023-24': calculate_over_line_ratio(previous_season_data, line),
                'All': calculate_over_line_ratio(stat_data, line)
            }
            results.append(row)

# Convert results to DataFrame
results_df = pd.DataFrame(results, columns=['PlayerID', 'Stat', 'Line', '2024-25', 'L5', 'L10', 'L20', 'L30', '2023-24', 'All'])

# Save to CSV
results_df.to_csv(output_file_path, index=False)

print("Summary statistics saved to:", output_file_path)
