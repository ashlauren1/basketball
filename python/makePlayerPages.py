import pandas as pd
import os
from datetime import datetime

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\basketball\data"
output_dir = r"C:\Users\ashle\Documents\Projects\basketball\players"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# **Load Data**
roster_csv = os.path.join(data_dir, "rosters.csv")
gamelogs_csv = os.path.join(data_dir, "gamelogs.csv")
leaders_csv = os.path.join(data_dir, "leaders.csv")

# Load roster data
roster_data = pd.read_csv(roster_csv)
roster_data.sort_values(by=["Team", "Player"], inplace=True)

# Load gamelogs data
gamelogs_data = pd.read_csv(gamelogs_csv).sort_values(by=["PlayerID", "Date"], ascending=[True, False])

leader_data = pd.read_csv(leaders_csv)

# **Part 1: Generate Player Directory (index.html)**
def create_player_directory(roster_data, output_file_path):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <script src="modalsMobileNavAndSearch.js"></script>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="stylesheet" href="commonStylesheet.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <title>Player Directory</title>
<script>
document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("player-index");
    const headerRow = table.querySelector("thead tr:first-child");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

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

            if (valA < valB) {
                return direction === "asc" ? -1 : 1;
            } else if (valA > valB) {
                return direction === "asc" ? 1 : -1;
            } else {
                return 0;
            }
        });

        rows.forEach(row => table.querySelector("tbody").appendChild(row));
    }
});

document.addEventListener("DOMContentLoaded", async function () {
    const searchBar = document.getElementById("search-bar");
    const searchResults = document.getElementById("search-results");
    const searchButton = document.getElementById("search-button");

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
            .filter(([name]) => name.toLowerCase().includes(query))  // Matches on both name and ID
            .slice(0, 10); // Limit to top 10


        matchingEntries.forEach(([name, url]) => {
            const resultItem = document.createElement("div");
            resultItem.classList.add("suggestion");

            // Proper case for names
            resultItem.textContent = name;

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
    if (!searchResults.contains(event.target) && event.target !== searchBar) {
        searchResults.style.display = "none";
    }
});

// Add event listener to search bar
searchBar.addEventListener("input", updateSuggestions);

function redirectToSearchResults() {
    const query = searchBar.value.trim().toLowerCase();;
    if (query) {
        window.location.href = `/basketball/search_results.html?query=${encodeURIComponent(query)}`;
    }
}

// Add event listeners for search
searchBar.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        redirectToSearchResults();
    }
});

searchButton.addEventListener("click", redirectToSearchResults);
});

</script>

</head>
<body>
<div id="mobileTopnav">
    <div class="menuBarContainer mobile active">
        <a href="javascript:void(0);" class="icon" onclick="myFunction()"><i class="fa fa-bars"></i>Menu</a>
    </div>
    <div id="myLinks">
        <ul class="navLinks">
            <li class="nav-link"><a href="/basketball/" target="_blank">Projections</a></li>
            <li class="nav-link"><a href="/basketball/players/" target="_blank">Players</a></li>
            <li class="nav-link"><a href="/basketball/teams/" target="_blank">Teams</a></li>
            <li class="nav-link"><a href="/basketball/leaders/" target="_blank">Leaders</a></li>
            <li class="nav-link"><a href="/basketball/leaders/standings.html" target="_blank">Standings</a></li>
            <li class="nav-link"><a href="/basketball/boxscores/" target="_blank">Scores</a></li>
            <li class="nav-link"><a href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a></li>
            <li class="nav-link"><a href="https://ashlauren1.github.io/ufc/" target="_blank">UFC</a></li>
        </ul>
    </div>
</div>

