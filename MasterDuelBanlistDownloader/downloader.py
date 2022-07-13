
from bs4 import BeautifulSoup
import requests
import os
import json
from datetime import datetime
import re

url = "https://db.ygoprodeck.com/master-duel-banlist/"

page = requests.get(url)

if False:
    with open("page.html","w") as outfile:
        outfile.write(str(page.content))
soup = BeautifulSoup(page.content, "html.parser")



banned = soup.find(id="list-banned")
semi   = soup.find(id="list-semilimited")
limited = soup.find(id="list-limited")

def get_card_names(parent):
    result = []
    cards = parent.find_all("figcaption")
    for card in cards:
        c = card.find("span",class_="container-name")
        result.append(c.text)
    return result


banned_cards = get_card_names(banned)
semi_limted_cards = get_card_names(semi)
limited_cards = get_card_names(limited)


        

with open("banlist.txt","w") as outfile:
    for title, l in zip(["Banned","Semi-limted","Limited"],[banned_cards,semi_limted_cards,limited_cards]):
        outfile.write(title+"\n")
        for card in l:
            outfile.write(card+"\n")

# <div id="list-banned">
# <div id="list-semilimited">
# <div id="list-limited">

def load_card_database(force_update=False):
    api = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    if force_update or (not os.path.exists("data/card_database.json")):
        data = requests.get(api)
        json_data = data.json()
        with open("data/card_database.json","w") as outfile:
            json.dump(json_data,outfile)
    else:
        with open("data/card_database.json","r") as infile:
            json_data = json.load(infile)

    return json_data

def get_lf_date(root):
    div = root.find(class_="ranking-msg")
    p = div.find("p")
    print(p.text)
    date = p.text.split(":")[1]
    print(date)
    day,month,year = date[1:].split(" ")
    day = int(re.sub("[A-Za-z]+","",day))
    month = ["January","February","..."].index(month)+1
    year = int(year.replace(".",""))
    return datetime(year,month,day)



def get_card_id(db,names):
    data = db["data"]
    result = []
    for card in data:
        if card["name"] in names:
            result.append([card["name"],card["id"]])
    
    print(len(result))
    return result


db = load_card_database()

banned_cards = get_card_id(db,banned_cards)
semi_limted_cards = get_card_id(db,semi_limted_cards)
limited_cards = get_card_id(db,limited_cards)

date = get_lf_date(soup)
with open("master_duel_banlist.lflist.conf","w") as outfile:
    outfile.write(f"#[{date.year}.{date.month} Master Duel]\n!{date.year}.{date.month} Master Duel\n")
    outfile.write("#Forbidden MD\n")
    for name,cid in banned_cards:
        s = f"{cid} 0 --{name}\n"
        outfile.write(s)

    outfile.write("#Limited MD\n")
    for name,cid in limited_cards:
        s = f"{cid} 1 --{name}\n"
        outfile.write(s)

    outfile.write("#Semi-Limited MD\n")
    for name,cid in semi_limted_cards:
        s = f"{cid} 2 --{name}\n"
        outfile.write(s)
    