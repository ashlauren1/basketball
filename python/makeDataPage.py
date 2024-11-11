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
        const table = document.getElementById("allStats-table");
        const headerRow = table.querySelector("thead tr:first-child");
        const filterRow = document.querySelector("#filter-row");
        const rows = Array.from(table.querySelectorAll("tbody tr"));
        const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
        const clearAllButton = document.getElementById("clear-all-btn");
        const clearButton = document.getElementById("clear-filters-btn");
        let showSelectedOnly = false;
        let isDragging = false;

        const rowsPerPage = 500;
        let currentPage = 1;
        let totalPages = Math.ceil(rows.length / rowsPerPage);

        document.getElementById('total-pages').textContent = totalPages;

        function displayPage(page) {{
            const start = (page - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            rows.forEach((row, index) => {{
                row.style.display = (index >= start && index < end) ? '' : 'none';
            }});
            document.getElementById('current-page').textContent = page;
        }}

        document.getElementById('prev-page-btn').addEventListener('click', () => {{
            if (currentPage > 1) {{
                currentPage--;
                displayPage(currentPage);
            }}
        }});

        document.getElementById('next-page-btn').addEventListener('click', () => {{
            if (currentPage < totalPages) {{
                currentPage++;
                displayPage(currentPage);
            }}
        }});

        displayPage(currentPage);

        function filterTable() {{
            const filters = Array.from(document.querySelectorAll(".filter-select")).map(select => select.value);
            let visibleRows = 0;
            rows.forEach(row => {{
                const cells = Array.from(row.cells);
                const matchesFilter = filters.every((filter, i) => !filter || cells[i].textContent.trim() === filter);
                row.style.display = matchesFilter ? '' : 'none';
                if (matchesFilter) visibleRows++;
            }});
            currentPage = 1;
            totalPages = Math.ceil(visibleRows / rowsPerPage);
            document.getElementById('total-pages').textContent = totalPages;
            displayPage(currentPage);
        }}

        function sortTable(columnIndex) {{
            const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
            table.dataset.sortDirection = direction;

            let isNumeric = true;
            rows.sort((a, b) => {{
                const cellA = a.cells[columnIndex].textContent.trim();
                const cellB = b.cells[columnIndex].textContent.trim();
                if (isNumeric && (isNaN(cellA) || isNaN(cellB))) isNumeric = false;
                return isNumeric ? direction === "asc" ? cellA - cellB : cellB - cellA
                                : direction === "asc" ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            }});

            rows.forEach(row => table.querySelector("tbody").appendChild(row));
            displayPage(currentPage);
        }}

        function addFilters() {{
            Array.from(headerRow.cells).forEach((header, index) => {{
                const filterCell = document.createElement("td");
                const filterSelect = document.createElement("select");
                filterSelect.classList.add("filter-select");
                filterSelect.innerHTML = '<option value="">All</option>';
                const values = Array.from(new Set(rows.map(row => row.cells[index].textContent.trim()))).sort();
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

        addFilters();
        displayPage(currentPage);
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
                <th>Steal</th>
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
                <th>Foul</th>
                <th>B+S</th>
                <th>R+A</th>
                <th>P+A</th>
                <th>P+R</th>
                <th>P+R+A</th>
                <th>Fant</th>          
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
            <td>{row['PF']}</td>
            <td>{row['BLK_STL']}</td>
            <td>{row['REB_AST']}</td>
            <td>{row['PTS_AST']}</td>
            <td>{row['PTS_REB']}</td>
            <td>{row['PTS_REB_AST']}</td>
            <td>{row['FANTASY']}</td>
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
