import pandas as pd
import os
import re
from datetime import datetime
from tqdm import tqdm
import json

# File paths
metrics_file_path = r"C:\Users\ashle\Documents\Projects\basketball\data\gamelogs.csv"
lines_file_path = r"C:\Users\ashle\Documents\Projects\basketball\data\todayLines.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\basketball\index.html"
rosters_file_path = r"C:\Users\ashle\Documents\Projects\basketball\data\rosters.csv"
rosters_data = pd.read_csv(rosters_file_path)

# Load data
metrics_data = pd.read_csv(metrics_file_path,  parse_dates=["Date"], low_memory=False)
lines_data = pd.read_csv(lines_file_path)

player_links = {f"{row['Player']} ({row['PlayerID']})".lower(): f"/basketball/players/{row['PlayerID']}.html" 
                for _, row in rosters_data.iterrows()}


team_links = {row['Team'].lower(): f"/basketball/teams/{row['TeamID']}.html" 
              for _, row in rosters_data.drop_duplicates('TeamID').iterrows()}

# Write out to JSON with proper formatting
with open("players.json", "w") as f:
    json.dump(player_links, f, indent=4)

with open("teams.json", "w") as f:
    json.dump(team_links, f)

print("players.json and teams.json created successfully!")

# Convert relevant columns to numeric types to avoid type errors
metrics_data[['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV', 'MP', 'OffREB', 'DefREB', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'PF', 'BLK_STL', 'REB_AST', 'PTS_AST', 'PTS_REB', 'PTS_REB_AST', 'FANTASY']] = metrics_data[['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV', 'MP', 'OffREB', 'DefREB', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'PF', 'BLK_STL', 'REB_AST', 'PTS_AST', 'PTS_REB', 'PTS_REB_AST', 'FANTASY']].apply(pd.to_numeric, errors='coerce')

lines_players = lines_data['PlayerID'].unique()
metrics_data = metrics_data[metrics_data['PlayerID'].isin(lines_players)]

# Create a dictionary mapping GameID to Game
game_mapping = lines_data.set_index('GameID')['Game'].to_dict()


# Functions to calculate averages and ratios
def calculate_average_stats(group):
    return {stat: group[stat].mean() for stat in ['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV', 'MP', 'OffREB', 'DefREB', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'PF', 'BLK_STL', 'REB_AST', 'PTS_AST', 'PTS_REB', 'PTS_REB_AST', 'FANTASY']}

def calculate_over_ratio(filtered_data, line, stat):
    over_count = (filtered_data[stat] > line).sum()
    total_games = len(filtered_data)
    return f"{over_count}/{total_games}" if total_games > 0 else "0/0"

# Aggregated stats
player_home_stats = metrics_data[metrics_data['Is_Home'] == 1].groupby('PlayerID').apply(calculate_average_stats, include_groups=False).to_dict()
player_away_stats = metrics_data[metrics_data['Is_Home'] == 0].groupby('PlayerID').apply(calculate_average_stats, include_groups=False).to_dict()
player_vs_opp_stats = metrics_data.groupby(['PlayerID', 'Opp']).apply(calculate_average_stats, include_groups=False).to_dict()

team_home_stats = metrics_data[metrics_data['Is_Home'] == 1].groupby('Team').apply(calculate_average_stats, include_groups=False).to_dict()
team_away_stats = metrics_data[metrics_data['Is_Home'] == 0].groupby('Team').apply(calculate_average_stats, include_groups=False).to_dict()
team_vs_opp_stats = metrics_data.groupby(['Team', 'Opp']).apply(calculate_average_stats, include_groups=False).to_dict()

