import pandas as pd
from tqdm import tqdm  # Progress bar (optional)

# Paths to CSV files
historical_data_path = r'C:\Users\ashle\Documents\Projects\hockey\data\skaters2022_25.csv'
upcoming_games_path = r'C:\Users\ashle\Documents\Projects\hockey\data\games_thisWeek.csv'
output_file_path = r'C:\Users\ashle\Documents\Projects\hockey\projectedStats.csv'

# Read the historical data and upcoming games data
historical_df = pd.read_csv(historical_data_path)
upcoming_games_df = pd.read_csv(upcoming_games_path)

# Function to calculate the average stats per group
def calculate_average_stats(group):
    return {
        'G': group['G'].mean(),
        'A': group['A'].mean(),
        'PTS': group['PTS'].mean(),
        'SOG': group['SOG'].mean(),
        'HIT': group['HIT'].mean(),
        'BLK': group['BLK'].mean(),
        'TOI': group['TOI'].mean()
    }

# Calculate player and team stats by opponent and by home/away
player_home_stats = historical_df[historical_df['Is_Home'] == 1].groupby('PlayerID').apply(calculate_average_stats).to_dict()
player_away_stats = historical_df[historical_df['Is_Home'] == 0].groupby('PlayerID').apply(calculate_average_stats).to_dict()
player_vs_opp_stats = historical_df.groupby(['PlayerID', 'Opp']).apply(calculate_average_stats).to_dict()

team_home_stats = historical_df[historical_df['Is_Home'] == 1].groupby('Team').apply(calculate_average_stats).to_dict()
team_away_stats = historical_df[historical_df['Is_Home'] == 0].groupby('Team').apply(calculate_average_stats).to_dict()
team_vs_opp_stats = historical_df.groupby(['Team', 'Opp']).apply(calculate_average_stats).to_dict()

# Function to get projected stats with team adjustment for players with fewer than 5 games
def get_projected_stats(player_id, team, opp, is_home):
    # Get stats by home/away and opponent for the player
    home_away_stats = player_home_stats.get(player_id) if is_home == 1 else player_away_stats.get(player_id)
    opp_stats = player_vs_opp_stats.get((player_id, opp))
    
    # Calculate team stats by home/away and opponent
    team_home_away_stats = team_home_stats.get(team) if is_home == 1 else team_away_stats.get(team)
    team_opp_stats = team_vs_opp_stats.get((team, opp))

    # Determine if player has fewer than 5 games in total
    player_game_count = len(historical_df[historical_df['PlayerID'] == player_id])
    
    # If player has 5 or more games, use only player's stats
    if player_game_count >= 5:
        if home_away_stats and opp_stats:
            projected_stats = {k: (0.8 * opp_stats[k] + 0.2 * home_away_stats[k]) for k in opp_stats}
        elif home_away_stats:
            projected_stats = home_away_stats
        elif opp_stats:
            projected_stats = opp_stats
        else:
            projected_stats = {'G': 0, 'A': 0, 'PTS': 0, 'SOG': 0, 'HIT': 0, 'BLK': 0, 'TOI': 0}
    
    # If player has fewer than 5 games, blend player and team stats
    else:
        # Calculate player stats weighted 80% opponent, 20% home/away
        if home_away_stats and opp_stats:
            player_weighted_stats = {k: (0.8 * opp_stats[k] + 0.2 * home_away_stats[k]) for k in opp_stats}
        elif home_away_stats:
            player_weighted_stats = home_away_stats
        elif opp_stats:
            player_weighted_stats = opp_stats
        else:
            player_weighted_stats = {'G': 0, 'A': 0, 'PTS': 0, 'SOG': 0, 'HIT': 0, 'BLK': 0, 'TOI': 0}
        
        # Calculate team stats weighted 80% opponent, 20% home/away
        if team_home_away_stats and team_opp_stats:
            team_weighted_stats = {k: (0.8 * team_opp_stats[k] + 0.2 * team_home_away_stats[k]) for k in team_opp_stats}
        elif team_home_away_stats:
            team_weighted_stats = team_home_away_stats
        elif team_opp_stats:
            team_weighted_stats = team_opp_stats
        else:
            team_weighted_stats = {'G': 0, 'A': 0, 'PTS': 0, 'SOG': 0, 'HIT': 0, 'BLK': 0, 'TOI': 0}

        # Combine player and team stats: 70% player and 30% team
        projected_stats = {k: (0.7 * player_weighted_stats[k] + 0.3 * team_weighted_stats[k]) for k in player_weighted_stats}
    
    return projected_stats

# Prepare the final results
final_results = []

# Iterate over each upcoming game and calculate projections
for index, row in tqdm(upcoming_games_df.iterrows(), total=upcoming_games_df.shape[0]):
    player_id = row['PlayerID']
    team = row['Team']
    opp = row['Opp']
    is_home = row['Is_Home']
    game_id = row['GameID']
    
    # Get projected stats
    projected_stats = get_projected_stats(player_id, team, opp, is_home)
    
    # Prepare result row
    result_row = [
        game_id, player_id, team, is_home, opp,
        projected_stats['G'], projected_stats['A'], projected_stats['PTS'],
        projected_stats['SOG'], projected_stats['HIT'], projected_stats['BLK'], projected_stats['TOI']
    ]
    
    final_results.append(result_row)

# Create a DataFrame for the final results
columns = ['GameID', 'PlayerID', 'Team', 'Is_Home', 'Opp', 'Projected G', 'Projected A', 'Projected PTS', 'Projected SOG', 'Projected HIT', 'Projected BLK', 'Projected TOI']
projected_stats_df = pd.DataFrame(final_results, columns=columns)

# Save the projected stats to a CSV
projected_stats_df.to_csv(output_file_path, index=False)

print(f"Projected stats saved to: {output_file_path}")
