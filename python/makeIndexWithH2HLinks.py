import pandas as pd
import os
import re
from datetime import datetime
from tqdm import tqdm
import numpy as np

# File paths
metrics_file_path = r"C:\Users\ashle\Documents\Projects\basketball\data\gamelogs.csv"
upcoming_games_path = r"C:\Users\ashle\Documents\Projects\basketball\data\games_thisWeek.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\basketball\index.html"

# Load data
metrics_data = pd.read_csv(metrics_file_path, parse_dates=["Date"], low_memory=False)
upcoming_games_data = pd.read_csv(upcoming_games_path, low_memory=False)

# Convert relevant columns to numeric types
metrics_data[['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV']] = metrics_data[['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV']].apply(pd.to_numeric, errors='coerce')

# Map GameID to Game
game_mapping = upcoming_games_data.set_index('GameID')['Game'].to_dict()

# Define weighted projection function based on opponent and home/away stats
def calculate_weighted_projection(player_data, stat, opp, is_home):
    opp_stats = player_data[player_data['Opp'] == opp][stat].mean() if not player_data[player_data['Opp'] == opp].empty else 0
    home_away_stats = player_data[player_data['Is_Home'] == is_home][stat].mean() if not player_data[player_data['Is_Home'] == is_home].empty else 0
    return round(0.8 * opp_stats + 0.2 * home_away_stats, 2)

# Calculate last N games
def calculate_last_n_games(player_data, stat, n):
    recent_games = player_data.sort_values(by='Date', ascending=False).head(n)
    return round(recent_games[stat].mean() if not recent_games.empty else 0, 2)

# Helper function to calculate season averages
def calculate_season_average(player_data, stat, season):
    return round(player_data[player_data['Season'] == season][stat].mean() if not player_data[player_data['Season'] == season].empty else 0, 2)

# Collect unique player-opponent pairs for H2H
h2h_pairs = set()

# Define the stats we're interested in
stats_to_project = ['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV']

# Process each upcoming game
final_results = []
for _, game in tqdm(upcoming_games_data.iterrows(), total=upcoming_games_data.shape[0]):
    player_id = game['PlayerID']
    team = game['Team']
    opp = game['Opp']
    game_id = game['GameID']
    game_display = game_mapping.get(game_id, game_id)
    is_home = game['Is_Home']
    
    h2h_pairs.add((player_id, opp))
    player_data = metrics_data[metrics_data['PlayerID'] == player_id]
    
    for stat in stats_to_project:
        proj = calculate_weighted_projection(player_data, stat, opp, is_home)
        
        stat_L5 = calculate_last_n_games(player_data, stat, 5)
        stat_L10 = calculate_last_n_games(player_data, stat, 10)
        stat_L20 = calculate_last_n_games(player_data, stat, 20)
        stat_2023_24 = calculate_season_average(player_data, stat, '2023-24')
        stat_2024_25 = calculate_season_average(player_data, stat, '2024-25')
        stat_H2H = round(player_data[player_data['Opp'] == opp][stat].mean() if not player_data[player_data['Opp'] == opp].empty else 0, 2)
        stat_all = round(player_data[stat].mean() if not player_data.empty else 0, 2)
        
        result_row = {
            'Game': game_display,
            'Team': f'<a href="/basketball/teams/{team}.html" target="_blank">{team}</a>',
            'Player': f'<a href="/basketball/players/{player_id}.html" target="_blank">{game["Player"]}</a>',
            'Stat': stat,
            'Proj.': proj,
            '2024-25': stat_2024_25,
            'H2H': stat_H2H,
            'L5': stat_L5,
            'L10': stat_L10,
            'L20': stat_L20,
            '2023-24': stat_2023_24,
            'All': stat_all
        }
        final_results.append(result_row)

# Function to sanitize filenames
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Generate H2H pages
def generate_h2h_pages(metrics_data, h2h_pairs, output_dir):
    h2h_dir = os.path.join(output_dir, 'h2h')
    os.makedirs(h2h_dir, exist_ok=True)

    for player_id, opp in h2h_pairs:
        group = metrics_data[(metrics_data['PlayerID'] == player_id) & (metrics_data['Opp'] == opp)]
        if group.empty:
            continue
        player_name = group.iloc[0]['Player']
        opp_name = opp
        filename = os.path.join(h2h_dir, sanitize_filename(f"{player_id}_vs_{opp}.html"))

        # Generate HTML content for each H2H page
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{player_name} vs {opp_name} - Previous Matchups</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel=Stylesheet href=stylesheet.css>
    <link rel="icon" type="image/x-icon" href="/baskeball/images/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
</head>
    