# Projections function
def get_projected_stats(player_id, team, opp, is_home):
    home_away_stats = player_home_stats.get(player_id) if is_home == 1 else player_away_stats.get(player_id)
    opp_stats = player_vs_opp_stats.get((player_id, opp))
    team_home_away_stats = team_home_stats.get(team) if is_home == 1 else team_away_stats.get(team)
    team_opp_stats = team_vs_opp_stats.get((team, opp))
    
    player_game_count = len(metrics_data[metrics_data['PlayerID'] == player_id])
    if player_game_count >= 5:
        if home_away_stats and opp_stats:
            return {k: (0.8 * opp_stats[k] + 0.2 * home_away_stats[k]) for k in opp_stats}
        return home_away_stats or opp_stats or {stat: 0 for stat in ['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV', 'MP', 'OffREB', 'DefREB', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'PF', 'BLK_STL', 'REB_AST', 'PTS_AST', 'PTS_REB', 'PTS_REB_AST', 'FANTASY']}
    else:
        player_weighted_stats = {k: (0.8 * opp_stats[k] + 0.2 * home_away_stats[k]) for k in opp_stats} if home_away_stats and opp_stats else home_away_stats or opp_stats or {stat: 0 for stat in ['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV', 'MP', 'OffREB', 'DefREB', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'PF', 'BLK_STL', 'REB_AST', 'PTS_AST', 'PTS_REB', 'PTS_REB_AST', 'FANTASY']}
        team_weighted_stats = {k: (0.8 * team_opp_stats[k] + 0.2 * team_home_away_stats[k]) for k in team_opp_stats} if team_home_away_stats and team_opp_stats else team_home_away_stats or team_opp_stats or {stat: 0 for stat in ['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV', 'MP', 'OffREB', 'DefREB', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'PF', 'BLK_STL', 'REB_AST', 'PTS_AST', 'PTS_REB', 'PTS_REB_AST', 'FANTASY']}
        return {k: (0.7 * player_weighted_stats[k] + 0.3 * team_weighted_stats[k]) for k in player_weighted_stats}

# Ratio calculations based on max game number
def calculate_ratios(player_data, stat, line):
    max_game_num = player_data['Gm#'].max()
    last_n_games = {5: 'L5', 10: 'L10', 20: 'L20', 30: 'L30'}
    ratios = {}
    for n, label in last_n_games.items():
        recent_games = player_data[player_data['Gm#'] >= max_game_num - n + 1]
        ratios[label] = calculate_over_ratio(recent_games, line, stat)
    return ratios

# Probability calculation function
weights = {"opponent": 0.80, "home_away": 0.20}
def calculate_probability(data, stat, line):
    return (data[stat] > line).mean() if len(data) > 0 else 0

# Initialize a set to store unique (player_id, opp) pairs
h2h_pairs = set()

# Generate final results
final_results = []
columns = ['Game', 'Team', 'Player', 'Type', 'Stat', 'Line', 'Proj.', 'Diff.', 'Prob.', '2024-25', 'H2H', 'L5', 'L10', 'L20', '2023-24', 'All']

unique_combinations = set()

