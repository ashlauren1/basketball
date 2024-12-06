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
    "202412050CLE": ("CLE", "DEN"),
    "202412050WAS": ("WAS", "DAL"),
    "202412050NYK": ("NYK", "CHO"),
    "202412050TOR": ("TOR", "OKC"),
    "202412050MEM": ("MEM", "SAC"),
    "202412050NOP": ("NOP", "PHO"),
    "202412050SAS": ("SAS", "CHI"),
    "202412050GSW": ("GSW", "HOU")
}

#    "202412060PHI": ("PHI", "ORL"),
#    "202412060ATL": ("ATL", "LAL"),
#    "202412060BOS": ("BOS", "MIL"),
#    "202412060CHI": ("CHI", "IND"),
#    "202412060SAS": ("SAS", "SAC"),
#    "202412060GSW": ("GSW", "MIN"),
#    "202412060POR": ("POR", "UTA"),
#    "202412070CHO": ("CHO", "CLE"),
#    "202412070NOP": ("NOP", "OKC"),
#    "202412070WAS": ("WAS", "DEN"),
#    "202412070NYK": ("NYK", "DET"),
#    "202412070TOR": ("TOR", "DAL"),
#    "202412070BOS": ("BOS", "MEM"),
#    "202412070MIA": ("MIA", "PHO"),
#    "202412080CHI": ("CHI", "PHI"),
#    "202412080BRK": ("BRK", "MIL"),
#    "202412080IND": ("IND", "CHO"),
#    "202412080ATL": ("ATL", "DEN"),
#    "202412080MIA": ("MIA", "CLE"),
#    "202412080ORL": ("ORL", "PHO"),
#    "202412080SAS": ("SAS", "NOP"),
#    "202412080WAS": ("WAS", "MEM"),
#    "202412080GSW": ("GSW", "MIN"),
#    "202412080LAC": ("LAC", "HOU"),
#    "202412080SAC": ("SAC", "UTA"),
#    "202412080LAL": ("LAL", "POR"),
#    "202412090TOR": ("TOR", "NYK"),
#    "202412190DET": ("DET", "UTA"),
#    "202412190ORL": ("ORL", "OKC"),
#    "202412190WAS": ("WAS", "CHO"),
#    "202412190BOS": ("BOS", "CHI"),
#    "202412190TOR": ("TOR", "BRK"),
#    "202412190HOU": ("HOU", "NOP"),
#    "202412190MEM": ("MEM", "GSW"),
#    "202412190MIN": ("MIN", "NYK"),
#    "202412190DAL": ("DAL", "LAC"),
#    "202412190PHO": ("PHO", "IND"),
#    "202412190SAS": ("SAS", "ATL"),
#    "202412190POR": ("POR", "DEN"),
#    "202412190SAC": ("SAC", "LAL"),
#    "202412200PHI": ("PHI", "CHO"),
#    "202412200CLE": ("CLE", "MIL"),
#    "202412200MIA": ("MIA", "OKC"),
#    "202412210SAC": ("SAC", "LAL"),
#    "202412210ORL": ("ORL", "MIA"),
#    "202412210ATL": ("ATL", "MEM"),
#    "202412210BRK": ("BRK", "UTA"),
#    "202412210CHI": ("CHI", "BOS"),
#    "202412210CLE": ("CLE", "PHI"),
#    "202412210MIL": ("MIL", "WAS"),
#    "202412210MIN": ("MIN", "GSW"),
#    "202412210NOP": ("NOP", "NYK"),
#    "202412210DAL": ("DAL", "LAC"),
#    "202412210SAS": ("SAS", "POR"),
#    "202412210PHO": ("PHO", "DET"),
#    "202412220SAC": ("SAC", "IND"),
#    "202412220TOR": ("TOR", "HOU"),
#    "202412220NOP": ("NOP", "DEN"),
#    "202412230CHO": ("CHO", "HOU"),
#    "202412230CLE": ("CLE", "UTA"),
#    "202412230ORL": ("ORL", "BOS"),
#    "202412230PHI": ("PHI", "SAS"),
#    "202412230ATL": ("ATL", "MIN"),
#    "202412230MIA": ("MIA", "BRK"),
#    "202412230NYK": ("NYK", "TOR"),
#    "202412230CHI": ("CHI", "MIL"),
#    "202412230MEM": ("MEM", "LAC"),
#    "202412230OKC": ("OKC", "WAS"),
#    "202412230DAL": ("DAL", "POR"),
#    "202412230DEN": ("DEN", "PHO"),
#    "202412230GSW": ("GSW", "IND"),
#    "202412230LAL": ("LAL", "DET"),
#    "202412250NYK": ("NYK", "SAS"),
#    "202412250DAL": ("DAL", "MIN"),
#    "202412250BOS": ("BOS", "PHI"),
#    "202412250GSW": ("GSW", "LAL"),
#    "202412250PHO": ("PHO", "DEN"),
#    "202412260IND": ("IND", "OKC"),
#    "202412260ORL": ("ORL", "MIA"),
#    "202412260WAS": ("WAS", "CHO"),
#    "202412260ATL": ("ATL", "CHI"),
#    "202412260MEM": ("MEM", "TOR"),
#    "202412260MIL": ("MIL", "BRK"),
#    "202412260NOP": ("NOP", "HOU"),
#    "202412260POR": ("POR", "UTA"),
#    "202412260SAC": ("SAC", "DET"),
#    "202412270ORL": ("ORL", "NYK"),
#    "202412270BOS": ("BOS", "IND"),
#    "202412270BRK": ("BRK", "SAS"),
#    "202412270HOU": ("HOU", "MIN"),
#    "202412270NOP": ("NOP", "MEM"),
#    "202412270DEN": ("DEN", "CLE"),
#    "202412270PHO": ("PHO", "DAL"),
#    "202412270LAC": ("LAC", "GSW"),
#    "202412280ATL": ("ATL", "MIA"),
#    "202412280CHO": ("CHO", "OKC"),
#    "202412280WAS": ("WAS", "NYK"),
#    "202412280CHI": ("CHI", "MIL"),
#    "202412280GSW": ("GSW", "PHO"),
#    "202412280DEN": ("DEN", "DET"),
#    "202412280UTA": ("UTA", "PHI"),
#    "202412280POR": ("POR", "DAL"),
#    "202412280LAL": ("LAL", "SAC"),
#    "202412290ORL": ("ORL", "BRK"),
#    "202412290BOS": ("BOS", "IND"),
#    "202412290TOR": ("TOR", "ATL"),
#    "202412290HOU": ("HOU", "MIA"),
#    "202412290OKC": ("OKC", "MEM"),
#    "202412290MIN": ("MIN", "SAS"),
#    "202412300CHO": ("CHO", "CHI"),
#    "202412300WAS": ("WAS", "NYK"),
#    "202412300NOP": ("NOP", "LAC"),
#    "202412300UTA": ("UTA", "DEN"),
#    "202412300GSW": ("GSW", "CLE"),
#    "202412300POR": ("POR", "PHI"),
#    "202412300SAC": ("SAC", "DAL"),
#    "202412310BOS": ("BOS", "TOR"),
#    "202412310IND": ("IND", "MIL"),
#    "202412310SAS": ("SAS", "LAC"),
#    "202412310OKC": ("OKC", "MIN"),
#    "202412310LAL": ("LAL", "CLE"),
#    "202412310PHO": ("PHO", "MEM"),
#    "202501010DET": ("DET", "ORL"),
#    "202501010WAS": ("WAS", "CHI"),
#    "202501010MIA": ("MIA", "NOP"),
#    "202501010NYK": ("NYK", "UTA"),
#    "202501010TOR": ("TOR", "BRK"),
#    "202501010HOU": ("HOU", "DAL"),
#    "202501010DEN": ("DEN", "ATL"),
#    "202501010SAC": ("SAC", "PHI"),
#    "202501020MIA": ("MIA", "IND"),
#    "202501020MIN": ("MIN", "BOS"),
#    "202501020MIL": ("MIL", "BRK"),
#    "202501020OKC": ("OKC", "LAC"),
#    "202501020GSW": ("GSW", "PHI"),
#    "202501020LAL": ("LAL", "POR"),
#    "202501030DET": ("DET", "CHO"),
#    "202501030TOR": ("TOR", "ORL"),
#    "202501030HOU": ("HOU", "BOS"),
#    "202501030NOP": ("NOP", "WAS"),
#    "202501030OKC": ("OKC", "NYK"),
#    "202501030DAL": ("DAL", "CLE"),
#    "202501030DEN": ("DEN", "SAS"),
#    "202501030SAC": ("SAC", "MEM"),
#    "202501030LAL": ("LAL", "ATL"),
#    "202501040BRK": ("BRK", "PHI"),
#    "202501040DET": ("DET", "MIN"),
#    "202501040IND": ("IND", "PHO"),
#    "202501040CHI": ("CHI", "NYK"),
#    "202501040MIA": ("MIA", "UTA"),
#    "202501040MIL": ("MIL", "POR"),
#    "202501040SAS": ("SAS", "DEN"),
#    "202501040GSW": ("GSW", "MEM"),
#    "202501040LAC": ("LAC", "ATL"),
#    "202501050OKC": ("OKC", "BOS"),
#    "202501050CLE": ("CLE", "CHO"),
#    "202501050WAS": ("WAS", "NOP"),
#    "202501050ORL": ("ORL", "UTA"),
#    "202501050HOU": ("HOU", "LAL"),
#    "202501050GSW": ("GSW", "SAC"),
#    "202501060DET": ("DET", "POR"),
#    "202501060PHI": ("PHI", "PHO"),
#    "202501060BRK": ("BRK", "IND"),
#    "202501060NYK": ("NYK", "ORL"),
#    "202501060TOR": ("TOR", "MIL"),
#    "202501060CHI": ("CHI", "SAS"),
#    "202501060MEM": ("MEM", "DAL"),
#    "202501060MIN": ("MIN", "LAC"),
#    "202501060SAC": ("SAC", "MIA"),
#    "202501070CHO": ("CHO", "PHO"),
#    "202501070WAS": ("WAS", "HOU"),
#    "202501070DAL": ("DAL", "LAL"),
#    "202501070NOP": ("NOP", "MIN"),
#    "202501070UTA": ("UTA", "ATL"),
#    "202501070DEN": ("DEN", "BOS"),
#    "202501070GSW": ("GSW", "MIA"),
#    "202501080CLE": ("CLE", "OKC"),
#    "202501080IND": ("IND", "CHI"),
#    "202501080NYK": ("NYK", "TOR"),
#    "202501080PHI": ("PHI", "WAS"),
#    "202501080BRK": ("BRK", "DET"),
#    "202501080NOP": ("NOP", "POR"),
#    "202501080DEN": ("DEN", "LAC"),
#    "202501080MIL": ("MIL", "SAS"),
#    "202501090CLE": ("CLE", "TOR"),
#    "202501090DET": ("DET", "GSW"),
#    "202501090ORL": ("ORL", "MIN"),
#    "202501090MEM": ("MEM", "HOU"),
#    "202501090DAL": ("DAL", "POR"),
#    "202501090PHO": ("PHO", "ATL"),
#    "202501090UTA": ("UTA", "MIA"),
#    "202501090LAL": ("LAL", "CHO"),
#    "202501100IND": ("IND", "GSW"),
#    "202501100ORL": ("ORL", "MIL"),
#    "202501100PHI": ("PHI", "NOP"),
#    "202501100BOS": ("BOS", "SAC"),
#    "202501100NYK": ("NYK", "OKC"),
#    "202501100CHI": ("CHI", "WAS"),
#    "202501100DEN": ("DEN", "BRK"),
#    "202501110ATL": ("ATL", "HOU"),
#    "202501110PHO": ("PHO", "UTA"),
#    "202501110DET": ("DET", "TOR"),
#    "202501110MIN": ("MIN", "MEM"),
#    "202501110POR": ("POR", "MIA"),
#    "202501110LAC": ("LAC", "CHO"),
#    "202501110LAL": ("LAL", "SAS"),
#    "202501120DAL": ("DAL", "DEN"),
#    "202501120NYK": ("NYK", "MIL"),
#    "202501120CHI": ("CHI", "SAC"),
#    "202501120BOS": ("BOS", "NOP"),
#    "202501120CLE": ("CLE", "IND"),
#    "202501120ORL": ("ORL", "PHI"),
#    "202501120WAS": ("WAS", "OKC"),
#    "202501120UTA": ("UTA", "BRK"),
#    "202501120PHO": ("PHO", "CHO"),
#    "202501130WAS": ("WAS", "MIN"),
#    "202501130NYK": ("NYK", "DET"),
#    "202501130TOR": ("TOR", "GSW"),
#    "202501130HOU": ("HOU", "MEM"),
#    "202501130LAC": ("LAC", "MIA"),
#    "202501130LAL": ("LAL", "SAS"),
#    "202501140IND": ("IND", "CLE"),
#    "202501140PHI": ("PHI", "OKC"),
#    "202501140ATL": ("ATL", "PHO"),
#    "202501140CHI": ("CHI", "NOP"),
#    "202501140MIL": ("MIL", "SAC"),
#    "202501140DAL": ("DAL", "DEN"),
#    "202501140POR": ("POR", "BRK"),
#    "202501150PHI": ("PHI", "NYK"),
#    "202501150TOR": ("TOR", "BOS"),
#    "202501150CHI": ("CHI", "ATL"),
#    "202501150MIL": ("MIL", "ORL"),
#    "202501150MIN": ("MIN", "GSW"),
#    "202501150NOP": ("NOP", "DAL"),
#    "202501150SAS": ("SAS", "MEM"),
#    "202501150DEN": ("DEN", "HOU"),
#    "202501150UTA": ("UTA", "CHO"),
#    "202501150LAL": ("LAL", "MIA"),
#    "202501150LAC": ("LAC", "BRK"),
#    "202501160DET": ("DET", "IND"),
#    "202501160WAS": ("WAS", "PHO"),
#    "202501160OKC": ("OKC", "CLE"),
#    "202501160POR": ("POR", "LAC"),
#    "202501160SAC": ("SAC", "HOU"),
#    "202501170BOS": ("BOS", "ORL"),
#    "202501170NYK": ("NYK", "MIN"),
#    "202501170MIA": ("MIA", "DEN"),
#    "202501170MIL": ("MIL", "TOR"),
#    "202501170NOP": ("NOP", "UTA"),
#    "202501170SAS": ("SAS", "MEM"),
#    "202501170DAL": ("DAL", "OKC"),
#    "202501170CHI": ("CHI", "CHO"),
#    "202501170LAL": ("LAL", "BRK"),
#    "202501180DET": ("DET", "PHO"),
#    "202501180BOS": ("BOS", "ATL"),
#    "202501180IND": ("IND", "PHI"),
#    "202501180GSW": ("GSW", "WAS"),
#    "202501180MIN": ("MIN", "CLE"),
#    "202501180POR": ("POR", "HOU"),
#    "202501190MIA": ("MIA", "SAS"),
#    "202501190ORL": ("ORL", "DEN"),
#    "202501190MIL": ("MIL", "PHI"),
#    "202501190OKC": ("OKC", "BRK"),
#    "202501190LAC": ("LAC", "LAL"),
#    "202501190POR": ("POR", "CHI"),
#    "202501190SAC": ("SAC", "WAS"),
#    "202501200CHO": ("CHO", "DAL"),
#    "202501200HOU": ("HOU", "DET"),
#    "202501200MEM": ("MEM", "MIN"),
#    "202501200NYK": ("NYK", "ATL"),
#    "202501200CLE": ("CLE", "PHO"),
#    "202501200GSW": ("GSW", "BOS"),
#    "202501200NOP": ("NOP", "UTA"),
#    "202501210BRK": ("BRK", "NYK"),
#    "202501210MIA": ("MIA", "POR"),
#    "202501210TOR": ("TOR", "ORL"),
#    "202501210DEN": ("DEN", "PHI"),
#    "202501210LAC": ("LAC", "CHI"),
#    "202501210LAL": ("LAL", "WAS"),
#    "202501220ATL": ("ATL", "DET"),
#    "202501220BRK": ("BRK", "PHO"),
#    "202501220DAL": ("DAL", "MIN"),
#    "202501220HOU": ("HOU", "CLE"),
#    "202501220MEM": ("MEM", "CHO"),
#    "202501220NOP": ("NOP", "MIL"),
#    "202501220OKC": ("OKC", "UTA"),
#    "202501220SAC": ("SAC", "GSW"),
#    "202501220LAC": ("LAC", "BOS"),
#    "202501230IND": ("IND", "SAS"),
#    "202501230ORL": ("ORL", "POR"),
#    "202501230ATL": ("ATL", "TOR"),
#    "202501230MIL": ("MIL", "MIA"),
#    "202501230OKC": ("OKC", "DAL"),
#    "202501230DEN": ("DEN", "SAC"),
#    "202501230UTA": ("UTA", "WAS"),
#    "202501230GSW": ("GSW", "CHI"),
#    "202501230LAL": ("LAL", "BOS"),
#    "202501240CHO": ("CHO", "POR"),
#    "202501240PHI": ("PHI", "CLE"),
#    "202501240MEM": ("MEM", "NOP"),
#    "202501250SAS": ("SAS", "IND"),
#    "202501250MIN": ("MIN", "DEN"),
#    "202501250DAL": ("DAL", "BOS"),
#    "202501250BRK": ("BRK", "MIA"),
#    "202501250CHO": ("CHO", "NOP"),
#    "202501250ORL": ("ORL", "DET"),
#    "202501250ATL": ("ATL", "TOR"),
#    "202501250CLE": ("CLE", "HOU"),
#    "202501250NYK": ("NYK", "SAC"),
#    "202501250CHI": ("CHI", "PHI"),
#    "202501250MEM": ("MEM", "UTA"),
#    "202501250GSW": ("GSW", "LAL"),
#    "202501250PHO": ("PHO", "WAS"),
#    "202501250LAC": ("LAC", "MIL"),
#    "202501260POR": ("POR", "OKC"),
#    "202501270CHO": ("CHO", "LAL"),
#    "202501270CLE": ("CLE", "DET"),
#    "202501270BOS": ("BOS", "HOU"),
#    "202501270BRK": ("BRK", "SAC"),
#    "202501270MIA": ("MIA", "ORL"),
#    "202501270NYK": ("NYK", "MEM"),
#    "202501270TOR": ("TOR", "NOP"),
#    "202501270CHI": ("CHI", "DEN"),
#    "202501270MIN": ("MIN", "ATL"),
#    "202501270DAL": ("DAL", "WAS"),
#    "202501270UTA": ("UTA", "MIL"),
#    "202501270PHO": ("PHO", "LAC"),
#    "202501280PHI": ("PHI", "LAL"),
#    "202501280GSW": ("GSW", "UTA"),
#    "202501280POR": ("POR", "MIL"),
#    "202501290CHO": ("CHO", "BRK"),
#    "202501290IND": ("IND", "DET"),
#    "202501290WAS": ("WAS", "TOR"),
#    "202501290BOS": ("BOS", "CHI"),
#    "202501290MIA": ("MIA", "CLE"),
#    "202501290NYK": ("NYK", "DEN"),
#    "202501290PHI": ("PHI", "SAC"),
#    "202501290NOP": ("NOP", "DAL"),
#    "202501290SAS": ("SAS", "LAC"),
#    "202501290PHO": ("PHO", "MIN"),
#    "202501290GSW": ("GSW", "OKC"),
#    "202501300WAS": ("WAS", "LAL"),
#    "202501300CLE": ("CLE", "ATL"),
#    "202501300MEM": ("MEM", "HOU"),
#    "202501300POR": ("POR", "ORL"),
#    "202501300UTA": ("UTA", "MIN"),
#    "202501310CHO": ("CHO", "LAC"),
#    "202501310DET": ("DET", "DAL"),
#    "202501310PHI": ("PHI", "DEN"),
#    "202501310TOR": ("TOR", "CHI"),
#    "202501310NOP": ("NOP", "BOS"),
#    "202501310SAS": ("SAS", "MIL"),
#    "202501310GSW": ("GSW", "PHO"),
#    "202502010IND": ("IND", "ATL"),
#    "202502010UTA": ("UTA", "ORL"),
#    "202502010CHO": ("CHO", "DEN"),
#    "202502010HOU": ("HOU", "BRK"),
#    "202502010MIN": ("MIN", "WAS"),
#    "202502010OKC": ("OKC", "SAC"),
#    "202502010NYK": ("NYK", "LAL"),
#    "202502010SAS": ("SAS", "MIA"),
#    "202502010POR": ("POR", "PHO"),
#    "202502020DET": ("DET", "CHI"),
#    "202502020CLE": ("CLE", "DAL"),
#    "202502020TOR": ("TOR", "LAC"),
#    "202502020PHI": ("PHI", "BOS"),
#    "202502020MIL": ("MIL", "MEM"),
#    "202502030CHO": ("CHO", "WAS"),
#    "202502030DET": ("DET", "ATL"),
#    "202502030NYK": ("NYK", "HOU"),
#    "202502030MEM": ("MEM", "SAS"),
#    "202502030MIN": ("MIN", "SAC"),
#    "202502030OKC": ("OKC", "MIL"),
#    "202502030DEN": ("DEN", "NOP"),
#    "202502030UTA": ("UTA", "IND"),
#    "202502030GSW": ("GSW", "ORL"),
#    "202502030POR": ("POR", "PHO"),
#    "202502040CLE": ("CLE", "BOS"),
#    "202502040BRK": ("BRK", "HOU"),
#    "202502040PHI": ("PHI", "DAL"),
#    "202502040TOR": ("TOR", "NYK"),
#    "202502040CHI": ("CHI", "MIA"),
#    "202502040LAC": ("LAC", "LAL"),
#    "202502040POR": ("POR", "IND"),
#    "202502050CHO": ("CHO", "MIL"),
#    "202502050DET": ("DET", "CLE"),
#    "202502050ATL": ("ATL", "SAS"),
#    "202502050BRK": ("BRK", "WAS"),
#    "202502050PHI": ("PHI", "MIA"),
#    "202502050TOR": ("TOR", "MEM"),
#    "202502050MIN": ("MIN", "CHI"),
#    "202502050OKC": ("OKC", "PHO"),
#    "202502050UTA": ("UTA", "GSW"),
#    "202502050DEN": ("DEN", "NOP"),
#    "202502050SAC": ("SAC", "ORL"),
#    "202502060BOS": ("BOS", "DAL"),
#    "202502060MIN": ("MIN", "HOU"),
#    "202502060DEN": ("DEN", "ORL"),
#    "202502060LAL": ("LAL", "GSW"),
#    "202502060POR": ("POR", "SAC"),
#    "202502060LAC": ("LAC", "IND"),
#    "202502070CHO": ("CHO", "SAS"),
#    "202502070WAS": ("WAS", "CLE"),
#    "202502070ATL": ("ATL", "MIL"),
#    "202502070BRK": ("BRK", "MIA"),
#    "202502070DET": ("DET", "PHI"),
#    "202502070OKC": ("OKC", "TOR"),
#    "202502070PHO": ("PHO", "UTA"),
#    "202502080DAL": ("DAL", "HOU"),
#    "202502080LAL": ("LAL", "IND"),
#    "202502080ORL": ("ORL", "SAS"),
#    "202502080WAS": ("WAS", "ATL"),
#    "202502080CHI": ("CHI", "GSW"),
#    "202502080MEM": ("MEM", "OKC"),
#    "202502080MIN": ("MIN", "POR"),
#    "202502080NYK": ("NYK", "BOS"),
#    "202502080PHO": ("PHO", "DEN"),
#    "202502080SAC": ("SAC", "NOP"),
#    "202502080LAC": ("LAC", "UTA"),
#    "202502090DET": ("DET", "CHO"),
#    "202502090HOU": ("HOU", "TOR"),
#    "202502090MIL": ("MIL", "PHI"),
#    "202502100CLE": ("CLE", "MIN"),
#    "202502100ORL": ("ORL", "ATL"),
#    "202502100WAS": ("WAS", "SAS"),
#    "202502100BRK": ("BRK", "CHO"),
#    "202502100MIA": ("MIA", "BOS"),
#    "202502100MIL": ("MIL", "GSW"),
#    "202502100OKC": ("OKC", "NOP"),
#    "202502100DAL": ("DAL", "SAC"),
#    "202502100DEN": ("DEN", "POR"),
#    "202502110PHI": ("PHI", "TOR"),
#    "202502110IND": ("IND", "NYK"),
#    "202502110CHI": ("CHI", "DET"),
#    "202502110PHO": ("PHO", "MEM"),
#    "202502110LAL": ("LAL", "UTA"),
#    "202502120BOS": ("BOS", "SAS"),
#    "202502120ORL": ("ORL", "CHO"),
#    "202502120WAS": ("WAS", "IND"),
#    "202502120BRK": ("BRK", "PHI"),
#    "202502120NYK": ("NYK", "ATL"),
#    "202502120TOR": ("TOR", "CLE"),
#    "202502120CHI": ("CHI", "DET"),
#    "202502120MIN": ("MIN", "MIL"),
#    "202502120NOP": ("NOP", "SAC"),
#    "202502120OKC": ("OKC", "MIA"),
#    "202502120HOU": ("HOU", "PHO"),
#    "202502120DEN": ("DEN", "POR"),
#    "202502120UTA": ("UTA", "LAL"),
#    "202502120DAL": ("DAL", "GSW"),
#    "202502120LAC": ("LAC", "MEM"),
#    "202502130HOU": ("HOU", "GSW"),
#    "202502130NOP": ("NOP", "SAC"),
#    "202502130DAL": ("DAL", "MIA"),
#    "202502130MIN": ("MIN", "OKC"),
#    "202502200IND": ("IND", "MEM"),
#    "202502200PHI": ("PHI", "BOS"),
#    "202502200ATL": ("ATL", "ORL"),
#    "202502200BRK": ("BRK", "CLE"),
#    "202502200NYK": ("NYK", "CHI"),
#    "202502200MIL": ("MIL", "LAC"),
#    "202502200DEN": ("DEN", "CHO"),
#    "202502200SAS": ("SAS", "PHO"),
#    "202502200POR": ("POR", "LAL"),
#    "202502210CLE": ("CLE", "NYK"),
#    "202502210ORL": ("ORL", "MEM"),
#    "202502210WAS": ("WAS", "MIL"),
#    "202502210TOR": ("TOR", "MIA"),
#    "202502210HOU": ("HOU", "MIN"),
#    "202502210SAS": ("SAS", "DET"),
#    "202502210DAL": ("DAL", "NOP"),
#    "202502210UTA": ("UTA", "OKC"),
#    "202502210SAC": ("SAC", "GSW"),
#    "202502220CHI": ("CHI", "PHO"),
#    "202502220PHI": ("PHI", "BRK"),
#    "202502220DEN": ("DEN", "LAL"),
#    "202502220UTA": ("UTA", "HOU"),
#    "202502220POR": ("POR", "CHO"),
#    "202502230BOS": ("BOS", "NYK"),
#    "202502230GSW": ("GSW", "DAL"),
#    "202502230IND": ("IND", "LAC"),
#    "202502230ATL": ("ATL", "DET"),
#    "202502230ORL": ("ORL", "WAS"),
#    "202502230TOR": ("TOR", "PHO"),
#    "202502230MIL": ("MIL", "MIA"),
#    "202502230NOP": ("NOP", "SAS"),
#    "202502230CLE": ("CLE", "MEM"),
#    "202502230MIN": ("MIN", "OKC"),
#    "202502240DET": ("DET", "LAC"),
#    "202502240IND": ("IND", "DEN"),
#    "202502240PHI": ("PHI", "CHI"),
#    "202502240WAS": ("WAS", "BRK"),
#    "202502240ATL": ("ATL", "MIA"),
#    "202502240OKC": ("OKC", "MIN"),
#    "202502240UTA": ("UTA", "POR"),
#    "202502240SAC": ("SAC", "CHO"),
#    "202502250TOR": ("TOR", "BOS"),
#    "202502250ORL": ("ORL", "CLE"),
#    "202502250HOU": ("HOU", "MIL"),
#    "202502250MEM": ("MEM", "PHO"),
#    "202502250NOP": ("NOP", "SAS"),
#    "202502250GSW": ("GSW", "CHO"),
#    "202502250LAL": ("LAL", "DAL"),
#    "202502260DET": ("DET", "BOS"),
#    "202502260IND": ("IND", "TOR"),
#    "202502260NYK": ("NYK", "PHI"),
#    "202502260WAS": ("WAS", "POR"),
#    "202502260BRK": ("BRK", "OKC"),
#    "202502260MIA": ("MIA", "ATL"),
#    "202502260CHI": ("CHI", "LAC"),
#    "202502260UTA": ("UTA", "SAC"),
#    "202502260HOU": ("HOU", "SAS"),
#    "202502270ORL": ("ORL", "GSW"),
#    "202502270MIL": ("MIL", "DEN"),
#    "202502270DAL": ("DAL", "CHO"),
#    "202502270PHO": ("PHO", "NOP"),
#    "202502270LAL": ("LAL", "MIN"),
#    "202502280DET": ("DET", "DEN"),
#    "202502280ATL": ("ATL", "OKC"),
#    "202502280BOS": ("BOS", "CLE"),
#    "202502280BRK": ("BRK", "POR"),
#    "202502280CHI": ("CHI", "TOR"),
#    "202502280MEM": ("MEM", "NYK"),
#    "202502280MIA": ("MIA", "IND"),
#    "202502280PHO": ("PHO", "NOP"),
#    "202502280UTA": ("UTA", "MIN"),
#    "202502280LAL": ("LAL", "LAC"),
#    "202503010CHO": ("CHO", "WAS"),
#    "202503010DET": ("DET", "BRK"),
#    "202503010HOU": ("HOU", "SAC"),
#    "202503010MEM": ("MEM", "SAS"),
#    "202503010DAL": ("DAL", "MIL"),
#    "202503010PHI": ("PHI", "GSW"),
#    "202503020BOS": ("BOS", "DEN"),
#    "202503020CLE": ("CLE", "POR"),
#    "202503020IND": ("IND", "CHI"),
#    "202503020MIA": ("MIA", "NYK"),
#    "202503020ORL": ("ORL", "TOR"),
#    "202503020SAS": ("SAS", "OKC"),
#    "202503020UTA": ("UTA", "NOP"),
#    "202503020LAL": ("LAL", "LAC"),
#    "202503020PHO": ("PHO", "MIN"),
#    "202503030CHO": ("CHO", "GSW"),
#    "202503030PHI": ("PHI", "POR"),
#    "202503030MIA": ("MIA", "WAS"),
#    "202503030MEM": ("MEM", "ATL"),
#    "202503030OKC": ("OKC", "HOU"),
#    "202503030DAL": ("DAL", "SAC"),
#    "202503030UTA": ("UTA", "DET"),
#    "202503040IND": ("IND", "HOU"),
#    "202503040ORL": ("ORL", "TOR"),
#    "202503040ATL": ("ATL", "MIL"),
#    "202503040NYK": ("NYK", "GSW"),
#    "202503040CHI": ("CHI", "CLE"),
#    "202503040MIN": ("MIN", "PHI"),
#    "202503040SAS": ("SAS", "BRK"),
#    "202503040PHO": ("PHO", "LAC"),
#    "202503040LAL": ("LAL", "NOP"),
#    "202503050BOS": ("BOS", "POR"),
#    "202503050CHO": ("CHO", "MIN"),
#    "202503050CLE": ("CLE", "MIA"),
#    "202503050WAS": ("WAS", "UTA"),
#    "202503050MEM": ("MEM", "OKC"),
#    "202503050DEN": ("DEN", "SAC"),
#    "202503050MIL": ("MIL", "DAL"),
#    "202503050LAC": ("LAC", "DET"),
#    "202503060ATL": ("ATL", "IND"),
#    "202503060BOS": ("BOS", "PHI"),
#    "202503060BRK": ("BRK", "GSW"),
#    "202503060NOP": ("NOP", "HOU"),
#    "202503060LAL": ("LAL", "NYK"),
#    "202503070CHO": ("CHO", "CLE"),
#    "202503070DAL": ("DAL", "MEM"),
#    "202503070TOR": ("TOR", "UTA"),
#    "202503070MIA": ("MIA", "MIN"),
#    "202503070OKC": ("OKC", "POR"),
#    "202503070DEN": ("DEN", "PHO"),
#    "202503070SAC": ("SAC", "SAS"),
#    "202503070LAC": ("LAC", "NYK"),
#    "202503080CHO": ("CHO", "BRK"),
#    "202503080HOU": ("HOU", "NOP"),
#    "202503080ATL": ("ATL", "IND"),
#    "202503080TOR": ("TOR", "WAS"),
#    "202503080MIA": ("MIA", "CHI"),
#    "202503080MIL": ("MIL", "ORL"),
#    "202503080BOS": ("BOS", "LAL"),
#    "202503080GSW": ("GSW", "DET"),
#    "202503090OKC": ("OKC", "DEN"),
#    "202503090DAL": ("DAL", "PHO"),
#    "202503090MIL": ("MIL", "CLE"),
#    "202503090NOP": ("NOP", "MEM"),
#    "202503090PHI": ("PHI", "UTA"),
#    "202503090MIN": ("MIN", "SAS"),
#    "202503090POR": ("POR", "DET"),
#    "202503090LAC": ("LAC", "SAC"),
#    "202503100ATL": ("ATL", "PHI"),
#    "202503100BOS": ("BOS", "UTA"),
#    "202503100BRK": ("BRK", "LAL"),
#    "202503100MIA": ("MIA", "CHO"),
#    "202503100TOR": ("TOR", "WAS"),
#    "202503100CHI": ("CHI", "IND"),
#    "202503100HOU": ("HOU", "ORL"),
#    "202503100MEM": ("MEM", "PHO"),
#    "202503100OKC": ("OKC", "DEN"),
#    "202503100SAS": ("SAS", "DAL"),
#    "202503100GSW": ("GSW", "POR"),
#    "202503100SAC": ("SAC", "NYK"),
#    "202503110CLE": ("CLE", "BRK"),
#    "202503110DET": ("DET", "WAS"),
#    "202503110IND": ("IND", "MIL"),
#    "202503110NOP": ("NOP", "LAC"),
#    "202503120ORL": ("ORL", "CHI"),
#    "202503120ATL": ("ATL", "CHO"),
#    "202503120BOS": ("BOS", "OKC"),
#    "202503120TOR": ("TOR", "PHI"),
#    "202503120HOU": ("HOU", "PHO"),
#    "202503120MEM": ("MEM", "UTA"),
#    "202503120MIA": ("MIA", "LAC"),
#    "202503120SAS": ("SAS", "DAL"),
#    "202503120DEN": ("DEN", "MIN"),
#    "202503120POR": ("POR", "NYK"),
#    "202503130DET": ("DET", "WAS"),
#    "202503130MIL": ("MIL", "LAL"),
#    "202503130CHI": ("CHI", "BRK"),
#    "202503130GSW": ("GSW", "SAC"),
#    "202503140MIA": ("MIA", "BOS"),
#    "202503140PHI": ("PHI", "IND"),
#    "202503140ATL": ("ATL", "LAC"),
#    "202503140HOU": ("HOU", "DAL"),
#    "202503140MEM": ("MEM", "CLE"),
#    "202503140MIN": ("MIN", "ORL"),
#    "202503140SAS": ("SAS", "CHO"),
#    "202503140DEN": ("DEN", "LAL"),
#    "202503140UTA": ("UTA", "TOR"),
#    "202503140PHO": ("PHO", "SAC"),
#    "202503150BRK": ("BRK", "BOS"),
#    "202503150DET": ("DET", "OKC"),
#    "202503150HOU": ("HOU", "CHI"),
#    "202503150MEM": ("MEM", "MIA"),
#    "202503150MIL": ("MIL", "IND"),
#    "202503150GSW": ("GSW", "NYK"),
#    "202503150SAS": ("SAS", "NOP"),
#    "202503150DEN": ("DEN", "WAS"),
#    "202503160DAL": ("DAL", "PHI"),
#    "202503160LAL": ("LAL", "PHO"),
#    "202503160BRK": ("BRK", "ATL"),
#    "202503160CLE": ("CLE", "ORL"),
#    "202503160POR": ("POR", "TOR"),
#    "202503160MIN": ("MIN", "UTA"),
#    "202503160MIL": ("MIL", "OKC"),
#    "202503160LAC": ("LAC", "WAS"),
#    "202503170NYK": ("NYK", "MIA"),
#    "202503170HOU": ("HOU", "PHI"),
#    "202503170MIN": ("MIN", "IND"),
#    "202503170NOP": ("NOP", "DET"),
#    "202503170SAS": ("SAS", "ORL"),
#    "202503170UTA": ("UTA", "CHI"),
#    "202503170GSW": ("GSW", "DEN"),
#    "202503170PHO": ("PHO", "TOR"),
#    "202503170SAC": ("SAC", "MEM"),
#    "202503180CHO": ("CHO", "ATL"),
#    "202503180BOS": ("BOS", "BRK"),
#    "202503180POR": ("POR", "WAS"),
#    "202503180LAC": ("LAC", "CLE"),
#    "202503180LAL": ("LAL", "MIL"),
#    "202503190IND": ("IND", "DAL"),
#    "202503190ORL": ("ORL", "HOU"),
#    "202503190MIA": ("MIA", "DET"),
#    "202503190MIN": ("MIN", "NOP"),
#    "202503190OKC": ("OKC", "PHI"),
#    "202503190SAS": ("SAS", "NYK"),
#    "202503190UTA": ("UTA", "LAC"),
#    "202503190GSW": ("GSW", "TOR"),
#    "202503190LAL": ("LAL", "DEN"),
#    "202503190PHO": ("PHO", "CHI"),
#    "202503190POR": ("POR", "MEM"),
#    "202503190SAC": ("SAC", "CLE"),
#    "202503200CHO": ("CHO", "NYK"),
#    "202503200IND": ("IND", "BRK"),
#    "202503200GSW": ("GSW", "MIL"),
#    "202503200SAC": ("SAC", "CHI"),
#    "202503210WAS": ("WAS", "ORL"),
#    "202503210MIA": ("MIA", "HOU"),
#    "202503210MIN": ("MIN", "NOP"),
#    "202503210OKC": ("OKC", "CHO"),
#    "202503210SAS": ("SAS", "PHI"),
#    "202503210DAL": ("DAL", "DET"),
#    "202503210UTA": ("UTA", "BOS"),
#    "202503210PHO": ("PHO", "CLE"),
#    "202503210POR": ("POR", "DEN"),
#    "202503210LAC": ("LAC", "MEM"),
#    "202503220IND": ("IND", "BRK"),
#    "202503220ATL": ("ATL", "GSW"),
#    "202503220NYK": ("NYK", "WAS"),
#    "202503220SAC": ("SAC", "MIL"),
#    "202503220LAL": ("LAL", "CHI"),
#    "202503230DET": ("DET", "NOP"),
#    "202503230UTA": ("UTA", "CLE"),
#    "202503230ATL": ("ATL", "PHI"),
#    "202503230MIA": ("MIA", "CHO"),
#    "202503230POR": ("POR", "BOS"),
#    "202503230TOR": ("TOR", "SAS"),
#    "202503230HOU": ("HOU", "DEN"),
#    "202503230LAC": ("LAC", "OKC"),
#    "202503240IND": ("IND", "MIN"),
#    "202503240ORL": ("ORL", "LAL"),
#    "202503240WAS": ("WAS", "TOR"),
#    "202503240BRK": ("BRK", "DAL"),
#    "202503240NOP": ("NOP", "PHI"),
#    "202503240DEN": ("DEN", "CHI"),
#    "202503240PHO": ("PHO", "MIL"),
#    "202503240SAC": ("SAC", "BOS"),
#    "202503250CHO": ("CHO", "ORL"),
#    "202503250DET": ("DET", "SAS"),
#    "202503250MIA": ("MIA", "GSW"),
#    "202503250NYK": ("NYK", "DAL"),
#    "202503250HOU": ("HOU", "ATL"),
#    "202503250UTA": ("UTA", "MEM"),
#    "202503250POR": ("POR", "CLE"),
#    "202503250SAC": ("SAC", "OKC"),
#    "202503260PHI": ("PHI", "WAS"),
#    "202503260BRK": ("BRK", "TOR"),
#    "202503260IND": ("IND", "LAL"),
#    "202503260NYK": ("NYK", "LAC"),
#    "202503260DEN": ("DEN", "MIL"),
#    "202503260PHO": ("PHO", "BOS"),
#    "202503270CLE": ("CLE", "SAS"),
#    "202503270ORL": ("ORL", "DAL"),
#    "202503270WAS": ("WAS", "IND"),
#    "202503270MIA": ("MIA", "ATL"),
#    "202503270CHI": ("CHI", "LAL"),
#    "202503270OKC": ("OKC", "MEM"),
#    "202503270UTA": ("UTA", "HOU"),
#    "202503270SAC": ("SAC", "POR"),
#    "202503280DET": ("DET", "CLE"),
#    "202503280BRK": ("BRK", "LAC"),
#    "202503280TOR": ("TOR", "CHO"),
#    "202503280MIL": ("MIL", "NYK"),
#    "202503280MIN": ("MIN", "PHO"),
#    "202503280NOP": ("NOP", "GSW"),
#    "202503280DEN": ("DEN", "UTA"),
#    "202503290ORL": ("ORL", "SAC"),
#    "202503290WAS": ("WAS", "BRK"),
#    "202503290PHI": ("PHI", "MIA"),
#    "202503290CHI": ("CHI", "DAL"),
#    "202503290MEM": ("MEM", "LAL"),
#    "202503290OKC": ("OKC", "IND"),
#    "202503290SAS": ("SAS", "BOS"),
#    "202503300CLE": ("CLE", "LAC"),
#    "202503300NYK": ("NYK", "POR"),
#    "202503300MIL": ("MIL", "ATL"),
#    "202503300MIN": ("MIN", "DET"),
#    "202503300NOP": ("NOP", "CHO"),
#    "202503300SAS": ("SAS", "GSW"),
#    "202503300PHI": ("PHI", "TOR"),
#    "202503300PHO": ("PHO", "HOU"),
#    "202503310CHO": ("CHO", "UTA"),
#    "202503310IND": ("IND", "SAC"),
#    "202503310ORL": ("ORL", "LAC"),
#    "202503310WAS": ("WAS", "MIA"),
#    "202503310MEM": ("MEM", "BOS"),
#    "202503310OKC": ("OKC", "CHI"),
#    "202503310DAL": ("DAL", "BRK"),
#    "202503310LAL": ("LAL", "HOU"),
#    "202504010ATL": ("ATL", "POR"),
#    "202504010NYK": ("NYK", "PHI"),
#    "202504010CHI": ("CHI", "TOR"),
#    "202504010MEM": ("MEM", "GSW"),
#    "202504010MIL": ("MIL", "PHO"),
#    "202504010DEN": ("DEN", "MIN"),
#    "202504020CLE": ("CLE", "NYK"),
#    "202504020IND": ("IND", "CHO"),
#    "202504020WAS": ("WAS", "SAC"),
#    "202504020BOS": ("BOS", "MIA"),
#    "202504020HOU": ("HOU", "UTA"),
#    "202504020OKC": ("OKC", "DET"),
#    "202504020DAL": ("DAL", "ATL"),
#    "202504020DEN": ("DEN", "SAS"),
#    "202504020LAC": ("LAC", "NOP"),
#    "202504030WAS": ("WAS", "ORL"),
#    "202504030BRK": ("BRK", "MIN"),
#    "202504030MIA": ("MIA", "MEM"),
#    "202504030PHI": ("PHI", "MIL"),
#    "202504030TOR": ("TOR", "POR"),
#    "202504030LAL": ("LAL", "GSW"),
#    "202504040CHO": ("CHO", "SAC"),
#    "202504040IND": ("IND", "UTA"),
#    "202504040BOS": ("BOS", "PHO"),
#    "202504040TOR": ("TOR", "DET"),
#    "202504040CHI": ("CHI", "POR"),
#    "202504040HOU": ("HOU", "OKC"),
#    "202504040SAS": ("SAS", "CLE"),
#    "202504040GSW": ("GSW", "DEN"),
#    "202504040LAC": ("LAC", "DAL"),
#    "202504040LAL": ("LAL", "NOP"),
#    "202504050ATL": ("ATL", "NYK"),
#    "202504050DET": ("DET", "MEM"),
#    "202504050PHI": ("PHI", "MIN"),
#    "202504050MIA": ("MIA", "MIL"),
#    "202504050LAC": ("LAC", "DAL"),
#    "202504060CHO": ("CHO", "CHI"),
#    "202504060BRK": ("BRK", "TOR"),
#    "202504060OKC": ("OKC", "LAL"),
#    "202504060ATL": ("ATL", "UTA"),
#    "202504060BOS": ("BOS", "WAS"),
#    "202504060CLE": ("CLE", "SAC"),
#    "202504060POR": ("POR", "SAS"),
#    "202504060NOP": ("NOP", "ORL"),
#    "202504060NYK": ("NYK", "PHO"),
#    "202504060DEN": ("DEN", "IND"),
#    "202504060GSW": ("GSW", "HOU"),
#    "202504070DET": ("DET", "SAC"),
#    "202504070MIA": ("MIA", "PHI"),
#    "202504080CHO": ("CHO", "MEM"),
#    "202504080CLE": ("CLE", "CHI"),
#    "202504080IND": ("IND", "WAS"),
#    "202504080ORL": ("ORL", "ATL"),
#    "202504080BRK": ("BRK", "NOP"),
#    "202504080NYK": ("NYK", "BOS"),
#    "202504080MIL": ("MIL", "MIN"),
#    "202504080OKC": ("OKC", "LAL"),
#    "202504080PHO": ("PHO", "GSW"),
#    "202504080LAC": ("LAC", "SAS"),
#    "202504090ORL": ("ORL", "BOS"),
#    "202504090WAS": ("WAS", "PHI"),
#    "202504090DAL": ("DAL", "LAL"),
#    "202504090TOR": ("TOR", "CHO"),
#    "202504090CHI": ("CHI", "MIA"),
#    "202504090MIL": ("MIL", "NOP"),
#    "202504090UTA": ("UTA", "POR"),
#    "202504090GSW": ("GSW", "SAS"),
#    "202504090PHO": ("PHO", "OKC"),
#    "202504090SAC": ("SAC", "DEN"),
#    "202504090LAC": ("LAC", "HOU"),
#    "202504100DET": ("DET", "NYK"),
#    "202504100IND": ("IND", "CLE"),
#    "202504100BRK": ("BRK", "ATL"),
#    "202504100MEM": ("MEM", "MIN"),
#    "202504110DET": ("DET", "MIL"),
#    "202504110IND": ("IND", "ORL"),
#    "202504110PHI": ("PHI", "ATL"),
#    "202504110BOS": ("BOS", "CHO"),
#    "202504110NYK": ("NYK", "CLE"),
#    "202504110CHI": ("CHI", "WAS"),
#    "202504110NOP": ("NOP", "MIA"),
#    "202504110DAL": ("DAL", "TOR"),
#    "202504110DEN": ("DEN", "MEM"),
#    "202504110MIN": ("MIN", "BRK"),
#    "202504110UTA": ("UTA", "OKC"),
#    "202504110PHO": ("PHO", "SAS"),
#    "202504110POR": ("POR", "GSW"),
#    "202504110SAC": ("SAC", "LAC"),
#    "202504110LAL": ("LAL", "HOU"),
#    "202504130ATL": ("ATL", "ORL"),
#    "202504130BOS": ("BOS", "CHO"),
#    "202504130BRK": ("BRK", "NYK"),
#    "202504130CLE": ("CLE", "IND"),
#    "202504130MIA": ("MIA", "WAS"),
#    "202504130MIL": ("MIL", "DET"),
#    "202504130PHI": ("PHI", "CHI"),
#    "202504130GSW": ("GSW", "LAC"),
#    "202504130HOU": ("HOU", "DEN"),
#    "202504130MEM": ("MEM", "DAL"),
#    "202504130MIN": ("MIN", "UTA"),
#    "202504130NOP": ("NOP", "OKC"),
#    "202504130POR": ("POR", "LAL"),
#    "202504130SAC": ("SAC", "PHO"),
#    "202504130SAS": ("SAS", "TOR"),


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

final_gamelogs_path = os.path.join(data_path, "gamelogs.csv")
boxscore_df.to_csv(final_gamelogs_path, mode='a', index=False, header=False, encoding="utf-8")
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

game_index_file_path = os.path.join(data_path, "gameindex.csv")
game_index.to_csv(game_index_file_path, mode='a', index=False, header=False, encoding="utf-8")
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

team_gamelogs_file_path = os.path.join(data_path, "teamgamelogs.csv")
team_gamelogs.to_csv(team_gamelogs_file_path, mode='a', index=False, header=False, encoding="utf-8")
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
