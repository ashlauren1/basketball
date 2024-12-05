from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os

REQUESTS_PER_MINUTE = 20
ONE_MINUTE = 60

@sleep_and_retry
@limits(calls=REQUESTS_PER_MINUTE, period=ONE_MINUTE)
def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


base_path = r"C:\Users\ashle\Documents\Projects\basketball\data"

leaders_columns = [
    'Player', 'PlayerID', 'Age', 'TeamID', 'GP', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'OffREB', 'DefREB', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', '2P', '2PA', '2P%', 'PTS_GP', 'REB_GP', 'AST_GP', 'STL_GP', 'BLK_GP', 'MP_GP'
]

leaders_data = []

url = f"https://www.basketball-reference.com/leagues/NBA_2025_totals.html#totals_stats::pts"

try:
    html_content = fetch_webpage(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.select_one('#totals_stats')
    
    if table:
        headers = [th.get_text(strip=True) for th in table.select("thead tr")[0].find_all("th")]
        df = pd.read_html(StringIO(str(table)))[0]
        df.columns = headers
        df = df.iloc[:-1, :]
        
        valid_rows = [
            row for row in table.select("tbody tr")
            if not any(cls in (row.get("class") or []) for cls in ["over_header", "thead", "norank"])
            and "League Average" not in row.get_text(strip=True)
        ]

        # Rename columns and clean data
        column_mapping = {'Team': 'TeamID', 'G': 'GP', 'TRB': 'REB', 'ORB': 'OffREB', 'DRB': 'DefREB'}
        df.rename(columns=column_mapping, inplace=True)

        df = df[["Player", "Age", "TeamID", "GP", 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'OffREB', 'DefREB', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', '2P', '2PA', '2P%']]

        # Insert player IDs
        player_ids = [row.select_one("td[data-append-csv]").get("data-append-csv") for row in valid_rows if row.select_one("td[data-append-csv]")]
        df.insert(df.columns.get_loc("Player") + 1, "PlayerID", player_ids + [None] * (len(df) - len(player_ids)))

        # Add per-game stats
        for col in ['PTS', 'REB', 'AST', 'STL', 'BLK', 'MP']:
            df[f"{col}_GP"] = df[col] / df["GP"]
            df[f"{col}_GP"] = df[f"{col}_GP"].fillna(0)

        df = df.reindex(columns=leaders_columns, fill_value=None)
        leaders_data.append(df)

    time.sleep(3)  # Avoid rate limits

except requests.RequestException as e:
    print(f"Error fetching data: {e}")
except Exception as e:
    print(f"Error processing data: {e}")

# Process leaders_data
if not leaders_data:
    print("No leader data was extracted. Ensure the table exists and the HTML structure is correct.")
else:
    leaders_df = pd.concat(leaders_data, ignore_index=True)

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
    
    leaders_df["Player"] = leaders_df["PlayerID"].map(player_info).fillna(leaders_df["Player"])

    # Save to CSV
    leaders_path = os.path.join(base_path, "leaders.csv")
    leaders_df.to_csv(leaders_path, index=False, encoding="utf-8")
    print(f"Leaders saved to {leaders_path}")