# Process each game
for _, game in tqdm(lines_data.iterrows(), total=lines_data.shape[0]):
    player_id = game['PlayerID']
    team = game['Team']
    is_home = game['Is_Home']
    opp = game['Opp']
    game_id = game['GameID']
    game_display = game_mapping.get(game['GameID'], game['GameID'])
    
    # Add the player-opponent pair to the set
    h2h_pairs.add((player_id, opp))
    
    player_data = metrics_data[metrics_data['PlayerID'] == player_id]
    lines_for_player = lines_data[lines_data['PlayerID'] == player_id]
    
    if not player_data.empty and not lines_for_player.empty:
        player_name = lines_for_player.iloc[0]['Player']  # Fetch player name
        projected_stats = get_projected_stats(player_id, team, opp, is_home)
        
        # Process each line for player
        for _, line_row in lines_for_player.iterrows():
            stat = line_row['Stat']
            line_value = line_row['Line']
            stat_type = line_row['Type']
            
            unique_key = (player_id, stat, line_value, stat_type)
            if unique_key in unique_combinations:
                continue  # Skip this row if already processed
            
            # Add to set of unique combinations
            unique_combinations.add(unique_key)
            
            
            # Helper function to safely evaluate ratios
            def safe_eval_ratio(ratio_str):
                try:
                    if '/' in ratio_str:
                        x, n = map(int, ratio_str.split('/'))
                        return f"{(x / n):.2f}" if n != 0 else ratio_str  # Avoid division by zero
                    return ratio_str
                except ZeroDivisionError:
                    return ratio_str

            # Calculate difference and probability
            projected_value = projected_stats.get(stat, 0)
            difference = projected_value - line_value
            opp_data = player_data[player_data['Opp'] == opp]
            opp_prob = calculate_probability(opp_data, stat, line_value)
            home_away_data = player_data[player_data['Is_Home'] == is_home]
            home_away_prob = calculate_probability(home_away_data, stat, line_value)
            weighted_prob = (weights["opponent"] * opp_prob + weights["home_away"] * home_away_prob)

            # Calculate H2H and last N games ratios
            h2h_ratio = calculate_over_ratio(opp_data, line_value, stat)  # Keeps {x / n} format

            # Convert ratios to decimal if possible; otherwise, keep original
            season_ratio_raw = calculate_over_ratio(player_data[player_data['Season'] == '2024-25'], line_value, stat)
            season_ratio = safe_eval_ratio(season_ratio_raw)

            last_n_ratios = calculate_ratios(player_data, stat, line_value)
            l5_ratio = safe_eval_ratio(last_n_ratios['L5'])
            l10_ratio = safe_eval_ratio(last_n_ratios['L10'])
            l20_ratio = safe_eval_ratio(last_n_ratios['L20'])

            prev_season_ratio_raw = calculate_over_ratio(player_data[player_data['Season'] == '2023-24'], line_value, stat)
            prev_season_ratio = safe_eval_ratio(prev_season_ratio_raw)

            all_ratio_raw = calculate_over_ratio(player_data, line_value, stat)
            all_ratio = safe_eval_ratio(all_ratio_raw)

            # Compile row and add to results
            result_row = {
                'Game': game_display,
                'Team': team,
                'Player': player_name,
                'PlayerID': player_id,
                'Opp': opp,
                'Type': stat_type,
                'Stat': stat,
                'Line': line_value,
                'Proj.': projected_value,
                'Diff.': difference,
                'Prob.': weighted_prob,
                '24-25': season_ratio,
                'H2H': h2h_ratio,
                'L5': l5_ratio,
                'L10': l10_ratio,
                'L20': l20_ratio,
                '23-24': prev_season_ratio,
                'All': all_ratio
            }
            final_results.append(result_row)

# Generate H2H pages
def sanitize_filename(filename):
    # Remove invalid characters
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def generate_h2h_pages(metrics_data, h2h_pairs, output_dir):
    h2h_dir = os.path.join(output_dir, 'h2h')
    os.makedirs(h2h_dir, exist_ok=True)

    for player_id, opp in h2h_pairs:
        # Filter the data for this player and opponent
        group = metrics_data[(metrics_data['PlayerID'] == player_id) & (metrics_data['Opp'] == opp)]
        if group.empty:
            continue
        player_name = group.iloc[0]['Player']
        opp_name = opp

        # Sanitize the filename
        filename = os.path.join(h2h_dir, sanitize_filename(f"{player_id}_vs_{opp}.html"))

        # Start HTML content
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{player_name} vs {opp_name} - Previous Matchups</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel=Stylesheet href=stylesheet.css>
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <script>
    document.addEventListener("DOMContentLoaded", async function () {{
        const searchBar = document.getElementById("search-bar");
        const searchResults = document.getElementById("search-results");

        let playerLinks = {{}};
        let teamLinks = {{}};

        // Load players and teams data from JSON files
        async function loadLinks() {{
            playerLinks = await fetch('players.json').then(response => response.json());
            teamLinks = await fetch('teams.json').then(response => response.json());
        }}

        await loadLinks();  // Ensure links are loaded before searching

        // Filter data and show suggestions based on input
        function updateSuggestions() {{
            const query = searchBar.value.trim().toLowerCase();
            searchResults.innerHTML = ""; // Clear previous results

            if (query === "") return;

            // Combine players and teams for search
            const combinedLinks = {{ ...playerLinks, ...teamLinks }};
            const matchingEntries = Object.entries(combinedLinks)
                .filter(([name]) => name.includes(query))  // Matches on both name and ID
                .slice(0, 5); // Limit to top 5

            matchingEntries.forEach(([name, url]) => {{
                const resultItem = document.createElement("div");
                resultItem.classList.add("suggestion");

                // Proper case for names
                resultItem.textContent = name.split(" ")
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(" ");

                resultItem.addEventListener("click", () => {{
                    window.open(url, "_self");
                }});
                searchResults.appendChild(resultItem);
            }});

            if (matchingEntries.length > 0) {{
                searchResults.style.display = "block"; // Show results if matches are found
            }} else {{
                const noResultItem = document.createElement("div");
                noResultItem.classList.add("no-result");
                noResultItem.textContent = "No results found.";
                searchResults.appendChild(noResultItem);
                searchResults.style.display = "block";
            }}
        }}
        
        document.addEventListener("click", function(event) {{
            if (!searchContainer.contains(event.target)) {{
                searchResults.style.display = "none";
            }}
        }});

        // Add event listener to search bar
        searchBar.addEventListener("input", updateSuggestions);
}});
    </script>
    
