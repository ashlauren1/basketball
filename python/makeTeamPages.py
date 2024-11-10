import pandas as pd
import os

# **File Paths**
team_csv = r"C:\Users\ashle\Documents\Projects\basketball\data\teamgamelogs.csv"
output_dir = r"C:\Users\ashle\Documents\Projects\basketball\teams"

# **Ensure Output Directory Exists**
os.makedirs(output_dir, exist_ok=True)

# **Load Data Once**
data = pd.read_csv(team_csv)

# **Part 1: Create Team Directory (index.html)**
def create_team_directory(data, output_dir):
    unique_teams = data.drop_duplicates(subset=["Team", "TeamID"]).sort_values(by="Team")
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Team Directory</title>
        <link rel="stylesheet" href="stylesheet.css">
        <link rel="icon" type="image/x-icon" href="/basketball/images/favicon.ico">
        <script>
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
                    window.open(url, "_blank");
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
        <h1>Team Directory</h1>
        </div>
        <button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>
        <div id="index-container">
        <table id="team-index">
            <thead>
                <tr>
                    <th>Team</th>
                </tr>
            </thead>
            <tbody>
    """

    # Populate the table with each unique team and link
    for _, row in unique_teams.iterrows():
        team_name = row["Team"]
        team_id = row["TeamID"]

        html_content += f"""
            <tr>
                <td style="text-align:left"><a href="/basketball/teams/{team_id}.html">{team_name}</a></td>
            </tr>
        """

    # Close the table and HTML tags
    html_content += """
            </tbody>
        </table>
        <div class="footer"></div>
    </body>
    </html>
    """

    # Write the HTML content to a file
    output_file_path = os.path.join(output_dir, "index.html")
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Team directory created at {output_file_path}")

# **Part 2: Generate Individual Team Pages**
def create_team_pages(data, output_dir):
    grouped_data = data.groupby('TeamID')

    for team_id, team_data in grouped_data:
        team_name = team_data.iloc[0]['Team']
        team_filename = os.path.join(output_dir, f"{team_id}.html")

        # Start HTML content for the team's gamelog
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
        <title>{team_name}</title>
        <link rel="stylesheet" href="stylesheet.css">
        <link rel="icon" type="image/x-icon" href="/basketball/images/favicon.ico">

        <script>
        document.addEventListener("DOMContentLoaded", function () {{
            const table = document.getElementById("team-table");
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
                        window.open(url, "_blank");
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
        </div>
        <div class="header">
        <h1>{team_name} Gamelog</h1>
        </div>
        <div class="button-container">
            <button id="toggle-selection-btn">Show Selected Only</button>
            <button id="clear-filters-btn">Remove Filters</button>
            <button id="clear-all-btn">Clear All</button>
        </div>
        <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
        
        <div id="team-container">
            <table id="team-table">
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
                        <th>PTSA</th>
                        <th>REBA</th>
                        <th>ASTA</th>
                        <th>STLA</th>
                        <th>BLKA</th>
                    </tr>
                <tr id="filter-row">
                </tr>
                </thead>
                <tbody>
        '''

        # Add rows for each game in the team's gamelog
        for _, row in team_data.iterrows():
            html_content += f'''
                <tr>
                    <td style="text-align:left">{row['Season']}</td>
                    <td style="text-align:left"><a href="/basketball/boxscores/{row['GameID']}.html" target="_blank">{row['Date']}</a></td>
                    <td><a href="/basketball/teams/{row['TeamID']}.html" target="_blank">{row['TeamID']}</a></td>
                    <td>{'vs' if row['Is_Home'] == 1 else '@'}</td>
                    <td><a href="/basketball/teams/{row['Opp']}.html" target="_blank">{row['Opp']}</a></td>
                    <td>{row['PTS']}</td>
                    <td>{row['REB']}</td>
                    <td>{row['AST']}</td>
                    <td>{row['STL']}</td>
                    <td>{row['BLK']}</td>
                    <td>{row['PTSA']}</td>
                    <td>{row['REBA']}</td>
                    <td>{row['ASTA']}</td>
                    <td>{row['STLA']}</td>
                    <td>{row['BLKA']}</td>
                </tr>
            '''

        # Close HTML content
        html_content += '''
                </tbody>
            </table>
            </div>
        </body>
        </html>
        '''

        # Write to HTML file
        with open(team_filename, 'w') as file:
            file.write(html_content)

    print("Team Pages created successfully.")

# **Run the Functions**
create_team_directory(data, output_dir)
create_team_pages(data, output_dir)
