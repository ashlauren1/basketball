import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\basketball\data"
output_dir = r"C:\Users\ashle\Documents\Projects\basketball\leaders"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

leaders_csv = os.path.join(data_dir, "leaders.csv")
leader_data = pd.read_csv(leaders_csv)
leader_data.sort_values(by=["PTS", "PlayerID"], ascending=[False, True], inplace=True)

team_leaders_csv = os.path.join(data_dir, "teamStatsAndStandings.csv")
team_leaders_data = pd.read_csv(team_leaders_csv)

def create_current_leader_directory(leader_data, output_dir):
    current_leader_filename = os.path.join(output_dir, "2024-25.html")
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <script src="modalsMobileNavAndSearch.js"></script>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="stylesheet" href="commonStylesheet.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <title>NBA Season Leaders</title>
<script>
document.addEventListener("DOMContentLoaded", function () {
	const seasonTable = document.getElementById("seasonLeaders");
	const headerRow = seasonTable.querySelector("thead tr:first-child");
    const rows = Array.from(seasonTable.querySelectorAll("tbody tr"));
    const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
    const clearAllButton = document.getElementById("clear-all-btn");
    const clearButton = document.getElementById("clear-filters-btn");
    let showSelectedOnly = false;
    let isDragging = false;
	
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

    function toggleRowSelection(row) {
        row.classList.toggle("selected-row");
    }

    toggleSelectionBtn.addEventListener("click", () => {
        showSelectedOnly = !showSelectedOnly;
        if (showSelectedOnly) {
            rows.forEach(row => {
                row.style.display = row.classList.contains("selected-row") ? "" : "none";
            });
            toggleSelectionBtn.textContent = "Show All Rows";
        } else {
            rows.forEach(row => (row.style.display = ""));
            toggleSelectionBtn.textContent = "Show Selected Only";
        }
    });
	
	addSortToHeaders(seasonTable);
	
	function addSortToHeaders(seasonTable) {
		const headers = seasonTable.querySelectorAll("thead th");
		headers.forEach((header, index) => {
			header.style.cursor = "pointer";
			header.addEventListener("click", function () {
				sortTable(seasonTable, index);
			});
		});
	}
	
	function sortTable(seasonTable, columnIndex) {
		const rows = Array.from(seasonTable.querySelectorAll("tbody tr"));
		
		// TESTING DEFAULT DESC SORT DIRECTION
		let asc = false;
		const direction = seasonTable.dataset.sortDirection === "desc" ? "asc" : "desc";
		
		seasonTable.dataset.sortDirection = direction;

		rows.sort((a, b) => {
			let cellA = a.cells[columnIndex].textContent.trim();
			let cellB = b.cells[columnIndex].textContent.trim();

			let valA, valB;
			
			const isPercentage = cellA.includes('%') && cellB.includes('%');
			if (isPercentage) {
				valA = parseFloat(cellA.replace('%', ''));
				valB = parseFloat(cellB.replace('%', ''));
			} else if (!isNaN(cellA) && !isNaN(cellB)) {
				valA = parseFloat(cellA);
				valB = parseFloat(cellB);
			} else {
				valA = cellA.toLowerCase();
				valB = cellB.toLowerCase();
			}

			if (valA < valB) {
				return direction === "asc" ? -1 : 1;
			} else if (valA > valB) {
				return direction === "asc" ? 1 : -1;
			} else {
				return 0;
			}
		});

		const tbody = seasonTable.querySelector("tbody");
		rows.forEach(row => tbody.appendChild(row));
	}
	
	const teamSelect = document.getElementById("teams");
    const positionSelect = document.getElementById("pos");
    const positionGroups = {
        f: ["lw", "rw", "w", "c", "f"],
        w: ["lw", "rw", "w"],
        c: ["c"],
        lw: ["lw"],
        rw: ["rw"],
        d: ["d"],
    };
    
    teamSelect.addEventListener("change", filterTable);
    positionSelect.addEventListener("change", filterTable);

    function filterTable() {
        const teamFilter = teamSelect.value.trim().toLowerCase();
        const positionFilter = positionSelect.value.trim().toLowerCase();
        const positionGroup = positionGroups[positionFilter] || []; 
        
        rows.forEach(row => {
            const cells = row.cells;
            const teamCell = cells[1]?.textContent.trim().toLowerCase();
            const positionCell = cells[2]?.textContent.trim().toLowerCase();
            
            const matchesTeam = !teamFilter || teamCell === teamFilter;
            const matchesPosition =
                !positionFilter || positionGroup.includes(positionCell);
			const isFiltered = (!positionSelect.value === "") || (!teamSelect.value === "");
			
			!showSelectedOnly ? (row.style.display = matchesTeam && matchesPosition ? "" : "none") : (row.style.display = row.classList.contains("selected-row") && matchesTeam && matchesPosition ? "" : "none")
        });
    }
	
	clearButton.addEventListener("click", () => {
		document.querySelectorAll("select").forEach(select => select.value = "");
		filterTable();
		if (showSelectedOnly) {
            rows.forEach(row => {
                row.style.display = row.classList.contains("selected-row") ? "" : "none";
            });
            toggleSelectionBtn.textContent = "Show All Rows";
        } else {
            rows.forEach(row => (row.style.display = ""));
            toggleSelectionBtn.textContent = "Show Selected Only";
        }
	});

    clearAllButton.addEventListener("click", () => {
        document.querySelectorAll("select").forEach(select => select.value = "");

        rows.forEach(row => {
            row.classList.remove("selected-row");
            row.style.display = "";
        });
        toggleSelectionBtn.textContent = "Show Selected Only";
        showSelectedOnly = false;
        
        filterTable();
    });
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
	</div>
</div>
<button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
<main>
<div id="pageContainer">
<p class="title-caption">2024-25 NBA Stats</p>
    <div id="filter-container-div">
        <div id="filter-div">
            <form class="team-filters">
                <label for="teams">Team</label>
                <select id="teams" name="teams">
                    <option value="">All</option>
                    <option value="atl">Atlanta Hawks</option>
                    <option value="bos">Boston Celtics</option>
                    <option value="brk">Brooklyn Nets</option>
                    <option value="cho">Charlotte Hornets</option>
                    <option value="chi">Chicago Bulls</option>
                    <option value="cle">Cleveland Cavaliers</option>
                    <option value="dal">Dallas Mavericks</option>
                    <option value="den">Denver Nuggets</option>
                    <option value="det">Detroit Pistons</option>
                    <option value="gsw">Golden State Warriors</option>
                    <option value="hou">Houston Rockets</option>
                    <option value="ind">Indiana Pacers</option>
                    <option value="lac">Los Angeles Clippers</option>
                    <option value="lal">Los Angeles Lakers</option>
                    <option value="mem">Memphis Grizzlies</option>
                    <option value="mia">Miami Heat</option>
                    <option value="mil">Milwaukee Bucks</option>
                    <option value="min">Minnesota Timberwolves</option>
                    <option value="nop">New Orleans Pelicans</option>
                    <option value="nyk">New York Knicks</option>
                    <option value="okc">Oklahoma City Thunder</option>
                    <option value="orl">Orlando Magic</option>
                    <option value="phi">Philadelphia 76ers</option>
                    <option value="pho">Phoenix Suns</option>
                    <option value="por">Portland Trail Blazers</option>
                    <option value="sac">Sacramento Kings</option>
                    <option value="sas">San Antonio Spurs</option>
                    <option value="tor">Toronto Raptors</option>
                    <option value="uta">Utah Jazz</option>
                    <option value="was">Washington Wizards</option>
                </select>
            </form>
        </div>
        <div class="button-container">
            <button id="toggle-selection-btn">Show Selected Only</button>
            <button id="clear-filters-btn">Remove Filters</button>
            <button id="clear-all-btn">Clear All</button>
            <button id="glossaryButton">Glossary</button>
        </div>
    </div>
    
    <div id="tableContainer">
        <table id="seasonLeaders" class="seasonLeadersTable">
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Team</th>
                    <th>Age</th>
                    <th data-tip="Games Played">GP</th>
                    <th data-tip="Points">PTS</th>
                    <th data-tip="Rebounds">REB</th>
                    <th data-tip="Assists">AST</th>
                    <th data-tip="Steals">STL</th>
                    <th data-tip="Blocks">BLK</th>
                    <th data-tip="Turnovers">TOV</th>
                    <th data-tip="Fouls">PF</th>
                    <th data-tip="Offensive Rebounds">OffREB</th>
                    <th data-tip="Defensive Rebounds">DefREB</th>
                    <th data-tip="Minutes Played">MP</th>
                    <th data-tip="Field Goals">FG</th>
                    <th data-tip="Field Goals Attempted">FGA</th>
                    <th data-tip="Field Goal %">FG%</th>
                    <th data-tip="3-Pointers">3P</th>
                    <th data-tip="3-Point Attempts">3PA</th>
                    <th data-tip="3-Point %">3P%</th>
                    <th data-tip="Free Throws">FT</th>
                    <th data-tip="Free Throw Attempts">FTA</th>
                    <th data-tip="Free Throw %">FT%</th>
                    <th data-tip="2-Pointers">2P</th>
                    <th data-tip="2-Point Attempts">2PA</th>
                    <th data-tip="2-Point %">2P%</th>
                    <th data-tip="Points per Game">PTS/GP</th>
                    <th data-tip="Rebounds per Game">REB/GP</th>
                    <th data-tip="Assists per Game">AST/GP</th>
                    <th data-tip="Steals per Game">STL/GP</th>
                    <th data-tip="Blocks per Game">BLK/GP</th>
                    <th data-tip="Minutes per Game">MP/GP</th>
                </tr>
            </thead>
            <tbody>
    """

    # Generate table rows grouped by team
    for _, row in leader_data.iterrows():
        team_id = row["TeamID"]
        player_id = row["PlayerID"]
        player_name = row['Player'].replace(" ", "&nbsp;")
        age = row["Age"]
        
        # Add player row
        html_content += f"""
            <tr>
                <td style="text-align:left"><a href="/hockey/players/{player_id}.html">{player_name}</a></td>
                <td><a href="/hockey/teams/{team_id}.html">{team_id}</a></td>
                <td style="text-align:center">{age}</td>
                <td>{int(row['GP'])}</td>
                <td>{int(row['PTS'])}</td>
                <td>{int(row['REB'])}</td>
                <td>{int(row['AST'])}</td>
                <td>{int(row['STL'])}</td>
                <td>{int(row['BLK'])}</td>
                <td>{int(row['TOV'])}</td>
                <td>{int(row['PF'])}</td>
                <td>{int(row['OffREB'])}</td>
                <td>{int(row['DefREB'])}</td>
                <td>{int(row['MP'])}</td>
                <td>{int(row['FG'])}</td>
                <td>{int(row['FGA'])}</td>
                <td>{row['FG%']:.2f}%</td>
                <td>{int(row['3P'])}</td>
                <td>{int(row['3PA'])}</td>
                <td>{row['3P%']:.2f}%</td>
                <td>{int(row['FT'])}</td>
                <td>{int(row['FTA'])}</td>
                <td>{row['FT%']:.2f}%</td>
                <td>{int(row['2P'])}</td>
                <td>{int(row['2PA'])}</td>
                <td>{row['2P%']:.2f}%</td>
                <td>{row['PTS_GP']:.2f}</td>
                <td>{row['REB_GP']:.2f}</td>
                <td>{row['AST_GP']:.2f}</td>
                <td>{row['STL_GP']:.2f}</td>
                <td>{row['BLK_GP']:.2f}</td>
                <td>{row['MP_GP']:.2f}</td>
            </tr>
        """

    # Close the single <tbody>, table, and HTML tags
    html_content += """
        </tbody>
    </table>
</div>
</div>
<div class="footer"></div>
</body>
</html>
    """

    with open(current_leader_filename, "w") as file:
        file.write(html_content)

    print(f"Current leader pages created successfully")

def create_leader_directory(leader_data, output_file_path):
    int_columns = ["GP", "PTS", "REB", "AST", "STL", "BLK", "TOV", "PF", "DefREB", "OffREB", "MP", "FG", "FGA", "3P", "3PA", "2P", "2PA", "FT", "FTA"]
    decimal_columns = [col for col in leader_data.columns if col not in int_columns + ["Player", "PlayerID", "TeamID"]]

    leader_data[int_columns] = leader_data[int_columns].fillna(0).astype(int)
    leader_data[decimal_columns] = leader_data[decimal_columns].round(2)
    
    stat_columns = {
        "GP": "Games Played",
        "PTS": "Points",
        "REB": "Rebounds",
        "AST": "Assists",
        "STL": "Steals",
        "BLK": "Blocks",
        "TOV": "Turnovers",
        "PF": "Fouls",
        "OffREB": "Offensive Rebounds",
        "DefREB": "Defensive Rebounds",
        "MP": "Minutes Played",
        "FG": "Field Goals",
        "FGA": "Field Goals Attempted",
        "FG%": "Field Goal %",
        "3P": "3-Pointers",
        "3PA": "3-Point Attempts",
        "3P%": "3-Point %",
        "FT": "Free Throws",
        "FTA": "Free Throw Attempts",
        "2P": "2-Pointers",
        "2PA": "2-Point Attempts",
        "2P%": "2-Point %"
    }

    leaders = {}
    
    for key, display_name in stat_columns.items():
        if key in leader_data.columns:
            if key == "FG%" or "3P%" or "2P%":
                filtered_data = leader_data[leader_data["FG"] >= 50]
                if not filtered_data.empty:
                    max_value = filtered_data[key].max()
                    tied_leaders = filtered_data[filtered_data[key] == max_value]
                else:
                    continue
            else:
                max_value = leader_data[key].max()
                tied_leaders = leader_data[leader_data[key] == max_value]
            
            leaders[key] = [
                {
                    "player": row["Player"],
                    "player_id": row["PlayerID"],
                    "value": int(row[key]) if key in int_columns else round(row[key], 2)
                }
                for _, row in tied_leaders.iterrows()
            ]

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <script src="modalsMobileNavAndSearch.js"></script>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="stylesheet" href="commonStylesheet.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <title>Leaders Directory</title>
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
        <h1>NBA 2024-25 Leaders</h1>
    </div>
</div>

    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>

<main>
<div id="pageContainer">
    <div id="seasons_list_container">
        <p class="title-caption">Leaders by Season:</p>
		<ul class="seasons_list">
            <li><a href="/basketball/leaders/2024-25.html">2024-25</a></li>
		</ul>
	</div>
    <p class="title-caption">Current Leaders:</p>
    <div class="tabular">
    """
    
    for key, display_name in stat_columns.items():
        if key in leaders:
            leader_entries = ""
            is_tie = len(leaders[key]) > 1  # Check if there's a tie
            display_name_with_tie = f"{display_name} (Tie)" if is_tie else display_name
            leader_entries += f'<div class="groupedTabular">'
            
            for i, player in enumerate(leaders[key]):
                if i == 0:
                    leader_entries += f"""
        <div class="tabular_row">
            <div><strong>{display_name_with_tie}</strong></div>
            <div><a href="/basketball/players/{player['player_id']}.html">{player['player']}</a> ({player['value']})</div>
        </div>
                    """
                else:
                    leader_entries += f"""
        <div class="tabular_row">
            <div></div>
            <div><a href="/basketball/players/{player['player_id']}.html">{player['player']}</a> ({player['value']})</div>
        </div>
                    """
            leader_entries += f'</div>'

            html_content += leader_entries

    html_content += """
    </div>
</div>
</main>
<div class="footer"></div>
</body>
</html>
    """

    # Write the HTML content to a file
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Leaders index created at {output_file_path}")


def create_standings_page(team_leaders_data, output_dir):
    league_table = team_leaders_data
    conference_tables = {
        "Eastern": team_leaders_data[team_leaders_data["Conference"] == "Eastern"],
        "Western": team_leaders_data[team_leaders_data["Conference"] == "Western"],
    }
    
    html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <script src="modalsMobileNavAndSearch.js"></script>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="stylesheet" href="commonStylesheet.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <title>2024-25 Standings</title>

<script>
document.addEventListener("DOMContentLoaded", function () {{
    const leagueTable = document.getElementById("league-table-container");
    const conferenceTables = document.getElementById("conference-table-container");
    const buttons = {{
        league: document.getElementById("btn-league"),
        conference: document.getElementById("btn-conference"),
    }};	
	
    leagueTable.style.display = "none";
    conferenceTables.style.display = "block";
    	
	buttons.conference.classList.add("active-button");

    function showTable(view) {{
        leagueTable.style.display = view === "league" ? "block" : "none";
        conferenceTables.style.display = view === "conference" ? "block" : "none";
		
		Object.values(buttons).forEach(button => button.classList.remove("active-button"));

        buttons[view].classList.add("active-button");
    }}

    document.getElementById("btn-league").addEventListener("click", () => showTable("league"));
    document.getElementById("btn-conference").addEventListener("click", () => showTable("conference"));
    
    const headerRow = leagueTable.querySelectorAll("thead tr");
    
    const rows = Array.from(leagueTable.querySelectorAll("tbody tr"));

    addSortToHeaders(leagueTable);
        
    function addSortToHeaders(leagueTable) {{
        const headers = leagueTable.querySelectorAll("thead th");
        headers.forEach((header, index) => {{
            header.style.cursor = "pointer";
            header.addEventListener("click", function () {{
                sortTable(leagueTable, index);
            }});
        }});
    }}
    
    function sortTable(leagueTable, columnIndex) {{
        const rows = Array.from(leagueTable.querySelectorAll("tbody tr"));
        
        let asc = false;
        const direction = leagueTable.dataset.sortDirection === "desc" ? "asc" : "desc";
        
        leagueTable.dataset.sortDirection = direction;

        rows.sort((a, b) => {{
            let cellA = a.cells[columnIndex].textContent.trim();
            let cellB = b.cells[columnIndex].textContent.trim();

            let valA, valB;
            
            const isPercentage = cellA.includes('%') && cellB.includes('%');
            if (isPercentage) {{
                valA = parseFloat(cellA.replace('%', ''));
                valB = parseFloat(cellB.replace('%', ''));
            }} else if (!isNaN(cellA) && !isNaN(cellB)) {{
                valA = parseFloat(cellA);
                valB = parseFloat(cellB);
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

        const tbody = leagueTable.querySelector("tbody");
        rows.forEach(row => tbody.appendChild(row));
    }}
    
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
        <h1>2024-25 Standings</h1>
    </div>
</div>
    
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>

<main>

<div id="pageContainer">
    <div class="standings-button-container">
        <button id="btn-league">League</button>
        <button id="btn-conference">Conference</button>
    </div>
    <div id="tableContainer">
    '''
    
    # Add League Table
    html_content += f'<div id="league-table-container" style="display: none;">'
    html_content += generate_html_table(league_table, "League Standings", "league-standings", conference_table=False)
    html_content += '''
        </div>
        '''
    
    # Add Conference tables
    html_content += '<div id="conference-table-container" style="display: block;"><p class="title-caption">Standings</p>'
    for conference, table in conference_tables.items():
        html_content += generate_html_table(table, f"{conference} Conference", f"{conference.lower()}-conference", conference_table=True)
    html_content += '''
        </div>
    '''

    # Close HTML content
    html_content += '''
</div>
</div>
</main>
<div class="footer"></div>
</body>
</html>
    '''
    
    standings_filename = os.path.join(output_dir, "standings.html")
    with open(standings_filename, "w") as file:
        file.write(html_content)
    
    print(f"Standings page created at {standings_filename}")
    
def generate_html_table(data, title, table_id, conference_table=False):
    logo_id_map = {
        "CHO": "cha",
        "BRK": "bkn",
        "NOP": "no",
        "UTA": "utah"
    }
    
    def get_logo_url(team_id):
        logo_id = logo_id_map.get(team_id, team_id)
        return f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/{logo_id}.png&h=40&w=40"
    
    if not conference_table:
        table_html = f'<p class="title-caption">{title}</p>'
    else:
        table_html = ''
    
    table_html += f'<table id="{table_id}" class="standings-table">'
    
    if conference_table:
        first_header = f'<th>{title}</th><th data-tip="Rank">Rk</th>'
    else:
        first_header = '<th>Team</th>'
    
    if conference_table:
        games_back = f'<th data-tip="Games Back">GB</th>'
    else:
        games_back = ''

    table_html += f'''
        <thead>
            <tr>
                {first_header}
                <th data-tip="Games Played">GP</th>
                <th data-tip="Wins">W</th>
                <th data-tip="Losses">L</th>
                {games_back}
                <th data-tip="Points">PTS</th>
                <th data-tip="Rebounds">REB</th>
                <th data-tip="Assists">AST</th>
                <th data-tip="Steals">STL</th>
                <th data-tip="Blocks">BLK</th>
                <th data-tip="Turnovers">TOV</th>
                <th data-tip="Field Goal %">FG%</th>
                <th data-tip="3-Point %">3P%</th>
                <th data-tip="2-Point %">2P%</th>
                <th data-tip="Free Throw %">FT%</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for _, row in data.iterrows():
        team_id = row['TeamID']
        team_name = row['Team'].replace(" ", "&nbsp;")
        logo_url = get_logo_url(team_id)
        team_name_with_logo = f'<div class="team-cell"><div class="logo-container"><a href="/basketball/teams/{team_id}.html" target="_blank"><img src="{logo_url}" alt="{team_id}" class="team-logo"></a></div><div class="team-name-container"><a href="/basketball/teams/{team_id}.html" target="_blank">{team_name}</a></div></div>'
        rank = row['Rk']
        
        if conference_table:
            rank_td = f'<td>{rank}</td>'
        else:
            rank_td = ''
        
        if conference_table:
            gb_td = f'<td>{row['GB']}</td>'
        else:
            gb_td = ''
        
        table_html += f'''
            <tr>
                <td class="team-name-cell">{team_name_with_logo}</td>
                {rank_td}
                <td>{row['GP']}</td>
                <td>{row['W']}</td>
                <td>{row['L']}</td>
                {gb_td}
                <td>{row['PTS']}</td>
                <td>{row['REB']}</td>
                <td>{row['AST']}</td>
                <td>{row['STL']}</td>
                <td>{row['BLK']}</td>
                <td>{row['TOV']}</td>
                <td>{row['FG%']:.2f}%</td>
                <td>{row['3P%']:.2f}%</td>
                <td>{row['2P%']:.2f}%</td>
                <td>{row['FT%']:.2f}%</td>
            </tr>
        '''
        
    table_html += '''
        </tbody>
    </table>
    '''
    return table_html

output_file_path = os.path.join(output_dir, "index.html")
create_leader_directory(leader_data, output_file_path)

create_current_leader_directory(leader_data, output_dir)
create_standings_page(team_leaders_data, output_dir)