</head>
<body>
    <div class="topnav">
        <a href="/basketball/">Projections</a>
        <a href="/basketball/players/">Players</a>
        <a href="/basketball/boxscores/">Box Scores</a>
        <a href="/basketball/teams/">Teams</a>
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
                <th>Date</th><th>Team</th><th></th><th>Opp</th><th>PTS</th><th>REB</th>
                <th>AST</th><th>BLK</th><th>STL</th><th>TOV</th>
            </tr>
        </thead>
        <tbody>
        '''
        
        # Add rows for each game
        for _, row in group.iterrows():
            formatted_date = row['Date'].strftime("%m/%d/%Y")
            game_id = row['GameID']
            date_link = f'<a href="/basketball/boxscores/{game_id}.html" target="_blank">{formatted_date}</a>'
            html_content += f'''
            <tr>
                <td>{date_link}</td>
                <td><a href="/basketball/teams/{row["Team"]}.html" target="_blank">{row["Team"]}</a></td>
                <td>{'vs' if row['Is_Home'] == 1 else '@'}</td>
                <td><a href="/basketball/teams/{opp}.html" target="_blank">{opp}</a></td>
                <td>{row['PTS']}</td>
                <td>{row['REB']}</td>
                <td>{row['AST']}</td>
                <td>{row['BLK']}</td>
                <td>{row['STL']}</td>
                <td>{row['TOV']}</td>
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
        
        # Write HTML content to file
        with open(filename, 'w') as f:
            f.write(html_content)

    print("H2H pages created successfully.")

# Call the function to generate H2H pages
generate_h2h_pages(metrics_data, h2h_pairs, os.path.dirname(output_file_path))

# Save main table as HTML
columns = ['Game', 'Team', 'Player', 'Stat', 'Proj.', '2024-25', 'H2H', 'L5', 'L10', 'L20', '2023-24', 'All']
final_df = pd.DataFrame(final_results, columns=columns)
final_df.to_html(output_file_path, index=False)
print(f"HTML output saved to: {output_file_path}")


# Convert results to HTML format with specified JavaScript functionality
with open(output_file_path, 'w') as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Basketball!</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel=Stylesheet href=stylesheet.css>
    <link rel="icon" type="image/x-icon" href="/basketball/images/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">

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
        const filterColumns = ["Game", "Team", "Stat"];
        const filterClasses = ["game-filter", "team-filter", "stat-filter"];
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
        const filterClasses = ["game-filter", "team-filter", "stat-filter"];
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
        const filterClasses = ["game-filter", "team-filter", "stat-filter"];
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
});
</script>
</head>
<body>
    <div class="topnav">
        <a href="/basketball/">Projections</a>
        <a href="/basketball/players/">Players</a>
        <a href="/basketball/boxscores/">Box Scores</a>
        <a href="/basketball/teams/">Teams</a>
    </div>    
    <div class="header">
        <h1>Today's Probabilities and Projections</h1>
    </div>

	<button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>
    
    <div id="multi-filters">
        <table class="multi-filters">
            <tr><td style="width:8%;font-weight:700">Games:</td><td><div id="game-filters"></div></td></tr>
            <tr><td style="width:8%;font-weight:700">Teams:</td><td><div id="team-filters"></div></td></tr>
            <tr><td style="width:8%;font-weight:700">Stats:</td><td><div id="stat-filters"></div></td></tr>
        </table>
    </div>
    
    <div>       
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
                <th>Stat</th>
                <th>Proj.</th>
                <th>2024-25</th>
                <th>H2H</th>
                <th>L5</th>
                <th>L10</th>
                <th>L20</th>
                <th>2023-24</th>
                <th>All</th>
            </tr>
        </thead>
        <tbody>
    """)

    # Adjust your code to loop through final_results as dictionaries
    for row in final_results:
        projected_value = f"{row['Proj.']:.2f}"
        
        # Create links
        player_link = row['Player']  # Already contains the HTML link in 'final_results'
        team_link = row['Team']      # Already contains the HTML link in 'final_results'
        h2h_cell = row['H2H']  
        
        # Write the row
        f.write("<tr>")
        f.write(f"<td>{row['Game']}</td>")
        f.write(f"<td>{team_link}</td>")
        f.write(f"<td>{player_link}</td>")
        f.write(f"<td>{row['Stat']}</td>")
        f.write(f"<td>{projected_value}</td>")
        f.write(f"<td>{row['2024-25']}</td>")
        f.write(f"<td>{h2h_cell}</td>")
        f.write(f"<td>{row['L5']}</td>")
        f.write(f"<td>{row['L10']}</td>")
        f.write(f"<td>{row['L20']}</td>")
        f.write(f"<td>{row['2023-24']}</td>")
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
