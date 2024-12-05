import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\basketball\data"
output_dir = r"C:\Users\ashle\Documents\Projects\basketball\teams"

team_csv = os.path.join(data_dir, "teamgamelogs.csv")
team_leaders_csv = os.path.join(data_dir, "teamStatsAndStandings.csv")

# **Ensure Output Directory Exists**
os.makedirs(output_dir, exist_ok=True)

# **Load Data Once**
data = pd.read_csv(team_csv).sort_values(by=["Date"], ascending=[False])
team_leaders_data = pd.read_csv(team_leaders_csv)

# **Part 1: Create Team Directory (index.html)**
def create_team_directory(data, output_dir):
    logo_id_map = {
        "CHO": "cha",
        "BRK": "bkn",
        "NOP": "no",
        "UTA": "utah"
    }
    
    def get_logo_url(team_id):
        logo_id = logo_id_map.get(team_id, team_id)
        return f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/{logo_id}.png&h=40&w=40"
    
    unique_teams = data.drop_duplicates(subset=["Team", "TeamID"]).sort_values(by="Team")
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
    <script src="script.js"></script>
    <title>Team Directory</title>
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
        <h1>Team Directory</h1>
    </div>
</div>

    <button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>

<main>
<div id="pageContainer">
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
        logo_url = get_logo_url(team_id)
        team_name_with_logo = f'<div class="team-cell"><div class="logo-container"><a href="/basketball/teams/{team_id}.html" target="_blank"><img src="{logo_url}" alt="{team_id}" class="team-logo"></a></div><div class="team-name-container"><a href="/basketball/teams/{team_id}.html" target="_blank">{team_name}</a></div></div>'

        html_content += f"""
            <tr>
                <td class="team-name-cell">{team_name_with_logo}</td>
            </tr>
        """

    # Close the table and HTML tags
    html_content += """
        </tbody>
    </table>
</div>
</div>
</main>
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
    logo_id_map = {
        "CHO": "cha",
        "BRK": "bkn",
        "NOP": "no",
        "UTA": "utah"
    }
    
    def get_logo_url(team_id):
        logo_id = logo_id_map.get(team_id, team_id)
        return f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/{logo_id}.png"

    for team_id, team_data in grouped_data:
        team_name = team_data.iloc[0]['Team']
        team_info = team_leaders_data[team_leaders_data['TeamID'] == team_id]
        logo_url = get_logo_url(team_id)
        team_filename = os.path.join(output_dir, f"{team_id}.html")
        
        conference = team_info.iloc[0]['Conference']
        rank = team_info.iloc[0]['Rk']
        wins = team_info.iloc[0]['W']
        losses = team_info.iloc[0]['L']
        record = f'<h2>{wins}-{losses}</h2>'

        # Start HTML content for the team's gamelog
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
    <script src="script.js"></script>
    <title>{team_name}</title>
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
    <div id="team_info">
        <div id="teamLogoContainer">
            <img class="logo_img" src="{logo_url}" alt="{team_id}" onerror="this.style.display='none';">
       </div>
       <div class="teamInfo">
            <h1>{team_name}</h1>
            {record}
            <p>#{rank} in {conference} Conference</p>
        </div>
    </div>
    
    <div id="filter-container-div" class="button-container">
        <button id="toggle-selection-btn">Show Selected Only</button>
        <button id="clear-filters-btn">Remove Filters</button>
        <button id="clear-all-btn">Clear All</button>
    </div>
    
    <div id="tableContainer">
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
                <tr id="filter-row"></tr>
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
</div>
</main>
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