<div id="pageHeading">
	<div class="topnav">
        <a class="topnav-item" href="/basketball/" target="_blank">Projections</a>
        <a class="topnav-item" href="/basketball/players/" target="_blank">Players</a>
        <a class="topnav-item" href="/basketball/teams/" target="_blank">Teams</a>
        <a class="topnav-item" href="/basketball/leaders/" target="_blank">Leaders</a>
        <a class="topnav-item" href="/basketball/leaders/standings.html" target="_blank">Standings</a>
        <a class="topnav-item" href="/basketball/boxscores/" target="_blank">Scores</a>
        <a class="topnav-item" href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a>
        <a class="topnav-item" href="https://ashlauren1.github.io/ufc/" target="_blank">UFC</a>
    </div>
    
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for a player or team...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
    <div class="header">
        <h1>Player Directory</h1>
    </div>
</div>
        <button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>
        <div id="index-container">
        <table id="player-index">
        <thead>
            <tr>
                <th>Player</th>
                <th>Team</th>
            </tr>
        </thead>
        <tbody>
    """

    # Generate table rows grouped by team
    for _, row in roster_data.iterrows():
        team_id = row["TeamID"]
        team_name = row["Team"]
        player_id = row["PlayerID"]
        player_name = row["Player"]
        # Add player row
        html_content += f"""
            <tr>
                <td style="text-align:left"><a href="/basketball/players/{player_id}.html">{player_name}</a></td>
                <td style="text-align:center"><a href="/basketball/teams/{team_id}.html">{team_id}</a></td>
            </tr>
        """

    # Close the single <tbody>, table, and HTML tags
    html_content += """
        </tbody>
        </table>
        <div class="footer"></div>
    </body>
    </html>
    """

    # Write the HTML content to a file
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Player directory created at {output_file_path}")

# **Part 2: Generate Individual Player Gamelog Pages**
def create_player_gamelog_pages(gamelogs_data, output_dir):
    grouped_data = gamelogs_data.groupby('PlayerID')
    roster_data = pd.read_csv(roster_csv)

    for player_id, player_data in grouped_data:
        player_info = roster_data[roster_data['PlayerID'] == player_id]
        if player_info.empty:
            continue
        
        player_name = player_data.iloc[0]['Player']
        team_id = player_info.iloc[0]["TeamID"]
        team_name = player_info.iloc[0]["Team"]
        
        player_season = leader_data[leader_data['PlayerID'] == player_id]
        if player_season.empty:
            season_summary_rows = "<tr><td colspan='7'>Has Not Played</td></tr>"
        else:
            season_summary_rows = ""
            for _, row in player_season.iterrows():
                season_summary_rows += f"""
                <tr>
                    <td>{int(row['GP'])}</td>
                    <td>{row['PTS_GP']:.2f}</td>
                    <td>{row['REB_GP']:.2f}</td>
                    <td>{row['AST_GP']:.2f}</td>
                    <td>{row['STL_GP']:.2f}</td>
                    <td>{row['BLK_GP']:.2f}</td>
                    <td>{row['FG%']:.1f}%</td>
                </tr>
                """
        
        player_filename = os.path.join(output_dir, f"{player_id}.html")

        # Start HTML content for the player's gamelog
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <script src="modalsMobileNavAndSearch.js"></script>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="stylesheet" href="commonStylesheet.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <script src="playerScript.js"></script>
    <title>{player_name}</title>
<script>
document.addEventListener("DOMContentLoaded", function () {{
    const table = document.getElementById("player-table");
    const headerRow = table.querySelector("thead tr:first-child");
    const filterRow = document.querySelector("#filter-row");
    const rows = Array.from(table.querySelectorAll("tbody tr"));
    const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
    const clearAllButton = document.getElementById("clear-all-btn");
    const clearButton = document.getElementById("clear-filters-btn");
    let showSelectedOnly = false;
    let isDragging = false;

    addFilters(table);
    addSortToHeaders(table);

    clearButton.addEventListener("click", () => {{
        document.querySelectorAll(".filter-select").forEach(select => select.value = "");
        filterTable();
    }});

    clearAllButton.addEventListener("click", () => {{
        rows.forEach(row => {{
            row.classList.remove("selected-row");
            row.style.display = "";
        }});
        document.querySelectorAll(".filter-select").forEach(select => select.value = "");
        toggleSelectionBtn.textContent = "Show Selected Only";
        showSelectedOnly = false;
        filterTable();
    }});

    rows.forEach(row => {{
        row.addEventListener("mousedown", function () {{
            isDragging = true;
            toggleRowSelection(row);
        }});
        row.addEventListener("mouseenter", function () {{
            if (isDragging) toggleRowSelection(row);
        }});
        row.addEventListener("mouseup", () => isDragging = false);
    }});

    document.addEventListener("mouseup", () => isDragging = false);

    function toggleRowSelection(row) {{
        row.classList.toggle("selected-row");
    }}

    toggleSelectionBtn.addEventListener("click", () => {{
        showSelectedOnly = !showSelectedOnly;
        if (showSelectedOnly) {{
            rows.forEach(row => {{
                row.style.display = row.classList.contains("selected-row") ? "" : "none";
            }});
            toggleSelectionBtn.textContent = "Show All";
        }} else {{
            rows.forEach(row => (row.style.display = ""));
            toggleSelectionBtn.textContent = "Show Selected Only";
        }}
    }});

    function addFilters(table) {{
        const headerRow = table.querySelector("thead tr:first-child");
        const filterRow = document.querySelector("#filter-row");

        Array.from(headerRow.cells).forEach((header, index) => {{
            const filterCell = document.createElement("td");
            const filterSelect = document.createElement("select");
            filterSelect.classList.add("filter-select");

            filterSelect.innerHTML = '<option value="">All</option>';
            const values = Array.from(new Set(
                Array.from(table.querySelectorAll("tbody tr td:nth-child(" + (index + 1) + ")"))
                .map(cell => cell.textContent.trim())
            )).sort();

            values.forEach(value => {{
                const option = document.createElement("option");
                option.value = value;
                option.textContent = value;
                filterSelect.appendChild(option);
            }});

            filterSelect.addEventListener("change", filterTable);
            filterCell.appendChild(filterSelect);
            filterRow.appendChild(filterCell);
        }});
    }}

    function filterTable() {{
        const filters = Array.from(document.querySelectorAll(".filter-select")).map(select => select.value);
        rows.forEach(row => {{
            const cells = Array.from(row.cells);
            const matchesFilter = filters.every((filter, i) => !filter || cells[i].textContent.trim() === filter);
            row.style.display = matchesFilter ? "" : "none";
        }});
    }}

    function addSortToHeaders(table) {{
        const headers = table.querySelectorAll("thead th");
        headers.forEach((header, index) => {{
            header.style.cursor = "pointer";
            header.addEventListener("click", function () {{
                sortTable(table, index);
            }});
        }});
    }}

    function sortTable(table, columnIndex) {{
        const rows = Array.from(table.querySelectorAll("tbody tr"));
        const direction = table.dataset.sortDirection === "desc" ? "asc" : "desc";
        table.dataset.sortDirection = direction;
        
        // Detect data type
        let isNumeric = true;
        let isDate = true;
        for (let row of rows) {{
            const cellText = row.cells[columnIndex].textContent.trim();
            if (cellText === '') continue; // Skip empty cells
            if (isNumeric && isNaN(cellText)) {{
                isNumeric = false;
            }}
            if (isDate && isNaN(Date.parse(cellText))) {{
                isDate = false;
            }}
            if (!isNumeric && !isDate) break;
        }}

        rows.sort((a, b) => {{
            const cellA = a.cells[columnIndex].textContent.trim();
            const cellB = b.cells[columnIndex].textContent.trim();

            let valA, valB;

            if (isNumeric) {{
                valA = parseFloat(cellA);
                valB = parseFloat(cellB);
            }} else if (isDate) {{
                valA = new Date(cellA);
                valB = new Date(cellB);
            }} else {{
                valA = cellA.toLowerCase();
                valB = cellB.toLowerCase();
            }}

            if (valA < valB) {{
                return direction === "asc" ? -1 : 1;
            }} else if (valA > valB) {{
                return direction === "asc" ? 1 : -1;
            }} else {{
                return 0;
            }}
        }});

        // Append sorted rows to tbody
        const tbody = table.querySelector("tbody");
        rows.forEach(row => tbody.appendChild(row));
    }}
}});

document.addEventListener("DOMContentLoaded", function () {{
    initializeCharts(() => {{
        const images = document.querySelectorAll(".playerPicture");
        let validImageFound = false;

        images.forEach((img) => {{
            img.onload = function () {{
                if (!validImageFound) {{
                    validImageFound = true; // Mark the first valid image found
                }} else {{
                    img.style.display = "none"; // Hide any additional valid images
                }}
            }};

            img.onerror = function () {{
                img.style.display = "none"; // Hide the image if it fails to load
            }};
        }});
    }});
}});

function initializeCharts(callback) {{
    initializeChart("player_id", chartData, bettingLine, "G");
    if (callback) callback();
}}

document.addEventListener("DOMContentLoaded", function () {{
    const images = document.querySelectorAll(".playerPicture");
    let validImageFound = false;

    images.forEach((img) => {{
        img.onload = function () {{
            console.log("Image loaded:", img.src);
            if (!validImageFound) {{
                validImageFound = true;
            }} else {{
                img.style.display = "none"; 
            }}
        }};

        img.onerror = function () {{
            console.log("Image failed to load:", img.src);
            img.style.display = "none";
        }};
    }});
}});

document.addEventListener("DOMContentLoaded", function () {{
    const table = document.getElementById("player-table");
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));

    // Get the index of the "Date" column (assumes it's the first column)
    const dateColumnIndex = 1;

    // Sort rows by date (newest to oldest)
    rows.sort((a, b) => {{
        const dateA = new Date(a.cells[dateColumnIndex].textContent.trim());
        const dateB = new Date(b.cells[dateColumnIndex].textContent.trim());
        return dateB - dateA; // Descending order
    }});

    // Append sorted rows back to the table body
    rows.forEach(row => tbody.appendChild(row));
}});
</script>

</head>
<body>
<div id="mobileTopnav">
    <div class="menuBarContainer mobile active">
        <a href="javascript:void(0);" class="icon" onclick="myFunction()"><i class="fa fa-bars"></i>Menu</a>
    </div>
    <div id="myLinks">
        <ul class="navLinks">
            <li class="nav-link"><a href="/basketball/" target="_blank">Projections</a></li>
            <li class="nav-link"><a href="/basketball/players/" target="_blank">Players</a></li>
            <li class="nav-link"><a href="/basketball/teams/" target="_blank">Teams</a></li>
            <li class="nav-link"><a href="/basketball/leaders/" target="_blank">Leaders</a></li>
            <li class="nav-link"><a href="/basketball/leaders/standings.html" target="_blank">Standings</a></li>
            <li class="nav-link"><a href="/basketball/boxscores/" target="_blank">Scores</a></li>
            <li class="nav-link"><a href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a></li>
            <li class="nav-link"><a href="https://ashlauren1.github.io/ufc/" target="_blank">UFC</a></li>
        </ul>
    </div>
</div>

<div id="pageHeading">
	<div class="topnav">
        <a class="topnav-item" href="/basketball/" target="_blank">Projections</a>
        <a class="topnav-item" href="/basketball/players/" target="_blank">Players</a>
        <a class="topnav-item" href="/basketball/teams/" target="_blank">Teams</a>
        <a class="topnav-item" href="/basketball/leaders/" target="_blank">Leaders</a>
        <a class="topnav-item" href="/basketball/leaders/standings.html" target="_blank">Standings</a>
        <a class="topnav-item" href="/basketball/boxscores/" target="_blank">Scores</a>
        <a class="topnav-item" href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a>
        <a class="topnav-item" href="https://ashlauren1.github.io/ufc/" target="_blank">UFC</a>
    </div>
    
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for a player or team...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
    <div class="header">
    </div>
</div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
<main>
<div id="pageContainer">
    <div id="player_info">
        <div id="playerPictureContainer">
            <img class="playerPicture" src="https://www.basketball-reference.com/req/202106291/images/headshots/{player_id}.jpg" alt="{player_name}" onerror="this.style.display='none';">
        </div>    
        <div class="info">
            <h1>{player_name}</h1>
            <p>Team: {team_name}</p>
        </div>
        <div id="seasonStats">
            <table class="seasonSummary">
                <thead>
                    <tr>
                        <th>GP</th>
                        <th>PTS/GP</th>
                        <th>REB/GP</th>
                        <th>AST/GP</th>
                        <th>STL/GP</th>
                        <th>BLK/GP</th>
                        <th>FG%</th>
                    </tr>
                </thead>
                <tbody>
                    {season_summary_rows}
                </tbody>
            </table>
        </div>
    </div>    
    
    <div id="chartPlaceholder"></div>
    
    <div id="filter-container-div" class="button-container">
        <button id="toggle-selection-btn">Show Selected Only</button>
        <button id="clear-filters-btn">Remove Filters</button>
        <button id="clear-all-btn">Clear All</button>
    </div>
    
    <div id="tableContainer">        
        <table id="player-table">
            <thead>
                <tr>
                    <th>Season</th>
                    <th>Date</th>
                    <th>Team</th>
                    <th></th>
                    <th>Opp</th>
                    <th>PTS</th>
                    <th>REB</th>
                    <th>AST</th>
                    <th>STL</th>
                    <th>BLK</th>
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
                </tr>
                <tr id="filter-row"></tr>
            </thead>
            <tbody>
        '''

        # Add rows for each game in the player's gamelog
        for _, row in player_data.iterrows():
            html_content += f'''
                <tr>
                    <td style="text-align:left">{row['Season']}</td>
                    <td style="text-align:left"><a href="/basketball/boxscores/{row['GameID']}.html" target="_blank">{row['Date']}</a></td>
                    <td><a href="/basketball/teams/{row['Team']}.html" target="_blank">{row['Team']}</a></td>
                    <td>{'vs' if row['Is_Home'] == 1 else '@'}</td>
                    <td><a href="/basketball/teams/{row['Opp']}.html" target="_blank">{row['Opp']}</a></td>
                    <td>{row['PTS']}</td>
                    <td>{row['REB']}</td>
                    <td>{row['AST']}</td>
                    <td>{row['STL']}</td>
                    <td>{row['BLK']}</td>
                    <td>{row['TOV']}</td>
                    <td>{row['MP']:.2f}</td>
                    <td>{row['OffREB']}</td>
                    <td>{row['DefREB']}</td>
                    <td>{row['FG']}</td>
                    <td>{row['FGA']}</td>
                    <td>{row['3P']}</td>
                    <td>{row['3PA']}</td>
                    <td>{row['FT']}</td>
                    <td>{row['FTA']}</td>
                    <td>{row['PF']}</td>
                </tr>
            '''

        # Close HTML content
        html_content += '''
            </tbody>
        </table>
    </div>
</div>
</main>
<div class="footer"></div>
</body>
</html>
        '''

        # Write to HTML file
        with open(player_filename, 'w') as file:
            file.write(html_content)

    print("Player gamelog pages created successfully.")

# **Run the Functions**
# Create player directory
output_file_path = os.path.join(output_dir, "index.html")
create_player_directory(roster_data, output_file_path)

# Create individual player gamelog pages
create_player_gamelog_pages(gamelogs_data, output_dir)