</head>
<body>
    <div class="topnav">
        <a href="/basketball/">Projections</a>
        <a href="/basketball/players/">Players</a>
        <a href="/basketball/boxscores/">Box Scores</a>
        <a href="/basketball/teams/">Teams</a>
        <a href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a>
    </div>
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search players and teams">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
    <div class="header">
        <h1>{player_name} vs {opp_name} - Previous Matchups</h1>
    </div>
    
    <div id="H2H-container">
    
    <div id="table-container">
        <table id="H2H-table">
        <caption class="caption"><a href="/basketball/players/{player_id}.html" target="_blank">{player_name}</a> H2H Results</caption>
        <thead>
            <tr>
                <th>Date</th>
                <th>Team</th>
                <th></th>
                <th>Opp</th>
                <th>PTS</th>
                <th>REB</th>
                <th>AST</th>
                <th>BLK</th>
                <th>STL</th>
                <th>TOV</th>
                <th>MP</th>
                <th>OffREB</th>
                <th>DefREB</th>
                <th>FG</th>
                <th>FGA</th>
                <th>3P</th>
                <th>3PA</th>
                <th>FT</th>
                <th>FTA</th>
                <th>PF</th>
                <th>BLK+STL</th>
                <th>REB+AST</th>
                <th>PTS+AST</th>
                <th>PTS+REB</th>
                <th>PTS+REB+AST
                <th>FANTASY</th>
            </tr>
        </thead>
        <tbody>
        '''

        # Add rows for each game
        for _, row in group.iterrows():
            # Convert date to MM/DD/YYYY format
            date_obj = datetime.strptime(str(row['Date']), "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%m/%d/%Y")
            game_id = row['GameID']  # Assumes 'GameID' column is present in your data
            
            # Create a hyperlink for the date
            date_link = f'<a href="/basketball/boxscores/{game_id}.html" target="_blank">{formatted_date}</a>'

            # Other row data
            team = row['Team']
            opp = row['Opp']
            pts = row['PTS']
            reb = row['REB']
            ast = row['AST']
            blk = row['BLK']
            stl = row['STL']
            tov = row['TOV']
            mp = f"{row['MP']:.2f}"
            offreb = row['OffREB']
            defreb = row['DefREB']
            fg = row['FG']
            fga = row['FGA']
            threep = row['3P']
            threepa = ['3PA']
            ft = row['FT']
            fta= row['FTA']
            pf = row['PF']
            bs = row['BLK_STL']
            ra = row['REB_AST']
            pa = row['PTS_AST']
            pr = row['PTS_REB']
            pra = row['PTS_REB_AST']
            fant = row['FANTASY']

            

            html_content += f'''
            <tr>
                <td>{date_link}</td>
                <td><a href="/basketball/teams/{team}.html" target="_blank">{team}</a></td>
                <td>{'vs' if row['Is_Home'] == 1 else '@'}</td>
                <td><a href="/basketball/teams/{opp}.html" target="_blank">{opp}</a></td>
                <td>{pts}</td>
                <td>{reb}</td>
                <td>{ast}</td>
                <td>{blk}</td>
                <td>{stl}</td>
                <td>{tov}</td>
                <td>{mp}</td>
                <td>{offreb}</td>
                <td>{defreb}</td>
                <td>{fg}</td>
                <td>{fga}</td>
                <td>{threep}</td>
                <td>{threepa}</td>
                <td>{ft}</td>
                <td>{fta}</td>
                <td>{pf}</td>
                <td>{bs}</td>
                <td>{ra}</td>
                <td>{pa}</td>
                <td>{pr}</td>
                <td>{pra}</td>
                <td>{fant}</td>
            </tr>
            '''

        # Close HTML content
        html_content += '''
        </tbody>
        </table>
    </div>
    </div>
