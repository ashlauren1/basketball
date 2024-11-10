import pandas as pd
from tqdm import tqdm

# File paths
metrics_file_path = r"C:\Users\ashle\Documents\Projects\hockey\data\gamelogs.csv"
upcoming_games_path = r"C:\Users\ashle\Documents\Projects\hockey\data\games_thisWeek.csv"
lines_file_path = r"C:\Users\ashle\Documents\Projects\hockey\data\todayLines.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\hockey\index.html"

# Load data
metrics_data = pd.read_csv(metrics_file_path,  parse_dates=["Date"], low_memory=False)
upcoming_games_data = pd.read_csv(upcoming_games_path, low_memory=False)
lines_data = pd.read_csv(lines_file_path)

# Convert relevant columns to numeric types to avoid type errors
metrics_data[['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK']] = metrics_data[['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK']].apply(pd.to_numeric, errors='coerce')
metrics_data['TOI'] = pd.to_numeric(metrics_data['TOI'], errors='coerce')

# Create a dictionary mapping GameID to Game
game_mapping = upcoming_games_data.set_index('GameID')['Game'].to_dict()

# Filter for players in lines.csv
lines_players = lines_data['PlayerID'].unique()
metrics_data = metrics_data[metrics_data['PlayerID'].isin(lines_players)]
upcoming_games_data = upcoming_games_data[upcoming_games_data['PlayerID'].isin(lines_players)]

# Functions to calculate averages and ratios
def calculate_average_stats(group):
    return {stat: group[stat].mean() for stat in ['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK', 'TOI']}

def calculate_over_ratio(filtered_data, line, stat):
    over_count = (filtered_data[stat] > line).sum()
    total_games = len(filtered_data)
    return f"{over_count}/{total_games}" if total_games > 0 else "0/0"

# Aggregated stats
player_home_stats = metrics_data[metrics_data['Is_Home'] == 1].groupby('PlayerID').apply(calculate_average_stats).to_dict()
player_away_stats = metrics_data[metrics_data['Is_Home'] == 0].groupby('PlayerID').apply(calculate_average_stats).to_dict()
player_vs_opp_stats = metrics_data.groupby(['PlayerID', 'Opp']).apply(calculate_average_stats).to_dict()

team_home_stats = metrics_data[metrics_data['Is_Home'] == 1].groupby('Team').apply(calculate_average_stats).to_dict()
team_away_stats = metrics_data[metrics_data['Is_Home'] == 0].groupby('Team').apply(calculate_average_stats).to_dict()
team_vs_opp_stats = metrics_data.groupby(['Team', 'Opp']).apply(calculate_average_stats).to_dict()

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
        return home_away_stats or opp_stats or {stat: 0 for stat in ['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK', 'TOI']}
    else:
        player_weighted_stats = {k: (0.8 * opp_stats[k] + 0.2 * home_away_stats[k]) for k in opp_stats} if home_away_stats and opp_stats else home_away_stats or opp_stats or {stat: 0 for stat in ['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK', 'TOI']}
        team_weighted_stats = {k: (0.8 * team_opp_stats[k] + 0.2 * team_home_away_stats[k]) for k in team_opp_stats} if team_home_away_stats and team_opp_stats else team_home_away_stats or team_opp_stats or {stat: 0 for stat in ['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK', 'TOI']}
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

# Generate final results
final_results = []
columns = ['Game', 'Team', 'Player', 'Type', 'Stat', 'Line', 'Proj.', 'Diff.', 'Prob.', '2024-25', 'H2H', 'L5', 'L10', 'L20', '2023-24', 'All']

# Process each game
# Calculate ratios and difference values within the game processing loop
for _, game in tqdm(upcoming_games_data.iterrows(), total=upcoming_games_data.shape[0]):
    player_id = game['PlayerID']
    team = game['Team']
    is_home = game['Is_Home']
    opp = game['Opp']
    game_id = game['GameID']
    
    game_display = game_mapping.get(game_id, game_id)
    
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
            result_row = [
                game_display, team, player_name, player_id, stat_type, stat, line_value,
                projected_value, difference, weighted_prob, season_ratio,
                h2h_ratio, l5_ratio, l10_ratio, l20_ratio, prev_season_ratio, all_ratio
            ]
            final_results.append(result_row)


