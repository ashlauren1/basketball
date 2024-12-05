from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random


chrome_options = Options()
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-webgl')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

service = Service(r"C:\Users\ashle\AppData\Local\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

REQUESTS_PER_MINUTE = 20
ONE_MINUTE = 60

@sleep_and_retry
@limits(calls=REQUESTS_PER_MINUTE, period=ONE_MINUTE)
def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def convert_mp_to_decimal(mp_str):
    """Convert MP from 'mm:ss' to decimal minutes."""
    try:
        minutes, seconds = map(int, mp_str.split(':'))
        return minutes + seconds / 60
    except ValueError:
        return None

def extract_date_from_game_id(game_id):
    date_str = game_id[:8]
    return datetime.strptime(date_str, "%Y%m%d").strftime("%m/%d/%Y")

games_info = {
    "202411260WAS": ("WAS", "CHI"),
    "202411260MIA": ("MIA", "MIL"),
    "202411260MIN": ("MIN", "HOU"),
    "202411260UTA": ("UTA", "SAS"),
    "202411260PHO": ("PHO", "LAL"),
    "202411270CHO": ("CHO", "MIA"),
    "202411270CLE": ("CLE", "ATL"),
    "202411270IND": ("IND", "POR"),
    "202411270ORL": ("ORL", "CHI"),
    "202411270PHI": ("PHI", "HOU"),
    "202411270WAS": ("WAS", "LAC"),
    "202411270DAL": ("DAL", "NYK"),
    "202411270MEM": ("MEM", "DET"),
    "202411270MIN": ("MIN", "SAC"),
    "202411270NOP": ("NOP", "TOR"),
    "202411270SAS": ("SAS", "LAL"),
    "202411270PHO": ("PHO", "BRK"),
    "202411270UTA": ("UTA", "DEN"),
    "202411270GSW": ("GSW", "OKC"),
    "202411290CHO": ("CHO", "NYK"),
    "202411290ATL": ("ATL", "CLE"),
    "202411290MEM": ("MEM", "NOP"),
    "202411290BRK": ("BRK", "ORL"),
    "202411290MIN": ("MIN", "LAC"),
    "202411290CHI": ("CHI", "BOS"),
    "202411290IND": ("IND", "DET"),
    "202411290MIA": ("MIA", "TOR"),
    "202411290LAL": ("LAL", "OKC"),
    "202411290POR": ("POR", "SAC"),
    "202411300CHO": ("CHO", "ATL"),
    "202411300DET": ("DET", "PHI"),
    "202411300MIL": ("MIL", "WAS"),
    "202411300PHO": ("PHO", "GSW"),
    "202411300UTA": ("UTA", "DAL"),
    "202412010BRK": ("BRK", "ORL"),
    "202412010MEM": ("MEM", "IND"),
    "202412010CLE": ("CLE", "BOS"),
    "202412010NYK": ("NYK", "NOP"),
    "202412010TOR": ("TOR", "MIA"),
    "202412010HOU": ("HOU", "OKC"),
    "202412010UTA": ("UTA", "LAL"),
    "202412010POR": ("POR", "DAL"),
    "202412010SAC": ("SAC", "SAS"),
    "202412010LAC": ("LAC", "DEN"),
    "202412020ATL": ("ATL", "NOP"),
    "202412020BOS": ("BOS", "MIA"),
    "202412020CHI": ("CHI", "BRK"),
    "202412020MIN": ("MIN", "LAL"),
    "202412030CHO": ("CHO", "PHI"),
    "202412030CLE": ("CLE", "WAS"),
    "202412030DET": ("DET", "MIL"),
    "202412030NYK": ("NYK", "ORL"),
    "202412030TOR": ("TOR", "IND"),
    "202412030OKC": ("OKC", "UTA"),
    "202412030DAL": ("DAL", "MEM"),
    "202412030PHO": ("PHO", "SAS"),
    "202412030DEN": ("DEN", "GSW"),
    "202412030SAC": ("SAC", "HOU"),
    "202412030LAC": ("LAC", "POR"),
    "202412040BOS": ("BOS", "DET"),
    "202412040BRK": ("BRK", "IND"),
    "202412040MIA": ("MIA", "LAL"),
    "202412040PHI": ("PHI", "ORL"),
    "202412040MIL": ("MIL", "ATL"),
    "202412040LAC": ("LAC", "MIN")
}

# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\basketball"
data_path = r"C:\Users\ashle\Documents\Projects\basketball\data"

player_columns = [
    "Home", "HomeName", "Away", "AwayName", "Season", "GameID", "Date", "Game", "Player", "PlayerID", "Team", "TeamName", "Is_Home", "Opp", "OppName", "PTS", "REB", "AST", "STL", "BLK", "TOV", "MP", "OffREB", "DefREB", "FG", "FGA", "3P", "3PA", "FT", "FTA", "PF", "BLK_STL", "REB_AST", "PTS_AST", "PTS_REB", "PTS_REB_AST", "FANTASY"
]

boxscore_data = []

for game_id, (home_team, away_team) in games_info.items():
    url = f"https://www.basketball-reference.com/boxscores/{game_id}.html"

    try:
        print(f"Processing game ID {game_id} - Home Team: {home_team}, Away Team: {away_team}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        home_team_section = soup.select_one(f"#box-{home_team}-game-basic_sh")
        away_team_section = soup.select_one(f"#box-{away_team}-game-basic_sh")
        home_team_name = home_team_section.find("h2").get_text(strip=True) if home_team_section else "Unknown"
        away_team_name = away_team_section.find("h2").get_text(strip=True) if away_team_section else "Unknown"
        
        for team, team_name, is_home in [
            (home_team, home_team_name, True),
            (away_team, away_team_name, False),
        ]:
            table_selector = f"#box-{team}-game-basic"
            table = soup.select_one(table_selector)
            if table:
                header_row = table.select("thead tr")[1]
                headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
                
                headers[0] = "Player"
                
                rows = table.select("tbody tr:not([data-stat='reason'])")
                
                consolidated_rows = []
                for row in rows:
                    if "Starters" in row.get_text(strip=True) or "Reserves" in row.get_text(strip=True):
                        continue
                    consolidated_rows.append(row)
                
                consolidated_html = '<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>'.format(
                    ''.join(f'<th>{header}</th>' for header in headers),
                    ''.join(str(row) for row in consolidated_rows)
                )
                df = pd.read_html(StringIO(consolidated_html), encoding="utf-8")[0]
                
                column_mapping = {
                    "TRB": "REB",
                    "ORB": "OffREB",
                    "DRB": "DefREB",
                }
                df = df.rename(columns=column_mapping)
                
                df = df[["Player", "PTS", "REB", "AST", "STL", "BLK", "TOV", "MP", "OffREB", "DefREB", "FG", "FGA", "3P", "3PA", "FT", "FTA", "PF"]]
                
                if "MP" in df.columns:
                    df["MP"] = df["MP"].apply(convert_mp_to_decimal)
                 
                df.insert(0, "Home", home_team)
                df.insert(1, "HomeName", home_team_name)
                df.insert(2, "Away", away_team)
                df.insert(3, "AwayName", away_team_name)
                df.insert(4, "Season", "2024-25")
                df.insert(5, "GameID", game_id)
                df.insert(6, "Date", extract_date_from_game_id(game_id))
                df.insert(7, "Game", f"{home_team} vs {away_team}")

                player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr th[data-append-csv]")]
                df["Player ID"] = player_ids + [None] * (len(df) - len(player_ids))
                df.insert(df.columns.get_loc("Player") + 1, "PlayerID", player_ids + [None] * (len(df) - len(player_ids)))
                df.insert(df.columns.get_loc("Player") + 2, "Team", home_team if is_home else away_team)
                df.insert(df.columns.get_loc("Player") + 3, "TeamName", home_team_name if is_home else away_team_name)
                df.insert(df.columns.get_loc("Player") + 4, "Is_Home", 1 if is_home else 0)
                df.insert(df.columns.get_loc("Player") + 5, "Opp", away_team if is_home else home_team)
                df.insert(df.columns.get_loc("Player") + 6, "OppName", away_team_name if is_home else home_team_name)
                
                for col in ["PTS", "REB", "AST", "STL", "BLK", "TOV"]:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) 
                    
                df["BLK_STL"] = df["BLK"] + df["STL"]
                df["REB_AST"] = df["REB"] + df["AST"]
                df["PTS_AST"] = df["PTS"] + df["AST"]
                df["PTS_REB"] = df["PTS"] + df["REB"]
                df["PTS_REB_AST"] = df["PTS"] + df["REB"] + df["AST"]
                df["FANTASY"] = (df["PTS"] * 1) + (df["REB"] * 1.2) + (df["AST"] * 1.5) + (df["BLK"] * 3) + (df["STL"] * 3) - (df["TOV"] * 1)

                df = df.reindex(columns=player_columns, fill_value=None)

                boxscore_data.append(df)

        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for game ID {game_id}: {e}")
    except Exception as e:
        print(f"Error processing data for game ID {game_id}: {e}")

if boxscore_data:
    boxscore_df = pd.concat(boxscore_data, ignore_index=True)
    gamelog_columns = [
        "Season", "GameID", "Date", "Game", "Player", "PlayerID", "Gm#", "Team", "TeamName", "Is_Home", "Opp", "PTS", "REB", "AST", "STL", "BLK", "TOV", "MP", "OffREB", "DefREB", "FG", "FGA", "3P", "3PA", "FT", "FTA", "PF", "BLK_STL", "REB_AST", "PTS_AST", "PTS_REB", "PTS_REB_AST", "FANTASY"
    ]
    
    boxscore_df = boxscore_df.reindex(columns=gamelog_columns)

metrics_file_path = r"C:\Users\ashle\Documents\Projects\basketball\data\gamelogs.csv"
if os.path.exists(metrics_file_path):
    metrics_data = pd.read_csv(metrics_file_path, parse_dates=["Date"], low_memory=False)
else:
    metrics_data = pd.DataFrame(columns=["PlayerID", "Gm#", "Date"])

boxscore_df["Date"] = pd.to_datetime(boxscore_df["Date"], errors="coerce")
boxscore_df.sort_values(by=["PlayerID", "Date"], inplace=True)

max_game_nums = metrics_data.groupby("PlayerID")["Gm#"].max().fillna(0).to_dict()

def assign_game_number(row):
    player_id = row["PlayerID"]
    if player_id in max_game_nums:
        return max_game_nums[player_id] + 1 + boxscore_df[
            (boxscore_df["PlayerID"] == player_id) & (boxscore_df["Date"] < row["Date"])
        ].shape[0]
    else:
        return boxscore_df[(boxscore_df["PlayerID"] == player_id)].groupby("PlayerID").cumcount().loc[row.name] + 1

boxscore_df["Gm#"] = boxscore_df.apply(assign_game_number, axis=1)

player_info = {
    "adamsst01": ("Steven Adams"),
    "adebaba01": ("Bam Adebayo"),
    "agbajoc01": ("Ochai Agbaji"),
    "aldamsa01": ("Santi Aldama"),
    "alexani01": ("Nickeil Alexander-Walker"),
    "alexatr01": ("Trey Alexander"),
    "allengr01": ("Grayson Allen"),
    "allenja01": ("Jarrett Allen"),
    "alvarjo01": ("Jose Alvarado"),
    "anderky01": ("Kyle Anderson"),
    "antetgi01": ("Giannis Antetokounmpo"),
    "anthoco01": ("Cole Anthony"),
    "anunoog01": ("OG Anunoby"),
    "avdijde01": ("Deni Avdija"),
    "aytonde01": ("Deandre Ayton"),
    "baglema01": ("Marvin Bagley III"),
    "baldwpa01": ("Patrick Baldwin Jr."),
    "ballla01": ("LaMelo Ball"),
    "balllo01": ("Lonzo Ball"),
    "banchpa01": ("Paolo Banchero"),
    "banede01": ("Desmond Bane"),
    "bantoda01": ("Dalano Banton"),
    "barlodo01": ("Dominick Barlow"),
    "barneha02": ("Harrison Barnes"),
    "barnesc01": ("Scottie Barnes"),
    "barrerj01": ("RJ Barrett"),
    "bassech01": ("Charles Bassey"),
    "battlja01": ("Jamison Battle"),
    "batumni01": ("Nicolas Batum"),
    "bealbr01": ("Bradley Beal"),
    "beaslma01": ("Malik Beasley"),
    "beaucma01": ("MarJon Beauchamp"),
    "beekmre01": ("Reece Beekman"),
    "bitadgo01": ("Goga Bitadze"),
    "blackan01": ("Anthony Black"),
    "bogdabo01": ("Bogdan Bogdanovic"),
    "bonaad01": ("Adem Bona"),
    "bookede01": ("Devin Booker"),
    "bostobr01": ("Brandon Boston"),
    "bouchch01": ("Chris Boucher"),
    "branhma01": ("Malaki Branham"),
    "braunch01": ("Christian Braun"),
    "bridgja01": ("Jalen Bridges"),
    "bridgmi01": ("Mikal Bridges"),
    "bridgmi02": ("Miles Bridges"),
    "brookdi01": ("Dillon Brooks"),
    "brownja02": ("Jaylen Brown"),
    "brownko01": ("Kobe Brown"),
    "brunsja01": ("Jalen Brunson"),
    "bryanth01": ("Thomas Bryant"),
    "bufkiko01": ("Kobe Bufkin"),
    "burksal01": ("Alec Burks"),
    "butleja02": ("Jared Butler"),
    "butleji01": ("Jimmy Butler"),
    "buzelma01": ("Matas Buzelis"),
    "cainja01": ("Jamal Cain"),
    "caldwke01": ("Kentavious Caldwell-Pope"),
    "camarto01": ("Toumani Camara"),
    "cancavl01": ("Vlatko Cancar"),
    "capelca01": ("Clint Capela"),
    "carrica01": ("Carlton Carrington"),
    "carteje01": ("Jevon Carter"),
    "cartewe01": ("Wendell Carter Jr."),
    "cartodj01": ("D.J. Carton"),
    "carusal01": ("Alex Caruso"),
    "castlco01": ("Colin Castleton"),
    "castlst01": ("Stephon Castle"),
    "champju01": ("Justin Champagnie"),
    "champju02": ("Julian Champagnie"),
    "chomcul01": ("Ulrich Chomche"),
    "chrisma02": ("Max Christie"),
    "cissosi01": ("Sidy Cissoko"),
    "clarkbr01": ("Brandon Clarke"),
    "clarkjo01": ("Jordan Clarkson"),
    "claxtni01": ("Nicolas Claxton"),
    "clingdo01": ("Donovan Clingan"),
    "clownno01": ("Noah Clowney"),
    "coffeam01": ("Amir Coffey"),
    "colliis01": ("Isaiah Collier"),
    "collijo01": ("John Collins"),
    "colliza01": ("Zach Collins"),
    "conlemi01": ("Mike Conley"),
    "connapa01": ("Pat Connaughton"),
    "coulibi01": ("Bilal Coulibaly"),
    "councri01": ("Ricky Council IV"),
    "craigto01": ("Torrey Craig"),
    "cuiyo01": ("Yongxi Cui"),
    "cunnica01": ("Cade Cunningham"),
    "curryse01": ("Seth Curry"),
    "curryst01": ("Stephen Curry"),
    "dadiepa01": ("Pacome Dadiet"),
    "daniedy01": ("Dyson Daniels"),
    "dasiltr01": ("Tristan Da Silva"),
    "davisan02": ("Anthony Davis"),
    "davisjd01": ("JD Davison"),
    "davisjo06": ("Johnny Davis"),
    "derozde01": ("DeMar DeRozan"),
    "diabamo01": ("Moussa Diabate"),
    "dickgr01": ("Gradey Dick"),
    "diengou01": ("Ousmane Dieng"),
    "dilliro01": ("Rob Dillingham"),
    "dinwisp01": ("Spencer Dinwiddie"),
    "divindo01": ("Donte DiVincenzo"),
    "doncilu01": ("Luka Doncic"),
    "dortlu01": ("Luguentz Dort"),
    "dosunay01": ("Ayo Dosunmu"),
    "dowtije01": ("Jeff Dowtin"),
    "doziepj01": ("PJ Dozier"),
    "drumman01": ("Andre Drummond"),
    "duartch01": ("Chris Duarte"),
    "ducasal01": ("Alex Ducas"),
    "dukeda01": ("David Duke Jr."),
    "dunnkr01": ("Kris Dunn"),
    "dunnry01": ("Ryan Dunn"),
    "duranke01": ("Kevin Durant"),
    "durenja01": ("Jalen Duren"),
    "easonta01": ("Tari Eason"),
    "edeyza01": ("Zach Edey"),
    "edwaran01": ("Anthony Edwards"),
    "edwarke02": ("Kessler Edwards"),
    "elliske01": ("Keon Ellis"),
    "embiijo01": ("Joel Embiid"),
    "eubandr01": ("Drew Eubanks"),
    "fernabr01": ("Bruno Fernando"),
    "filipky01": ("Kyle Filipowski"),
    "finnedo01": ("Dorian Finney-Smith"),
    "flaglad01": ("Adam Flagler"),
    "fontesi01": ("Simone Fontecchio"),
    "foxde01": ("De'Aaron Fox"),
    "freemen01": ("Enrique Freeman"),
    "furphjo01": ("Johnny Furphy"),
    "gaffoda01": ("Daniel Gafford"),
    "garlada01": ("Darius Garland"),
    "garzalu01": ("Luka Garza"),
    "georgke01": ("Keyonte George"),
    "georgky01": ("Kyshawn George"),
    "georgpa01": ("Paul George"),
    "gibsota01": ("Taj Gibson"),
    "giddejo01": ("Josh Giddey"),
    "gilgesh01": ("Shai Gilgeous-Alexander"),
    "gillan01": ("Anthony Gill"),
    "gilleco01": ("Collin Gillespie"),
    "goberru01": ("Rudy Gobert"),
    "gordoaa01": ("Aaron Gordon"),
    "gordoer01": ("Eric Gordon"),
    "gortmja01": ("Jazian Gortman"),
    "grantje01": ("Jerami Grant"),
    "greenaj01": ("A.J. Green"),
    "greendr01": ("Draymond Green"),
    "greenja02": ("Javonte Green"),
    "greenja05": ("Jalen Green"),
    "greenje02": ("Jeff Green"),
    "greenjo02": ("Josh Green"),
    "grimequ01": ("Quentin Grimes"),
    "gueyemo02": ("Mouhamed Gueye"),
    "hachiru01": ("Rui Hachimura"),
    "halibty01": ("Tyrese Haliburton"),
    "hardati02": ("Tim Hardaway Jr."),
    "hardeja01": ("James Harden"),
    "hardyja02": ("Jaden Hardy"),
    "harriga01": ("Gary Harris"),
    "harrito02": ("Tobias Harris"),
    "hartjo01": ("Josh Hart"),
    "hausesa01": ("Sam Hauser"),
    "hawkijo01": ("Jordan Hawkins"),
    "hayesja02": ("Jaxson Hayes"),
    "hendesc01": ("Scoot Henderson"),
    "hendrita0": ("Taylor Hendricks"),
    "herroty01": ("Tyler Herro"),
    "hieldbu01": ("Buddy Hield"),
    "highsha01": ("Haywood Highsmith"),
    "holidaa01": ("Aaron Holiday"),
    "holidjr01": ("Jrue Holiday"),
    "hollaro01": ("Ron Holland"),
    "holmeri01": ("Richaun Holmes"),
    "holmgch01": ("Chet Holmgren"),
    "hoodsja01": ("Jalen Hood-Schifino"),
    "horfoal01": ("Al Horford"),
    "hortota01": ("Talen Horton-Tucker"),
    "houstca01": ("Caleb Houstan"),
    "howarje01": ("Jett Howard"),
    "huertke01": ("Kevin Huerter"),
    "huffja01": ("Jay Huff"),
    "hukpoar01": ("Ariel Hukporti"),
    "huntede01": ("De'Andre Hunter"),
    "hylanbo01": ("Bones Hyland"),
    "ighodos01": ("Oso Ighodaro"),
    "inglejo01": ("Joe Ingles"),
    "ingrabr01": ("Brandon Ingram"),
    "ingraha01": ("Harrison Ingram"),
    "irvinky01": ("Kyrie Irving"),
    "isaacjo01": ("Jonathan Isaac"),
    "iveyja01": ("Jaden Ivey"),
    "jacksan01": ("Andre Jackson Jr."),
    "jacksis01": ("Isaiah Jackson"),
    "jacksja02": ("Jaren Jackson Jr."),
    "jacksqu01": ("Quenton Jackson"),
    "jacksre01": ("Reggie Jackson"),
    "jackstr02": ("Trayce Jackson-Davis"),
    "jamesbr02": ("Bronny James"),
    "jamesle01": ("LeBron James"),
    "jaqueja01": ("Jaime Jaquez Jr."),
    "jemistr01": ("Trey Jemison"),
    "jenkida01": ("Daniss Jenkins"),
    "jeromty01": ("Ty Jerome"),
    "joeis01": ("Isaiah Joe"),
    "johnsaj01": ("AJ Johnson"),
    "johnsca02": ("Cameron Johnson"),
    "johnsja01": ("James Johnson"),
    "johnsja05": ("Jalen Johnson"),
    "johnske04": ("Keldon Johnson"),
    "johnske07": ("Keon Johnson"),
    "jokicni01": ("Nikola Jokic"),
    "jonesco02": ("Colby Jones"),
    "jonesde02": ("Derrick Jones Jr."),
    "jonesdi01": ("Dillon Jones"),
    "joneshe01": ("Herbert Jones"),
    "jonesis01": ("Isaac Jones"),
    "joneska01": ("Kai Jones"),
    "jonesma05": ("Mason Jones"),
    "jonessp01": ("Spencer Jones"),
    "jonestr01": ("Tre Jones"),
    "jonesty01": ("Tyus Jones"),
    "jordade01": ("DeAndre Jordan"),
    "josepco01": ("Cory Joseph"),
    "jovicni01": ("Nikola Jovic"),
    "juzanjo01": ("Johnny Juzang"),
    "kawamyu01": ("Yuki Kawamura"),
    "kennalu01": ("Luke Kennard"),
    "kesslwa01": ("Walker Kessler"),
    "kispeco01": ("Corey Kispert"),
    "klebima01": ("Maxi Kleber"),
    "knechda01": ("Dalton Knecht"),
    "kolekty01": ("Tyler Kolek"),
    "kolokch01": ("Christian Koloko"),
    "konchjo01": ("John Konchar"),
    "kornelu01": ("Luke Kornet"),
    "krejcvi01": ("Vit Krejci"),
    "kuminjo01": ("Jonathan Kuminga"),
    "kuzmaky01": ("Kyle Kuzma"),
    "landajo01": ("Jock Landale"),
    "laravja01": ("Jake LaRavia"),
    "larsspe01": ("Pelle Larsson"),
    "lavinza01": ("Zach LaVine"),
    "leeda03": ("Damion Lee"),
    "lenal01": ("Alex Len"),
    "leonsma01": ("Malevy Leons"),
    "leverca01": ("Caris LeVert"),
    "lewisma05": ("Maxwell Lewis"),
    "lillada01": ("Damian Lillard"),
    "livelde01": ("Dereck Lively II"),
    "livinch01": ("Chris Livingston"),
    "looneke01": ("Kevon Looney"),
    "lopezbr01": ("Brook Lopez"),
    "loveke01": ("Kevin Love"),
    "lowryky01": ("Kyle Lowry"),
    "lylestr01": ("Trey Lyles"),
    "mamuksa01": ("Sandro Mamukelashvili"),
    "mannte01": ("Terance Mann"),
    "manntr01": ("Tre Mann"),
    "markkla01": ("Lauri Markkanen"),
    "marshna01": ("Naji Marshall"),
    "martica02": ("Caleb Martin"),
    "martico01": ("Cody Martin"),
    "martija02": ("Jaylen Martin"),
    "martike04": ("KJ Martin"),
    "martity01": ("Tyrese Martin"),
    "mathega01": ("Garrison Mathews"),
    "mathube01": ("Bennedict Mathurin"),
    "matkoka01": ("Karlo Matkovic"),
    "maxeyty01": ("Tyrese Maxey"),
    "mcbrimi01": ("Miles McBride"),
    "mccaija01": ("Jared McCain"),
    "mccluma01": ("Mac McClung"),
    "mccolcj01": ("CJ McCollum"),
    "mccontj01": ("T.J. McConnell"),
    "mcdanja02": ("Jaden McDaniels"),
    "mcderdo01": ("Doug McDermott"),
    "mclaujo01": ("Jordan McLaughlin"),
    "mcveija01": ("Jack McVeigh"),
    "meltode01": ("De'Anthony Melton"),
    "merrisa01": ("Sam Merrill"),
    "micicva01": ("Vasilije Micic"),
    "millebr02": ("Brandon Miller"),
    "millejo02": ("Jordan Miller"),
    "millspa02": ("Patty Mills"),
    "miltosh01": ("Shake Milton"),
    "minixri01": ("Riley Minix"),
    "minotjo01": ("Josh Minott"),
    "missiyv01": ("Yves Missi"),
    "mitchaj01": ("Ajay Mitchell"),
    "mitchda01": ("Davion Mitchell"),
    "mitchdo01": ("Donovan Mitchell"),
    "mobleev01": ("Evan Mobley"),
    "mogbojo01": ("Jonathan Mogbo"),
    "monkma01": ("Malik Monk"),
    "moodymo01": ("Moses Moody"),
    "moorewe01": ("Wendell Moore Jr."),
    "moranja01": ("Ja Morant"),
    "morrima02": ("Markieff Morris"),
    "morrimo01": ("Monte Morris"),
    "murphtr02": ("Trey Murphy III"),
    "murrade01": ("Dejounte Murray"),
    "murraja01": ("Jamal Murray"),
    "murrake02": ("Keegan Murray"),
    "murrakr01": ("Kris Murray"),
    "mykhasv01": ("Svi Mykhailiuk"),
    "nancela02": ("Larry Nance Jr."),
    "nembhan01": ("Andrew Nembhard"),
    "nesmiaa01": ("Aaron Nesmith"),
    "niangge01": ("Georges Niang"),
    "nnajize01": ("Zeke Nnaji"),
    "nowelja01": ("Jaylen Nowell"),
    "nurkiju01": ("Jusuf Nurkic"),
    "okogijo01": ("Josh Okogie"),
    "okongon01": ("Onyeka Okongwu"),
    "okorois01": ("Isaac Okoro"),
    "onealro01": ("Royce O'Neale"),
    "oubreke01": ("Kelly Oubre Jr."),
    "paulch01": ("Chris Paul"),
    "payneca01": ("Cameron Payne"),
    "paytoga02": ("Gary Payton II"),
    "peterdr01": ("Drew Peterson"),
    "phillju01": ("Julian Phillips"),
    "pickeja02": ("Jalen Pickett"),
    "pippesc02": ("Scotty Pippen Jr."),
    "plumlma01": ("Mason Plumlee"),
    "podzibr01": ("Brandin Podziemski"),
    "poeltja01": ("Jakob Poeltl"),
    "poolejo01": ("Jordan Poole"),
    "portecr01": ("Craig Porter Jr."),
    "porteke02": ("Kevin Porter Jr."),
    "portemi01": ("Michael Porter Jr."),
    "portibo01": ("Bobby Portis"),
    "poweldw01": ("Dwight Powell"),
    "powelno01": ("Norman Powell"),
    "princta02": ("Taurean Prince"),
    "pritcpa01": ("Payton Pritchard"),
    "prospol01": ("Olivier-Maxence Prosper"),
    "queentr01": ("Trevelin Queen"),
    "quetane01": ("Neemias Queta"),
    "quickim01": ("Immanuel Quickley"),
    "quinole01": ("Lester Quinones"),
    "randlju01": ("Julius Randle"),
    "reathdu01": ("Duop Reath"),
    "reaveau01": ("Austin Reaves"),
    "reddica01": ("Cam Reddish"),
    "reedpa01": ("Paul Reed"),
    "reeseal01": ("Alex Reese"),
    "reevean01": ("Antonio Reeves"),
    "reidna01": ("Naz Reid"),
    "rhodeja01": ("Jared Rhoden"),
    "richajo01": ("Josh Richardson"),
    "richani01": ("Nick Richards"),
    "risacza01": ("Zaccharie Risacher"),
    "robbili01": ("Liam Robbins"),
    "robindu01": ("Duncan Robinson"),
    "robinje02": ("Jeremiah Robinson-Earl"),
    "roddyda01": ("David Roddy"),
    "rolliry01": ("Ryan Rollins"),
    "roziete01": ("Terry Rozier"),
    "ruperra01": ("Rayan Rupert"),
    "russeda01": ("D'Angelo Russell"),
    "ryanma01": ("Matt Ryan"),
    "sabondo01": ("Domantas Sabonis"),
    "salauti01": ("Tidjane Salaun"),
    "sanogad01": ("Adama Sanogo"),
    "santogu01": ("Gui Santos"),
    "saricda01": ("Dario Saric"),
    "sarral01": ("Alex Sarr"),
    "sassema01": ("Marcus Sasser"),
    "scheiba01": ("Baylor Scheierman"),
    "schrode01": ("Dennis Schroder"),
    "sengual01": ("Alperen Sengun"),
    "sensabr01": ("Brice Sensabaugh"),
    "sextoco01": ("Collin Sexton"),
    "shannte01": ("Terrence Shannon Jr."),
    "sharpsh01": ("Shaedon Sharpe"),
    "sheadja01": ("Jamal Shead"),
    "sheppbe01": ("Ben Sheppard"),
    "sheppre01": ("Reed Sheppard"),
    "siakapa01": ("Pascal Siakam"),
    "simmobe01": ("Ben Simmons"),
    "simonan01": ("Anfernee Simons"),
    "simpskj01": ("KJ Simpson"),
    "simsje01": ("Jericho Sims"),
    "smartma01": ("Marcus Smart"),
    "smithdr01": ("Dru Smith"),
    "smithja04": ("Jalen Smith"),
    "smithja05": ("Jabari Smith Jr."),
    "smithni01": ("Nick Smith Jr."),
    "smithty02": ("Tyler Smith"),
    "sochaje01": ("Jeremy Sochan"),
    "spencpa01": ("Pat Spencer"),
    "sprinja01": ("Jaden Springer"),
    "stewais01": ("Isaiah Stewart"),
    "strawju01": ("Julian Strawther"),
    "suggsja01": ("Jalen Suggs"),
    "swideco01": ("Cole Swider"),
    "tateja01": ("Jae'Sean Tate"),
    "tatumja01": ("Jayson Tatum"),
    "templga01": ("Garrett Temple"),
    "terryda01": ("Dalen Terry"),
    "theisda01": ("Daniel Theis"),
    "thomaca02": ("Cam Thomas"),
    "thompam01": ("Amen Thompson"),
    "thompkl01": ("Klay Thompson"),
    "thomptr01": ("Tristan Thompson"),
    "tillmxa01": ("Xavier Tillman Sr."),
    "toppija01": ("Jacob Toppin"),
    "toppiob01": ("Obi Toppin"),
    "townska01": ("Karl-Anthony Towns"),
    "travelu01": ("Luke Travers"),
    "trentga02": ("Gary Trent Jr."),
    "turnemy01": ("Myles Turner"),
    "tysonhu01": ("Hunter Tyson"),
    "tysonja01": ("Jaylon Tyson"),
    "umudest01": ("Stanley Umude"),
    "valanjo01": ("Jonas Valanciunas"),
    "vanvlfr01": ("Fred VanVleet"),
    "vassede01": ("Devin Vassell"),
    "vincega01": ("Gabe Vincent"),
    "vucevni01": ("Nikola Vucevic"),
    "wadede01": ("Dean Wade"),
    "wagnefr01": ("Franz Wagner"),
    "wagnemo01": ("Moritz Wagner"),
    "walkeja01": ("Jabari Walker"),
    "walkeja02": ("Jarace Walker"),
    "wallaca01": ("Cason Wallace"),
    "wallake01": ("Keaton Wallace"),
    "walshjo01": ("Jordan Walsh"),
    "walteja01": ("Ja'Kobe Walter"),
    "wareke01": ("Kel'el Ware"),
    "washipj01": ("P.J. Washington"),
    "waterli01": ("Lindy Waters III"),
    "watsope01": ("Peyton Watson"),
    "wellsja01": ("Jaylen Wells"),
    "wembavi01": ("Victor Wembanyama"),
    "weslebl01": ("Blake Wesley"),
    "westbru01": ("Russell Westbrook"),
    "whiteco01": ("Coby White"),
    "whiteda01": ("Dariq Whitehead"),
    "whitede01": ("Derrick White"),
    "whitmca01": ("Cam Whitmore"),
    "wiggiaa01": ("Aaron Wiggins"),
    "wiggian01": ("Andrew Wiggins"),
    "willibr03": ("Brandon Williams"),
    "willico04": ("Cody Williams"),
    "willigr01": ("Grant Williams"),
    "willija06": ("Jalen Williams"),
    "willije02": ("Jeenathan Williams"),
    "willike04": ("Kenrich Williams"),
    "willipa01": ("Patrick Williams"),
    "williro04": ("Robert Williams"),
    "willizi01": ("Zion Williamson"),
    "willizi02": ("Ziaire Williams"),
    "wilsoja03": ("Jalen Wilson"),
    "wisemja01": ("James Wiseman"),
    "wrighde01": ("Delon Wright"),
    "yabusgu01": ("Guerschon Yabusele"),
    "youngtr01": ("Trae Young"),
    "zubaciv01": ("Ivica Zubac"),
    "liddeej01": ("E.J. Liddell"),
    "washity02": ("TyTy Washington Jr."),
    "bolbo01": ("Bol Bol"),
    "willivi01": ("Vince Williams Jr."),
    "armeltr01": ("Armel Traore"),
    "robinor01": ("Orlando Robinson"),
    "thorjt01": ("JT Thor"),
    "hallpj01": ("PJ Hall"),
    "brogdma01": ("Malcolm Brogdon"),
    "watfotr01": ("Trendon Watford"),
    "bambamo01": ("Mo Bamba"),
    "willial06": ("Alondes Williams"),
    "mooreta02": ("Taze Moore"),
    "harteis01": ("Isaiah Hartenstein"),
    "brownmo01": ("Moses Brown"),
    "newtotr01": ("Tristen Newton"),
    "paytoel01": ("Elfrid Payton"),
    "spencca01": ("Cam Spencer"),
    "edwarju01": ("Justin Edwards"),
    "porzikr01": ("Kristaps Porzingis"),
    "thompau01": ("Ausar Thompson"),
    "minayju01": ("Justin Minaya"),
    "carlsbr01": ("Branden Carlson")
}

boxscore_df["Player"] = boxscore_df["PlayerID"].map(player_info).fillna(boxscore_df["Player"])

final_gamelogs_path = os.path.join(base_path, "gamelogs1.csv")
boxscore_df.to_csv(final_gamelogs_path, mode='a', index=False, encoding="utf-8")
print(f"Updated gamelogs saved to {final_gamelogs_path}")

game_index_data = (
    boxscore_df.groupby(["GameID", "Season", "Date", "Game", "Team", "Is_Home", "TeamName"])
    .agg({"PTS": "sum"})
    .reset_index()
)

home_data = game_index_data[game_index_data["Is_Home"] == 1].rename(
    columns={"Team": "HomeID", "PTS": "PTS", "TeamName": "Home"}
)
away_data = game_index_data[game_index_data["Is_Home"] == 0].rename(
    columns={"Team": "AwayID", "PTS": "PTSA", "TeamName": "Away"}
)

game_index = pd.merge(
    home_data[["GameID", "Season", "Date", "Game", "Home", "HomeID", "PTS"]],
    away_data[["GameID", "Away", "AwayID", "PTSA"]],
    on="GameID",
    how="inner"
)

game_index = game_index[
    ["Season", "Date", "Game", "GameID", "Home", "HomeID", "PTS", "Away", "AwayID", "PTSA"]
]

game_index_file_path = os.path.join(base_path, "gameindex1.csv")
game_index.to_csv(game_index_file_path, mode='a', index=False, encoding="utf-8")
print(f"Game index saved to {game_index_file_path}")

team_stats = (
    boxscore_df.groupby(["GameID", "Team", "Is_Home", "TeamName", "Opp"])
    .agg({
        "PTS": "sum",
        "REB": "sum",
        "AST": "sum",
        "STL": "sum",
        "BLK": "sum"
    })
    .reset_index()
)

opponent_stats = team_stats.rename(
    columns={
        "PTS": "PTSA", "REB": "REBA", "AST": "ASTA", "STL": "STLA", "BLK": "BLKA",
        "Team": "OppID", "TeamName": "OppName"
    }
)

team_gamelogs = pd.merge(
    team_stats,
    opponent_stats[["GameID", "OppID", "PTSA", "REBA", "ASTA", "STLA", "BLKA"]],
    left_on=["GameID", "Opp"],
    right_on=["GameID", "OppID"],
    how="inner"
)

team_gamelogs = team_gamelogs.drop(columns=["OppID"])

game_info = boxscore_df[["GameID", "Season", "Date"]].drop_duplicates()
team_gamelogs = pd.merge(team_gamelogs, game_info, on="GameID", how="left")

team_gamelogs = team_gamelogs.rename(columns={"TeamName": "Team", "Team": "TeamID"})
team_gamelogs = team_gamelogs[
    [
        "Season", "Date", "GameID", "Team", "TeamID", "Is_Home", "Opp", "PTS", "REB", "AST", "STL", "BLK", "PTSA", "REBA", "ASTA", "STLA", "BLKA"
    ]
]

team_gamelogs_file_path = os.path.join(base_path, "teamgamelogs1.csv")
team_gamelogs.to_csv(team_gamelogs_file_path, mode='a', index=False, encoding="utf-8")
print(f"Team gamelogs saved to {team_gamelogs_file_path}")

conferences = ["E", "W"]
years = ["2025"]

stats_columns = ['Team', 'GP', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'OffREB', 'DefREB', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'FT', 'FTA', 'FT%','PF']

standings_columns = ["Conference", "Team", "W", "L", "GB"]

final_columns = ['Conference', 'Rk', 'TeamID', 'Team', 'GP', 'W', 'L', 'GB', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'OffREB', 'DefREB', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'FT', 'FTA', 'FT%', 'PF']

team_info = {
    "Atlanta Hawks": ("Eastern", "ATL"),
    "Boston Celtics": ("Eastern", "BOS"),
    "Brooklyn Nets": ("Eastern", "BRK"),
    "Charlotte Hornets": ("Eastern", "CHO"),
    "Chicago Bulls": ("Eastern", "CHI"),
    "Cleveland Cavaliers": ("Eastern", "CLE"),
    "Dallas Mavericks": ("Western", "DAL"),
    "Denver Nuggets": ("Western", "DEN"),
    "Detroit Pistons": ("Eastern", "DET"),
    "Golden State Warriors": ("Western", "GSW"),
    "Houston Rockets": ("Western", "HOU"),
    "Indiana Pacers": ("Eastern", "IND"),
    "Los Angeles Clippers": ("Western", "LAC"),
    "Los Angeles Lakers": ("Western", "LAL"),
    "Memphis Grizzlies": ("Western", "MEM"),
    "Miami Heat": ("Eastern", "MIA"),
    "Milwaukee Bucks": ("Eastern", "MIL"),
    "Minnesota Timberwolves": ("Western", "MIN"),
    "New Orleans Pelicans": ("Western", "NOP"),
    "New York Knicks": ("Eastern", "NYK"),
    "Oklahoma City Thunder": ("Western", "OKC"),
    "Orlando Magic": ("Eastern", "ORL"),
    "Philadelphia 76ers": ("Eastern", "PHI"),
    "Phoenix Suns": ("Western", "PHO"),
    "Portland Trail Blazers": ("Western", "POR"),
    "Sacramento Kings": ("Western", "SAC"),
    "San Antonio Spurs": ("Western", "SAS"),
    "Toronto Raptors": ("Eastern", "TOR"),
    "Utah Jazz": ("Western", "UTA"),
    "Washington Wizards": ("Eastern", "WAS")
}

def fetch_and_parse(driver, url):
    driver.get(url)
    time.sleep(random.uniform(5, 10))
    return BeautifulSoup(driver.page_source, "html.parser")

stats_data = []

for year in years:
    url = f"https://www.basketball-reference.com/leagues/NBA_2025.html" 
    print(f"Processing {year}...")
    try:
        soup = fetch_and_parse(driver, url)
        table = soup.select_one("#totals-team")
        if table:
            header_row = table.select("thead tr")[0]
            headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

            rows = table.select("tbody tr")
            
            valid_rows = [
                row for row in rows
                if len(row.find_all("td")) > 0
            ]
            
            consolidated_html = '<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>'.format(
                ''.join(f'<th>{header}</th>' for header in headers),
                ''.join(str(row) for row in valid_rows)
            )
            df = pd.read_html(StringIO(consolidated_html), encoding="utf-8")[0]
            df.columns = headers
            
            column_mapping = {
                "G": "GP",
                "ORB": "OffREB",
                "DRB": "DefREB",
                "TRB": "REB"
            }
            
            column_names = list(df.columns)
            for i, col in enumerate(column_names):
                if col == "G":
                    column_names[i] = column_mapping["G"]
                elif col == "ORB":
                    column_names[i] = column_mapping["ORB"]
                elif col == "DRB":
                    column_names[i] = column_mapping["DRB"]
                elif col == "TRB":
                    column_names[i] = column_mapping["TRB"]
            df.columns = column_names    
            

            df = df[['Team', 'GP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'FT', 'FTA', 'FT%','OffREB', 'DefREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']]
            
            df = df.reindex(columns=stats_columns, fill_value=None)
            
        stats_data.append(df)

    except Exception as e:
        print(f"Error processing {year}: {e}")

driver.quit()

standings_data = []

for conference in conferences:
    url = f"https://www.basketball-reference.com/leagues/NBA_2025.html"
    
    try:
        print(f"Processing standings for conference {conference}...")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        table_selector = f"#confs_standings_{conference}"
        table = soup.select_one(table_selector)
        
        if table:
            header_row = table.select("thead tr")[0]
            headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
            
            conf_name = headers[0]
            
            rows = table.select("tbody tr:not([class='thead'])")
            
            consolidated_rows = []
            for row in rows:
                if "Division" in row.get_text(strip=True):
                    continue
                consolidated_rows.append(row)
            
            consolidated_html = '<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>'.format(
                ''.join(f'<th>{header}</th>' for header in headers),
                ''.join(str(row) for row in consolidated_rows)
            )
            
            df = pd.read_html(StringIO(consolidated_html), encoding="utf-8")[0]
            df.columns = headers
            
            column_mapping = {
                "Eastern Conference": "Team",
                "Western Conference": "Team",
            }
            
            df = df.rename(columns=column_mapping)                
            
            df = df[["Team", "W", "L", "GB"]] 
            
            df.insert(0, "Conference", conf_name)
            
            df = df.reindex(columns=standings_columns, fill_value=None)

            standings_data.append(df)

        time.sleep(3)

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"Error processing data: {e}")

if stats_data and standings_data:
    standings_df = pd.concat(standings_data, ignore_index=True)
    stats_df = pd.concat(stats_data, ignore_index=True)
    
    nbsp = u"\u00A0"  # Non-breaking space
    standings_df['Team'] = standings_df['Team'].str.split(nbsp).str[0]
    standings_df['GB'] = standings_df['GB'].replace('â€”', '0')
    standings_df['GB'] = standings_df['GB'].replace('—', '0')
    
    # Merge the standings and stats data
    merged_standings_df = standings_df.merge(stats_df, on="Team", how="left")
    
    merged_standings_df["Conference"] = merged_standings_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown"))[0])
    merged_standings_df["TeamID"] = merged_standings_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown"))[1])
    
    merged_standings_df.sort_values(by=["Conference", "W"], ascending=[True, False], inplace=True)
    merged_standings_df["Rk"] = merged_standings_df.groupby(["Conference"]).cumcount() + 1
    merged_standings_df = merged_standings_df[final_columns]
    
    merged_file_path = os.path.join(data_path, "teamStatsAndStandings.csv")
    merged_standings_df.to_csv(merged_file_path, index=False, encoding="utf-8")
    print(f"Merged data successfully saved to {merged_file_path}.")
else:
    print("Standings or stats data is missing, cannot merge.")
