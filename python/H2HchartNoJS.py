import pandas as pd
from bs4 import BeautifulSoup
import os

# Paths to CSV files and directory containing HTML files
lines_path = r'C:\Users\ashle\Documents\Projects\basketball\data\todayLines.csv'
gamelogs_path = r'C:\Users\ashle\Documents\Projects\basketball\data\gamelogs.csv'
html_dir = r"C:\Users\ashle\Documents\Projects\basketball\h2h"

# Load the data
lines_df = pd.read_csv(lines_path)
gamelogs_df = pd.read_csv(gamelogs_path)
gamelogs_df['Date'] = pd.to_datetime(gamelogs_df['Date'])
gamelogs_df = gamelogs_df.sort_values(by='Date')

# Chart.js template for bar chart with betting line overlay and filter controls
chart_script_template = """
<div class="chartContainer">
    <div class="barChart-filters">
        <div class="barChartFilter">
            <label for="{stat}_{game_id}_{betting_line_id}_teamFilter" class="barChartFilterLabel">Opponent:</label>
            <select id="{stat}_{game_id}_{betting_line_id}_teamFilter" onchange="applyFilters('{stat}', '{game_id}', '{betting_line_id}')" class="barChartOptionFilter">
                <option value="all">All</option>
                {team_options}
            </select>
        </div>
        <div class="barChartFilter">
            <label for="{stat}_{game_id}_{betting_line_id}_homeAwayFilter" class="barChartFilterLabel">Home/Away:</label>
            <select id="{stat}_{game_id}_{betting_line_id}_homeAwayFilter" onchange="applyFilters('{stat}', '{game_id}', '{betting_line_id}')" class="barChartOptionFilter">
                <option value="all">All</option>
                <option value="home">Home</option>
                <option value="away">Away</option>
            </select>
        </div>
        <div class="barChartFilter">
            <label for="{stat}_{game_id}_{betting_line_id}_startDate" class="barChartFilterLabel">Start Date:</label>
            <input type="date" id="{stat}_{game_id}_{betting_line_id}_startDate" onchange="applyFilters('{stat}', '{game_id}', '{betting_line_id}')" class="barChartDateFilter">
        </div>
        <div class="barChartFilter">
            <label for="{stat}_{game_id}_{betting_line_id}_endDate" class="barChartFilterLabel">End Date:</label>
            <input type="date" id="{stat}_{game_id}_{betting_line_id}_endDate" onchange="applyFilters('{stat}', '{game_id}', '{betting_line_id}')" class="barChartDateFilter">
        </div>
        <button onclick="clearFilters('{stat}', '{game_id}', '{betting_line_id}')" class="clear-chart-filters">Clear Filters</button>
    </div>
    
    <canvas id="{stat}_{game_id}_{betting_line_id}_chart" class="barChart"></canvas>
    
    <div class="filter-buttons">
        <button onclick="filterGames('{stat}', '{game_id}', '{betting_line_id}', 5)" class="last_n_games_btn">L5</button>
        <button onclick="filterGames('{stat}', '{game_id}', '{betting_line_id}', 10)" class="last_n_games_btn">L10 Games</button>
        <button onclick="filterGames('{stat}', '{game_id}', '{betting_line_id}', 20)" class="last_n_games_btn">L20 Games</button>
        <button onclick="filterBySeason('{stat}', '{game_id}', '{betting_line_id}', '2023-24')" class="last_n_games_btn">2023-24</button>
        <button onclick="filterBySeason('{stat}', '{game_id}', '{betting_line_id}', '2024-25')" class="last_n_games_btn">2024-25</button>
        <button onclick="filterAll('{stat}', '{game_id}', '{betting_line_id}')" class="last_n_games_btn">All</button>
    </div>

    
    <div class="slider-container">
        <div id="line-slider">
            <label for="{stat}_{game_id}_{betting_line_id}_lineSlider" class="lineSliderLabel">Change Line:</label>
            <input type="range" id="{stat}_{game_id}_{betting_line_id}_lineSlider" min="0" max="100" step="0.5" value="{betting_line}" oninput="updateLine('{stat}', '{game_id}', '{betting_line_id}', this.value)" class="lineSliderInput">
            <span id="{stat}_{game_id}_{betting_line_id}_lineValue" class="lineSliderSpan">{betting_line}</span>
        </div>
        <div class="chartButtons">
            <button onclick="resetLine('{stat}', '{game_id}', '{betting_line_id}')" class="reset-line-btn">Reset Line</button>
        </div>
    </div>
</div>
    
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@1.1.0"></script>
<script src="H2HChart.js"></script>
<script>
    const allData_{stat}_{game_id}_{betting_line_id} = {chart_data};
    initializeChart("{stat}", "{game_id}", "{betting_line_id}", allData_{stat}_{game_id}_{betting_line_id}, {betting_line});
</script>
"""


# Process each HTML file
for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(html_dir, filename)
        
        # Extract player ID from filename
        player_id = filename.split("_")[0]
        
        # Read and parse HTML file
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        
        # Filter gamelogs for the player
        player_gamelogs = gamelogs_df[gamelogs_df['PlayerID'] == player_id]
        
        # Check if we have any games for this player
        if player_gamelogs.empty:
            print(f"No gamelog data found for player {player_id} in {filename}")
            continue
        
        # Get unique stats for this player in the betting lines
        player_lines = lines_df[lines_df['PlayerID'] == player_id]
        
        # Add chart for each stat in the player's betting lines
        for _, line_row in player_lines.iterrows():
            game_id = line_row['GameID']
            stat = line_row['Stat'].replace('+', '_') 
            betting_line = line_row['Line']
            betting_line_id = str(betting_line).replace('.', '_')

            
            # Filter past game data for this stat
            stat_data = player_gamelogs[['Date', 'Opp', 'Is_Home', 'Season', stat]].dropna()
            
            # Format x-axis labels and values for JavaScript
            chart_data = [
                {
                    "date": row["Date"].strftime("%Y-%m-%d"),
                    "opponent": row["Opp"], 
                    "location": "home" if row["Is_Home"] == 1 else "away", 
                    "stat": row[stat],
                    "season": row["Season"]
                }
                for _, row in stat_data.iterrows()
            ]
            
            chart_data.sort(key=lambda x: x["date"])
            
            # Generate unique team options for the dropdown
            unique_teams = sorted(player_gamelogs['Opp'].unique(), key=lambda x: x.lower())
            team_options = "\n".join([f'<option value="{team}">{team}</option>' for team in unique_teams])
            
            # Generate the chart script
            chart_script = chart_script_template.format(
                stat=stat,
                game_id=game_id,
                betting_line_id=betting_line_id, 
                chart_data=chart_data,
                betting_line=betting_line,
                team_options=team_options
            )
            
            player_table = soup.select_one("#chartPlaceholder")
            chart_soup = BeautifulSoup(chart_script, "html.parser")
            player_table.insert_after(chart_soup) 

        # Save modified HTML file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

print("All files have been processed.")
