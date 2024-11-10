import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time  # Import time for sleep function

# Base URL template for player game logs
base_url = "https://www.basketball-reference.com/players/{}.html"

# Path to the CSV file
csv_file_path = r"C:\Users\ashle\Documents\Projects\basketball\MultiTeamPlayers.csv"

# Function to fetch and parse the HTML table for a given username
def fetch_table(username):
    # Get the first letter of the username
    first_letter = username[0]
    url = base_url.format(f"{first_letter}/{username}")
    
    try:
        # Fetch the HTML content
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the player's name from either element
        name_element_h1 = soup.select_one('h1 > span')
        name_element_p = soup.select_one('p:-soup-contains("Full Name:")')
        
        # Find the table
        table = soup.select_one('#per_game_stats')
        if table is None:
            print(f"No table found for {username}")
            return None
        
        # Use pandas to read the HTML table into a DataFrame
        html_table = str(table)
        df = pd.read_html(StringIO(html_table), flavor='bs4')[0]
        df.insert(0, 'Player', username)  # Add user name to DataFrame
        
        return df
    except Exception as e:
        print(f"Error fetching table for {username}: {e}")
        return None

# Function to save DataFrames to CSV
def save_to_csv(dfs, file_path):
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")
    else:
        print("No data to save.")

# Main script
def main():
    usernames = [       
        "achiupr01", "adamsst01", "adebaba01", "agbajoc01", "aldamsa01", "alexani01", "alexatr01", "allengr01", "allenja01", "allenti01", "alvarjo01", "anderky01", "antetgi01", "antetth01", "anthoco01", "anunoog01", "arcidry01", "avdijde01", "aytonde01", "azubuud01", "badjiib01", "baglema01", "baileam01", "baldwpa01", "ballla01", "balllo01", "bambamo01", "banchpa01", "banede01", "bantoda01", "barlodo01", "barneha02", "barnesc01", "barrerj01", "bassech01", "batesem01", "battlja01", "batumni01", "bealbr01", "beaslma01", "beaucma01", "beekmre01", "bernaju01", "beysa01", "bitadgo01", "bitimon01", "blackan01", "blackle01", "boehebu01", "bogdabo01", "bolbo01", "bonaad01", "bookede01", "bostobr01", "bouchch01", "bouknja01", "branhma01", "braunch01", "bridgmi01", "bridgmi02", "brissos01", "brockiz01", "brogdma01", "brookar01", "brookdi01", "brownch02", "browngr01", "brownja02", "brownke03", "brownko01", "brownmo01", "brunsja01", "bryanth01", "bufkiko01", "bullore01", "burksal01", "butleja02", "butleji01", "buzelma01", "cainja01", "caldwke01", "camarto01", "cancavl01", "capelca01", "carrica01", "carteje01", "cartewe01", "cartodj01", "carusal01", "castlco01", "castlst01", "cazalma01", "champju01", "champju02", "chomcul01", "chrisma02", "cissosi01", "clarkbr01", "clarkjo01", "claxtni01", "clingdo01", "clownno01", "coffeam01", "collijo01", "colliza01", "conlemi01", "connapa01", "coulibi01", "councri01", "craigto01", "crowdja01", "crutcja01", "cuiyo01", "cunnica01", "curryse01", "curryst01", "dadiepa01", "daniedy01", "dasiltr01", "davisan02", "davisjd01", "davisjo06", "dennide01", "derozde01", "diabamo01", "diallha01", "dickgr01", "diengou01", "dilliro01", "dinwisp01", "divindo01", "doncilu01", "dortlu01", "dosunay01", "dowtije01", "doziepj01", "drellhe01", "drumman01", "duartch01", "ducasal01", "dukeda01", "dunnkr01", "dunnry01", "duranke01", "durenja01", "easonta01", "edeyza01", "edwaran01", "edwarke02", "elliske01", "embiijo01", "eubandr01", "exumda01", "fernabr01", "filipky01", "finnedo01", "flaglad01", "fontesi01", "fordjo01", "forretr01", "foxde01", "freemen01", "freemja01", "fultzma01", "funkan01", "furphjo01", "gabriwe01", "gaffoda01", "garlada01", "garubus01", "garzalu01", "gateska01", "georgke01", "georgky01", "georgpa01", "gibsota01", "giddejo01", "gilgesh01", "gillan01", "gilleco01", "goberru01", "gordoaa01", "gordoer01", "gortmja01", "grahade01", "grantje01", "grayra01", "greenaj01", "greenda02", "greendr01", "greenja02", "greenja05", "greenje02", "greenjo02", "griffaj01", "grimequ01", "gueyemo01", "gueyemo02", "hachiru01", "haganas01", "halibty01", "hamptrj01", "hardati02", "hardeja01", "hardyja02", "harpero02", "harriga01", "harrijo01", "harrike01", "harrish01", "harrito02", "harteis01", "hartjo01", "hausesa01", "hawkijo01", "hayesja02", "hayeski01", "hendesc01", "hendrita0", "herroty01", "hieldbu01", "highsha01", "hintona01", "hodgedm01", "holidaa01", "holidjr01", "holidju01", "hollaro01", "holmeri01", "holmgch01", "hoodsja01", "horfoal01", "hortota01", "houseda01", "houstca01", "howarje01", "huertke01", "huffja01", "hukpoar01", "huntede01", "hurtma01", "hylanbo01", "ighodos01", "inglejo01", "ingrabr01", "ingraha01", "irvinky01", "isaacjo01", "iveyja01", "jacksan01", "jacksgg01", "jacksis01", "jacksja02", "jacksju01", "jacksqu01", "jacksre01", "jackstr02", "jamesbr02", "jamesle01", "jaqueja01", "jarrede01", "jeffrda01", "jemistr01", "jenkida01", "jeromty01", "joeis01", "johnsaj01", "johnsca02", "johnsja01", "johnsja05", "johnske04", "johnske07", "johnske08", "jokicni01", "jonesco02", "jonesda03", "jonesde02", "jonesdi01", "joneshe01", "jonesis01", "joneska01", "jonesma05", "jonessp01", "jonestr01", "jonesty01", "jordade01", "josepco01", "jovicni01", "juzanjo01", "kawamyu01", "kennalu01", "kesslwa01", "keybr01", "kispeco01", "klebima01", "knechda01", "knoxke01", "kolekty01", "kolokch01", "konchjo01", "korkmfu01", "kornelu01", "krejcvi01", "kuminjo01", "kuzmaky01", "landajo01", "laravja01", "larsspe01", "lavinza01", "lawsoaj01", "leeda03", "leesa01", "lenal01", "leonaka01", "leonsma01", "leverca01", "lewisma05", "liddeej01", "lillada01", "littlna01", "livelde01", "liveris01", "livinch01", "looneke01", "lopezbr01", "lopezro01", "loveke01", "lowryky01", "lundyse01", "lylestr01", "mamuksa01", "mannte01", "manntr01", "marjabo01", "markkla01", "marshna01", "martica02", "martico01", "martija02", "martike04", "martity01", "mathega01", "mathube01", "matkoka01", "matthwe02", "maxeyty01", "mcbrimi01", "mccaija01", "mccluma01", "mccolcj01", "mccontj01", "mcdanja01", "mcdanja02", "mcderdo01", "mcgeeja01", "mcgowbr01", "mclaujo01", "mcveija01", "meltode01", "mensana01", "merrisa01", "micicva01", "middlkh01", "millebr02", "millejo02", "millele01", "millspa02", "miltosh01", "minayju01", "minixri01", "minotjo01", "missiyv01", "mitchaj01", "mitchda01", "mitchdo01", "mobleev01", "mobleis01", "mogbojo01", "monkma01", "moodymo01", "moonxa01", "mooreta02", "moorewe01", "moranja01", "morrima02", "morrimo01", "murphtr02", "murrade01", "murraja01", "murrake02", "murrakr01", "mykhasv01", "nancela02", "nancepe01", "nembhan01", "nesmiaa01", "niangge01", "nixda01", "nnajize01", "nowelja01", "nowelma01", "ntilila01", "nurkiju01", "okekech01", "okogijo01", "okongon01", "okorois01", "omorueu01", "onealro01", "osmande01", "oubreke01", "paulch01", "payneca01", "paytoga02", "pereima01", "peterdr01", "phillju01", "pickeja02", "pippesc02", "plumlma01", "podzibr01", "poeltja01", "poolejo01", "portecr01", "portejo01", "porteke02", "portemi01", "porteot01", "portibo01", "porzikr01", "pottemi01", "poweldw01", "powelno01", "prestja01", "primojo01", "princta02", "pritcpa01", "prospol01", "queentr01", "quetane01", "quickim01", "quinole01", "ramseja01", "randlju01", "reathdu01", "reaveau01", "reddica01", "reedpa01", "reeseal01", "reevean01", "reidna01", "rhodeja01", "richajo01", "richani01", "risacza01", "robbili01", "robindu01", "robinje01", "robinje02", "robinmi01", "robinor01", "roddyda01", "rolliry01", "rosede01", "roziete01", "ruperra01", "russeda01", "ryanma01", "sabondo01", "salauti01", "samanlu01", "samueje01", "sanogad01", "santogu01", "saricda01", "sarral01", "sarrol01", "sassema01", "scheiba01", "schofad01", "schrode01", "seabrde01", "sengual01", "sensabr01", "sextoco01", "shamela01", "shannte01", "sharpda01", "sharpsh01", "sheadja01", "sheppbe01", "sheppre01", "siakapa01", "simmobe01", "simmoko01", "simonan01", "simpskj01", "simpsza01", "simsje01", "skapidm01", "slawsja01", "smartja01", "smartma01", "smithde03", "smithdr01", "smithis01", "smithja04", "smithja05", "smithni01", "smithte01", "smithty02", "sochaje01", "spencpa01", "sprinja01", "stewais01", "strawju01", "strusma01", "suggsja01", "swideco01", "tateja01", "tatumja01", "taylote01", "templga01", "terryda01", "theisda01", "thomaca02", "thomais02", "thompam01", "thompau01", "thompkl01", "thomptr01", "thorjt01", "thybuma01", "tillmxa01", "toppija01", "toppiob01", "toscaju01", "townska01", "travelu01", "trentga02", "tshieos01", "turnemy01", "tysonhu01", "tysonja01", "umudest01", "valanjo01", "vandeja01", "vanvlfr01", "vassede01", "vezenal01", "vincega01", "vucevni01", "vukcetr01", "wadede01", "wagnefr01", "wagnemo01", "walkeja01", "walkeja02", "walkelo01", "wallaca01", "wallake01", "walshjo01", "walteja01", "wareke01", "warretj01", "washipj01", "washity02", "waterli01", "watfotr01", "watsope01", "wellsja01", "wembavi01", "weslebl01", "westbru01", "whiteco01", "whiteda01", "whitede01", "whiteja03", "whitmca01", "wiggiaa01", "wiggian01", "wiggili01", "willial06", "willibr03", "willico04", "willigr01", "willija06", "willija07", "willije02", "willike04", "willima07", "willima11", "willipa01", "williro04", "willivi01", "willizi01", "willizi02", "wilsodj01", "wilsoja03", "wisemja01", "wongis01", "woodch01", "wrighde01", "yabusgu01", "youngtr01", "yurtsom01", "zelleco01", "zubaciv01"
    ]

    dfs = []
    for username in usernames:
        print(f"Processing {username}...")
        df = fetch_table(username)
        if df is not None:
            dfs.append(df)
        
        # Wait for 3 seconds before making the next request
        time.sleep(3)
    
    save_to_csv(dfs, csv_file_path)

if __name__ == "__main__":
    main()
