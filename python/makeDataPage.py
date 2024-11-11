import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\basketball\data"
output_file = r"C:\Users\ashle\Documents\Projects\basketball\stats\index.html"

# Load game index data
gamelogs_csv = os.path.join(data_dir, "gamelogsNormalPlayers.csv")
gamelogs_data = pd.read_csv(gamelogs_csv)

# Start HTML content for the player's gamelog
html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
    <title>All Stats</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="icon" type="image/x-icon" href="favicon.ico">
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
        <a href="/basketball/stats/">All Stats</a>
        <a href="https://ashlauren1.github.io/hockey/" target="_blank">Hockey</a>
    </div>
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for a player or team...">
        <button id="search-button">Search</button>
    <div id="search-results"></div>
    <div class="header">
    <h1>All Data</h1>
    </div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>

    <div id="player-container">
    
    <div id="table-container">
    <span class="table-button-container">
    <caption class="caption">Gamelogs for all players who played at least 10 minutes since 1/1/2024. Click <a href="/basketball/data/gamelogs.csv" download="gamelogs">here</a> to download all data for all players since 2023, regardless of minutes played.</caption>
        <button id="toggle-selection-btn">Show Selected Only</button>
        <button id="clear-filters-btn">Remove Filters</button>
        <button id="clear-all-btn">Clear All</button>
    </span>
    <div id="pagination">
        <button id="prev-page-btn">Previous</button>
        <span id="page-info">Page <span id="current-page">1</span> of <span id="total-pages"></span></span>
        <button id="next-page-btn">Next</button>
    </div>
    
        <table id="allStats-table">
            <thead>
            <tr>
                <th>Season</th>
                <th>Date</th>
                <th>Player</th>
                <th>Tm</th>
                <th></th>
                <th>Opp</th>
                <th>Pts</th>
                <th>Reb</th>
                <th>Ast</th>
                <th>STL</th>
                <th>Blk</th>
                <th>TOV</th>
                <th>Mins</th>
                <th>OReb</th>
                <th>DReb</th>
                <th>FG</th>
                <th>FGA</th>
                <th>3P</th>
                <th>3PA</th>
                <th>FT</th>
                <th>FTA</th>
                <th>B+S</th>
                <th>R+A</th>
                <th>P+A</th>
                <th>P+R</th>
                <th>PRA</th>   
            </tr>
            <tr id="filter-row"></tr>
        </thead>
        <tbody>
'''

for _, row in gamelogs_data.iterrows():
    html_content += f'''
        <tr>
            <td style="text-align:left">{row['Season']}</td>
            <td style="text-align:left"><a href="/basketball/boxscores/{row['GameID']}.html" target="_blank">{row['Date']}</a></td>
            <td style="text-align:left"><a href="/basketball/players/{row['PlayerID']}.html" target="_blank">{row['Player']}</a></td>
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
            <td>{row['BLK_STL']}</td>
            <td>{row['REB_AST']}</td>
            <td>{row['PTS_AST']}</td>
            <td>{row['PTS_REB']}</td>
            <td>{row['PTS_REB_AST']}</td>
        </tr>
    '''

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
with open(output_file, 'w') as file:
    file.write(html_content)

print("All stats HTML file created successfully.")
