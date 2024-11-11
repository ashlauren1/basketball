import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\basketball\data"
output_dir = r"C:\Users\ashle\Documents\Projects\basketball\players"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# **Load Data**
roster_csv = os.path.join(data_dir, "rosters.csv")
gamelogs_csv = os.path.join(data_dir, "gamelogs.csv")

# Load roster data
roster_data = pd.read_csv(roster_csv)
roster_data.sort_values(by=["Team", "Player"], inplace=True)

# Load gamelogs data
gamelogs_data = pd.read_csv(gamelogs_csv)

# **Part 1: Generate Player Directory (index.html)**
def create_player_directory(roster_data, output_file_path):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Player Directory</title>
        <link rel="stylesheet" href="stylesheet.css">
        <link rel="icon" type="image/x-icon" href="favicon.ico">
        
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
        <h1>Player Directory</h1>
        </div>
        <button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>
        <div id="index-container">
        <table id="player-index">
        <thead>
            <tr>
                <th>Player</th>
                <th>Team</th>
                <th>Position</th>
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
        position = row["Position"]

        # Add player row
        html_content += f"""
            <tr>
                <td style="text-align:left"><a href="/basketball/players/{player_id}.html">{player_name}</a></td>
                <td style="text-align:center"><a href="/basketball/teams/{team_id}.html">{team_id}</a></td>
                <td style="text-align:center">{position}</td>
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

    for player_id, player_data in grouped_data:
        player_name = player_data.iloc[0]['Player']

        player_filename = os.path.join(output_dir, f"{player_id}.html")

        # Start HTML content for the player's gamelog
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
        <title>{player_name}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="stylesheet.css">
        <link rel="icon" type="image/x-icon" href="favicon.ico">


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

            // Add filters and sorting
            addFilters(table);
            addSortToHeaders(table);

            // "Clear Filters" button functionality
            clearButton.addEventListener("click", () => {{
                document.querySelectorAll(".filter-select").forEach(select => select.value = "");
                filterTable();
            }});

            // "Clear All" functionality
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
                const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
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
            <input type="text" id="search-bar" placeholder="Search for a player or team...">
            <button id="search-button">Search</button>
        <div id="search-results"></div>
        <div class="header">
        <h1>{player_name}</h1>
        </div>
        <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>

        <div id="player-container">
        
        <div id="table-container">
        <span class="table-button-container">
		<span class="caption">Gamelog</span>
            <button id="toggle-selection-btn">Show Selected Only</button>
            <button id="clear-filters-btn">Remove Filters</button>
            <button id="clear-all-btn">Clear All</button>
        </span>
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
                <tr id="filter-row">
                </tr>
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