</body>
</html>
        '''

        # Write the HTML content to file
        with open(filename, 'w') as f:
            f.write(html_content)

    print("H2H pages created successfully.")

# Call the function to generate H2H pages
generate_h2h_pages(metrics_data, h2h_pairs, os.path.dirname(output_file_path))

# Convert results to HTML format with specified JavaScript functionality
with open(output_file_path, 'w') as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Basketball!</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel=Stylesheet href=stylesheet.css>
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <script src="players.json"></script>
    <script src="teams.json"></script>

<script>
document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("data-table");
    const headerRow = table.querySelector("thead tr:first-child");
    const rows = Array.from(table.querySelectorAll("tbody tr"));
    const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
    const clearAllButton = document.getElementById("clear-all-btn");
    const clearButton = document.getElementById("clear-filters-btn");
    let showSelectedOnly = false;
    let isDragging = false;

    // Explicitly set the index of the "Prob." column (adjust if necessary)
    const probColumnIndex = 8;

    // Add checkboxes to the header row
    const checkboxHeader = document.createElement("th");
    checkboxHeader.style.width = "38px";
    checkboxHeader.textContent = "";
    headerRow.prepend(checkboxHeader);

    // Add checkboxes to each row in the table
    rows.forEach(row => {
        const checkboxCell = document.createElement("td");
        checkboxCell.style.width = "38px";
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.classList.add("event-checkbox");

        // Get probability from "Prob." column and store it as a data attribute
        const probText = row.cells[probColumnIndex].textContent.trim();
        const probValue = parseFloat(probText);
        checkbox.dataset.prob = probValue;

        checkboxCell.appendChild(checkbox);
        row.prepend(checkboxCell);

        // Recalculate combined probability when a checkbox is checked or unchecked
        checkbox.addEventListener("change", calculateCombinedProbability);
    });

    // Calculate combined probability for selected rows
    function calculateCombinedProbability() {
        const checkboxes = document.querySelectorAll(".event-checkbox:checked");
        let combinedProbability = 1;

        checkboxes.forEach(checkbox => {
            const prob = parseFloat(checkbox.dataset.prob);
            combinedProbability *= prob;
        });

        document.getElementById("result").textContent = `Combined Probability: ${(combinedProbability * 100).toFixed(2)}%`;
    }

    // Multi-row selection by dragging
    rows.forEach(row => {
        row.addEventListener("mousedown", function () {
            isDragging = true;
            toggleRowSelection(row);
        });

        row.addEventListener("mouseenter", function () {
            if (isDragging) toggleRowSelection(row);
        });

        row.addEventListener("mouseup", () => isDragging = false);
    });

    document.addEventListener("mouseup", () => isDragging = false);

    // Toggle selection for individual rows
    function toggleRowSelection(row) {
        row.classList.toggle("selected-row");
    }

    // Show only selected rows or all rows
    toggleSelectionBtn.addEventListener("click", () => {
        showSelectedOnly = !showSelectedOnly;
        if (showSelectedOnly) {
            rows.forEach(row => {
                row.style.display = row.classList.contains("selected-row") ? "" : "none";
            });
            toggleSelectionBtn.textContent = "Show All";
        } else {
            rows.forEach(row => (row.style.display = ""));
            toggleSelectionBtn.textContent = "Show Selected Only";
        }
    });

    // Add sorting to each header
    addSortToHeaders(table);

    function addSortToHeaders(table) {
        const headers = table.querySelectorAll("thead th");
        headers.forEach((header, index) => {
            header.style.cursor = "pointer";
            header.addEventListener("click", function () {
                sortTable(table, index);
            });
        });
    }

    // Sort the table by column
    function sortTable(table, columnIndex) {
        const rows = Array.from(table.querySelectorAll("tbody tr"));
        const isNumeric = rows.every(row => !isNaN(row.cells[columnIndex].textContent.trim()));
        const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
        table.dataset.sortDirection = direction;

        rows.sort((a, b) => {
            const cellA = a.cells[columnIndex].textContent.trim();
            const cellB = b.cells[columnIndex].textContent.trim();

            const valA = isNumeric ? parseFloat(cellA) : cellA.toLowerCase();
            const valB = isNumeric ? parseFloat(cellB) : cellB.toLowerCase();

            return direction === "asc" ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
        });

        rows.forEach(row => table.querySelector("tbody").appendChild(row));
    }

    // Add filters
    addFilters(table);

    function addFilters(table) {
        const filterColumns = ["Game", "Team", "Type", "Stat"];
        const filterHeaders = Array.from(table.querySelectorAll("thead th"));
        const filterIndexes = filterColumns.map(col => filterHeaders.findIndex(header => header.textContent.trim() === col));

        filterColumns.forEach((colName, i) => {
            const index = filterIndexes[i];
            const values = Array.from(new Set(
                Array.from(table.querySelectorAll(`tbody tr td:nth-child(${index + 1})`))
                .map(cell => cell.textContent.trim())
            )).sort();

            // For each value, create a checkbox
            const filterDiv = document.getElementById(`${colName.toLowerCase()}-filters`);
            if (filterDiv) {
                filterDiv.innerHTML = "";
                const allLabel = document.createElement('label');
                const allCheckbox = document.createElement('input');
                allCheckbox.type = 'checkbox';
                allCheckbox.classList.add(`${colName.toLowerCase()}-filter-all`);
                allCheckbox.checked = true;
                allLabel.appendChild(allCheckbox);
                allLabel.appendChild(document.createTextNode("All"));
                filterDiv.appendChild(allLabel);

            // Event listener to check/uncheck all checkboxes in this category
            allCheckbox.addEventListener('change', function () {
                const isChecked = allCheckbox.checked;
                document.querySelectorAll(`.${colName.toLowerCase()}-filter`).forEach(checkbox => {
                    checkbox.checked = isChecked;
                });
                filterTable(); // Update table display based on new filter states
            });

                
                values.forEach(value => {
                    const label = document.createElement('label');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.value = value;
                    checkbox.checked = true;
                    checkbox.classList.add(`${colName.toLowerCase()}-filter`);
                    label.appendChild(checkbox);
                    label.appendChild(document.createTextNode(value));
                    filterDiv.appendChild(label);

                    // Add event listener to the checkbox
                    checkbox.addEventListener('change', () => {
                    // If any checkbox in the group is unchecked, uncheck the "All" checkbox
                    if (!checkbox.checked) {
                        allCheckbox.checked = false;
                    } else {
                        // Check if all individual boxes are selected to set "All" checkbox
                        const allSelected = Array.from(document.querySelectorAll(`.${colName.toLowerCase()}-filter`))
                            .every(cb => cb.checked);
                        allCheckbox.checked = allSelected;
                    }
                    filterTable();
                });
            });
        } else {
            console.error(`Filter div with ID ${colName.toLowerCase()}-filters not found.`);
        }
    });
}
        

    // Filter table based on selected filters
    function filterTable() {
        const filterColumns = ["Game", "Team", "Type", "Stat"];
        const filterClasses = ["game-filter", "team-filter", "type-filter", "stat-filter"];
        const filterHeaders = Array.from(table.querySelectorAll("thead th"));
        const filterIndexes = filterColumns.map(col => filterHeaders.findIndex(header => header.textContent.trim() === col));

        const filters = filterClasses.map(cls => {
            const checkboxes = document.querySelectorAll(`.${cls}:checked`);
            return Array.from(checkboxes).map(cb => cb.value);
        });
		
		const showSelectedOnly = toggleSelectionBtn.textContent === "Show All"; // Check if "Show Selected Only" mode is active

        rows.forEach(row => {
            const cells = Array.from(row.cells);
            let matchesFilter = true;
			
			for (let i = 0; i < filters.length; i++) {
				const filterValues = filters[i];
				const cellValue = cells[filterIndexes[i]].textContent.trim();

				if (filterValues.length === 0) {
                // No checkboxes checked in this category; no rows should match
					matchesFilter = false;
					break;
				} else if (!filterValues.includes(cellValue)) {
                // Cell value does not match any selected filter values
					matchesFilter = false;
					break;
            }
        }
		
		if (matchesFilter && (!showSelectedOnly || row.classList.contains("selected-row"))) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

    // "Clear Filters" button functionality
    clearButton.addEventListener("click", () => {
        const filterClasses = ["game-filter", "team-filter", "type-filter", "stat-filter"];
        filterClasses.forEach(cls => {
            document.querySelectorAll(`.${cls}`).forEach(checkbox => checkbox.checked = true);
        });
        filterTable();
    });

    // "Clear All" functionality
    clearAllButton.addEventListener("click", () => {
        // Uncheck all event checkboxes
        document.querySelectorAll(".event-checkbox").forEach(checkbox => checkbox.checked = false);

        // Reset filters
        const filterClasses = ["game-filter", "team-filter", "type-filter", "stat-filter"];
        filterClasses.forEach(cls => {
            document.querySelectorAll(`.${cls}`).forEach(checkbox => checkbox.checked = true);
        });

        rows.forEach(row => {
            row.classList.remove("selected-row");
            row.style.display = "";
        });
        toggleSelectionBtn.textContent = "Show Selected Only";
        showSelectedOnly = false;
        
        calculateCombinedProbability();
        filterTable();
    });

    // Gradient color code...
    const gradientColumns = ["Diff.", "Prob.", "24-25", "L5", "L10", "L20", "23-24", "All"];

    // Get column indexes based on column headers
    const headers = Array.from(table.querySelectorAll("thead th"));
    const columnIndexes = gradientColumns.map(col => headers.findIndex(header => header.textContent.trim() === col));

    // Get min and max values for each column
    const minMaxValues = columnIndexes.map(index => {
        let values = Array.from(table.querySelectorAll(`tbody tr td:nth-child(${index + 1})`))
            .map(cell => parseFloat(cell.textContent))
            .filter(value => !isNaN(value));

        return {
            min: Math.min(...values),
            max: Math.max(...values)
        };
    });

    // Apply gradient color based on value
    table.querySelectorAll("tbody tr").forEach(row => {
        columnIndexes.forEach((index, i) => {
            if (index >= 0) {
                const cell = row.cells[index];
                const value = parseFloat(cell.textContent);
                const { min, max } = minMaxValues[i];

                if (!isNaN(value)) {
                    // Adjust color for each value based on column min-max range
                    const color = getGradientColor(value, min, max);
                    cell.style.backgroundColor = color;
                    cell.style.color = "#000"; // Ensures text is readable
                }
            }
        });
    });

    // Helper function to get gradient color
    function getGradientColor(value, min, max) {
        // Normalize value within the range for the column
        let normalized = (value - min) / (max - min);
        normalized = Math.max(0, Math.min(1, normalized)); // Clamps the value between 0 and 1

        // Color blend from red (low values) to green (high values)
        const red = normalized < 0.5 ? 255 : Math.floor(255 * (1 - normalized) * 2);
        const green = normalized > 0.5 ? 255 : Math.floor(255 * normalized * 2);
        const blue = 255 * (1 - Math.abs(normalized - 0.5) * 2); // Blend through white

        return `rgb(${red}, ${green}, ${blue})`;
    }
});

    document.addEventListener("DOMContentLoaded", async function () {
        const searchBar = document.getElementById("search-bar");
        const searchResults = document.getElementById("search-results");

        let playerLinks = {};
        let teamLinks = {};

        // Load players and teams data from JSON files
        async function loadLinks() {
            playerLinks = await fetch('players.json').then(response => response.json());
            teamLinks = await fetch('teams.json').then(response => response.json());
        }

        await loadLinks();  // Ensure links are loaded before searching

        // Filter data and show suggestions based on input
        function updateSuggestions() {
            const query = searchBar.value.trim().toLowerCase();
            searchResults.innerHTML = ""; // Clear previous results

            if (query === "") return;

            // Combine players and teams for search
            const combinedLinks = { ...playerLinks, ...teamLinks };
            const matchingEntries = Object.entries(combinedLinks)
                .filter(([name]) => name.includes(query))  // Matches on both name and ID
                .slice(0, 5); // Limit to top 5

            matchingEntries.forEach(([name, url]) => {
                const resultItem = document.createElement("div");
                resultItem.classList.add("suggestion");

                // Proper case for names
                resultItem.textContent = name.split(" ")
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(" ");

                resultItem.addEventListener("click", () => {
                    window.open(url, "_self");
                });
                searchResults.appendChild(resultItem);
            });

            if (matchingEntries.length > 0) {
                searchResults.style.display = "block"; // Show results if matches are found
            } else {
                const noResultItem = document.createElement("div");
                noResultItem.classList.add("no-result");
                noResultItem.textContent = "No results found.";
                searchResults.appendChild(noResultItem);
                searchResults.style.display = "block";
            }
        }
        
        document.addEventListener("click", function(event) {
            if (!searchContainer.contains(event.target)) {
                searchResults.style.display = "none";
            }
        });

        // Add event listener to search bar
        searchBar.addEventListener("input", updateSuggestions);
    });
    </script>
</head>
<body>
    <div class="topnav">
        <a href="/basketball/">Projections</a>
        <a href="/basketball/players/">Players</a>
        <a href="/basketball/boxscores/">Box Scores</a>
        <a href="/basketball/teams/">Teams</a>
        <a href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a>
    </div>
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for a player or team...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>

    
    <div class="header">
        <h1>Today's Probabilities and Projections</h1>
    </div>

	<button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>
    
    <div id="multi-filters">
        <table class="multi-filters">
            <tr><td style="width:8%;font-weight:700">Games:</td><td><div id="game-filters"></div></td></tr>
            <tr><td style="width:8%;font-weight:700">Teams:</td><td><div id="team-filters"></div></td></tr>
            <tr><td style="width:8%;font-weight:700">Types:</td><td><div id="type-filters"></div></td></tr>
            <tr><td style="width:8%;font-weight:700">Stats:</td><td><div id="stat-filters"></div></td></tr>
        </table>
    </div>
    
    <div><p style="width:95%; margin:auto;">Click the Checkboxes Below to Calculate the Combined Probability</p>
        <div id="result-container">
            <div id="result">Combined Probability:</div>
        </div>
        <div class="button-container">
            <button id="toggle-selection-btn">Show Selected Only</button>
            <button id="clear-filters-btn">Remove Filters</button>
            <button id="clear-all-btn">Clear All</button>
        </div>
    </div>

    <div id="data-table-container">
        <table id="data-table">
        <thead>
            <tr>
                <th>Game</th>
                <th>Team</th>
                <th>Player</th>
                <th>Type</th>
                <th>Stat</th>
                <th>Line</th>
                <th>Proj.</th>
                <th>Diff.</th>
                <th>Prob.</th>
                <th>24-25</th>
                <th>H2H</th>
                <th>L5</th>
                <th>L10</th>
                <th>L20</th>
                <th>23-24</th>
                <th>All</th>
            </tr>
        </thead>
        <tbody>
    """)

    # Adjust your code to loop through final_results as dictionaries
    for row in final_results:
        projected_value = f"{row['Proj.']:.2f}"
        difference = f"{row['Diff.']:.2f}"
        weighted_prob = f"{row['Prob.']:.2f}"
        
        # Create links
        player_link = f'<a href="/basketball/players/{row["PlayerID"]}.html" target="_blank">{row["Player"]}</a>'
        team_link = f'<a href="/basketball/teams/{row["Team"]}.html" target="_blank">{row["Team"]}</a>'
        h2h_link = f'<a href="/basketball/h2h/{row["PlayerID"]}_vs_{row["Opp"]}.html" target="_blank">'
        h2h_cell = f'{h2h_link}{row["H2H"]}</a>'
        
        # Write the row
        f.write("<tr>")
        f.write(f"<td>{row['Game']}</td>")
        f.write(f"<td>{team_link}</td>")
        f.write(f"<td>{player_link}</td>")
        f.write(f"<td>{row['Type']}</td>")
        f.write(f"<td>{row['Stat']}</td>")
        f.write(f"<td>{row['Line']}</td>")
        f.write(f"<td>{projected_value}</td>")
        f.write(f"<td>{difference}</td>")
        f.write(f"<td>{weighted_prob}</td>")
        f.write(f"<td>{row['24-25']}</td>")
        f.write(f"<td>{h2h_cell}</td>")
        f.write(f"<td>{row['L5']}</td>")
        f.write(f"<td>{row['L10']}</td>")
        f.write(f"<td>{row['L20']}</td>")
        f.write(f"<td>{row['23-24']}</td>")
        f.write(f"<td>{row['All']}</td>")
        f.write("</tr>")
    
    f.write("""
        </tbody>
        </table>
    </div>
    <div class="footer"></div>
</body>
</html>
        """)

    print(f"HTML output saved to: {output_file_path}")