# Convert results to HTML format with specified JavaScript functionality
with open(output_file_path, 'w') as f:
    f.write("""
    <!DOCTYPE html>
<html>
<head>
<title>Hockey!</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel=Stylesheet href=stylesheet.css>
<link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">

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
                    checkbox.addEventListener('change', filterTable);
                });
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
    const gradientColumns = ["Diff.", "Prob.", "2024-25", "L5", "L10", "L20", "2023-24", "All"];

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
</script>
</head>
<body>
    <div class="topnav">
        <a href="/hockey/">Projections</a>
        <a href="/hockey/players/">Players</a>
        <a href="/hockey/boxscores/">Box Scores</a>
        <a href="/hockey/teams/">Teams</a>
    </div>    
    <div class="header">
        <h1>Today's Probabilities and Projections</h1>
    </div>

	<button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>

    <div id="multi-filters">
        <div id="game-filters"><p>Games:</p></div>
        <div id="team-filters"><p>Teams:</p></div>
        <div id="type-filters"><p>Types:</p></div>
        <div id="stat-filters"><p>Stats:</p></div>
    </div>

    
    <div><p style="width:95%; margin: auto;">Click the Checkboxes Below to Calculate the Combined Probability</p>
        <div id="result-container">
            <div id="result">
				Combined Probability:
            </div>
        </div>
        <div class="button-container">
            <button id="toggle-selection-btn">Show Selected Only</button>
            <button id="clear-filters-btn">Remove Filters</button>
            <button id="clear-all-btn">Clear All</button>
        </div>
    </div>

<div id="data-table-container">
<table id="data-table">

<colgroup>
<col style="width:38px">
<col style="width:90px">
<col style="width:48px">
<col style="width:164px">
<col span="3" style="width:48px">
<col span="10" style="width:68px">
</colgroup>
        <thead>
            <tr>
                <th>Game</th><th>Team</th><th>Player</th><th>Type</th><th>Stat</th><th>Line</th>
                <th>Proj.</th><th>Diff.</th><th>Prob.</th><th>2024-25</th><th>H2H</th>
                <th>L5</th><th>L10</th><th>L20</th><th>2023-24</th><th>All</th>
            </tr>
</thead>
<tbody>
    """)

# Write table rows from data with formatting and links
    for row in final_results:
        game_display, team, player_name, player_id, stat_type, stat, line_value, projected_value, difference, weighted_prob, season_ratio, h2h_ratio, l5_ratio, l10_ratio, l20_ratio, prev_season_ratio, all_ratio = row
    
    # Format numeric values to two decimal places where applicable
        projected_value = f"{projected_value:.2f}"
        difference = f"{difference:.2f}"
        weighted_prob = f"{weighted_prob:.2f}"
    
    # Create links for Player and Team columns
        player_link = f'<a href="/hockey/players/{player_id}.html" target="_blank">{player_name}</a>'
        team_link = f'<a href="/hockey/teams/{team}.html" target="_blank">{team}</a>'
    
    # Write the row with formatted values
        f.write("<tr>")
        f.write(f"<td>{game_display}</td>")
        f.write(f"<td>{team_link}</td>")
        f.write(f"<td>{player_link}</td>")
        f.write(f"<td>{stat_type}</td>")
        f.write(f"<td>{stat}</td>")
        f.write(f"<td>{line_value}</td>")
        f.write(f"<td>{projected_value}</td>")
        f.write(f"<td>{difference}</td>")
        f.write(f"<td>{weighted_prob}</td>")
        f.write(f"<td>{season_ratio}</td>")
        f.write(f"<td>{h2h_ratio}</td>")
        f.write(f"<td>{l5_ratio}</td>")
        f.write(f"<td>{l10_ratio}</td>")
        f.write(f"<td>{l20_ratio}</td>")
        f.write(f"<td>{prev_season_ratio}</td>")
        f.write(f"<td>{all_ratio}</td>")
        f.write("</tr>")
    
    f.write("""
    </tbody>
    </table>
    <div class="footer"></div>
    </div>
    </body>
    </html>
        """)

print(f"HTML output saved to: {output_file_path}")

