import pandas as pd
from bs4 import BeautifulSoup
import os

# Paths to CSV files and directory containing HTML files
gamelogs_path = r'C:\Users\ashle\Documents\Projects\basketball\data\gamelogs.csv'
html_dir = r'C:\Users\ashle\Documents\Projects\basketball\players'

# Load the data
gamelogs_df = pd.read_csv(gamelogs_path)
gamelogs_df['Date'] = pd.to_datetime(gamelogs_df['Date'])
gamelogs_df = gamelogs_df.sort_values(by='Date')

# List of all stats to generate charts for
all_stats = ['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV', 'MP', 'OffREB', 'DefREB', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'PF', 'BLK+STL', 'REB+AST', 'PTS+AST', 'PTS+REB', 'PTS+REB+AST', 'FANTASY']

# Default betting line and stat
default_betting_line = 0.5
default_stat = "PTS"

# Updated HTML template with an external JS file
chart_html_template = """
<div class="player-chart-container">
    <!-- Stat Selection Dropdown -->
    <div class="barChart-filters">
        <div class="barChartFilter">
            <label for="statSelector_{player_id}">Stat:</label>
            <select id="statSelector_{player_id}" onchange="updateStat('{player_id}', this.value)">
                {stat_options}
            </select>
        </div>  
        <div class="barChartFilter">
            <label for="teamFilter_{player_id}">Opponent:</label>
            <select id="teamFilter_{player_id}" onchange="applyFilters('{player_id}')">
                <option value="all">All</option>
                {team_options}
            </select>
        </div>
        <div class="barChartFilter">
            <label for="homeAwayFilter_{player_id}">Home/Away:</label>
            <select id="homeAwayFilter_{player_id}" onchange="applyFilters('{player_id}')">
                <option value="all">All</option>
                <option value="home">Home</option>
                <option value="away">Away</option>
            </select>
        </div>
        <div class="barChartFilter">
            <label for="startDate_{player_id}">Start:</label>
            <input type="date" id="startDate_{player_id}" onchange="applyFilters('{player_id}')">
        </div>
        <div class="barChartFilter">
            <label for="endDate_{player_id}">End:</label>
            <input type="date" id="endDate_{player_id}" onchange="applyFilters('{player_id}')">
        </div>
    </div>
    <canvas id="chart_{player_id}" class="player-barChart"></canvas>
    <div class="filter-buttons">
        <button id="L5_{player_id}" onclick="showRecentGames('{player_id}', 5)">L5</button>
        <button id="L10_{player_id}" onclick="showRecentGames('{player_id}', 10)">L10</button>
        <button id="L20_{player_id}" onclick="showRecentGames('{player_id}', 20)">L20</button>
        <button id="202324_{player_id}" onclick="filterBySeason('{player_id}', '2023-24')">2023-24</button>
        <button id="202425_{player_id}" onclick="filterBySeason('{player_id}', '2024-25')">2024-25</button>
        <button id="showAll_{player_id}" onclick="showAllGames('{player_id}')">All</button>
        <button id="clearFiltersBtn_{player_id}" onclick="clearFilters('{player_id}')" class="clear-chart-filters">Clear Filters</button>
    </div>
    <div class="slider-container">
        <div id="line-slider">
            <label for="lineSlider_{player_id}">Change Line:</label>
            <input type="range" id="lineSlider_{player_id}" min="0" max="30" step="0.25" value="{betting_line}" oninput="updateLine('{player_id}', this.value)">
            <span id="lineValue_{player_id}">{betting_line}</span>
        </div>
        <div class="chartButtons">
            <button id="reset-line-btn_{player_id}" onclick="updateLine('{player_id}', {betting_line})" class="reset-line-btn">Reset Line</button>
        </div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@1.1.0"></script>
<script src="chartScript.js"></script>
<script>
    // Initialize the chart with player-specific data by calling a function from chart_logic.js
    initializeChart("{player_id}", {chart_data}, {betting_line}, "{default_stat}");
</script>
"""

for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(html_dir, filename)
        player_id = filename.replace(".html", "")
                
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as file:
                soup = BeautifulSoup(file, "html.parser")

        # Select where to insert the chart based on table id
        player_table = soup.select_one("#table-container")
        if not player_table:
            print(f"No player table found in {filename}. Skipping.")
            continue

        # Filter gamelogs for the player
        player_gamelogs = gamelogs_df[gamelogs_df['PlayerID'] == player_id]
        if player_gamelogs.empty:
            print(f"No gamelog data found for player {player_id} in {filename}")
            continue

        unique_teams = sorted(player_gamelogs['Opp'].unique(), key=lambda x: x.lower())
        team_options = "\n".join([f'<option value="{team}">{team}</option>' for team in unique_teams])
        chart_data = [
            {
                "date": row["Date"].strftime("%Y-%m-%d"),
                "opponent": row["Opp"],
                "location": "home" if row["Is_Home"] == 1 else "away",
                "season": row["Season"],
                **{stat: row[stat] for stat in all_stats if stat in row}
            }
            for _, row in player_gamelogs.iterrows()
        ]
        chart_data.sort(key=lambda x: x["date"])

        # Mapping of short stat codes to full names
        stat_map = {
            "PTS": "Points",
            "REB": "Rebounds",
            "AST": "Assists",
            "STL": "Steals",
            "BLK": "Blocks", 
            "TOV": "Turnovers", 
            "MP": "Minutes Played",
            "OffREB": "Offensive Rebounds",
            "DefREB": "Defensive Rebounds", 
            "FG": "Field Goals", 
            "FGA": "Field Goal Attempts", 
            "3P": "3-Pointers", 
            "3PA": "3-Point Attempts", 
            "FT": "Free Throws", 
            "FTA": "Free Throw Attempts", 
            "PF": "Fouls",
            "BLK+STL": "BLK+STL",
            "REB+AST": "REB+AST",
            "PTS+AST": "PTS+AST",
            "PTS+REB": "PTS+REB",
            "PTS+REB+AST": "PTS+REB+AST",
            "FANTASY": "Fantasy Score"
        }
        stat_options = "\n".join([f'<option value="{stat}">{stat_map.get(stat, stat)}</option>' for stat in all_stats])

        chart_html = chart_html_template.format(
            player_id=player_id,
            stat_options=stat_options,
            chart_data=chart_data,
            betting_line=default_betting_line,
            default_stat=default_stat,
            team_options=team_options
        )
        chart_soup = BeautifulSoup(chart_html, "html.parser")
        player_table.insert_before(chart_soup)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

print("All files have been processed.")
