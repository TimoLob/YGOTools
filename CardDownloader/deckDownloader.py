import yugioh
from PIL import Image
import time
import os
import requests
import glob
import tkinter as tk
from tkinter import filedialog

verbose = False

def log(*args):
    if verbose:
        print(*args)

def update_progress(progress):
    progress = int(progress*100)
    print("\r [{0}] {1}%".format('#'*int(progress/10), progress),end="")


def load_blacklist():
    if not os.path.isfile("./blacklist.txt"):
        return set()
    ids = set()
    with open("blacklist.txt") as infile:
        lines = infile.readlines()
        for line in lines:
            ids.add(line.strip())
    return ids

def write_blacklist(blacklist):
    with open("blacklist.txt","w") as outfile:
        for id in blacklist:
            outfile.write(id+"\n")
    


def download_image(url,filename):
    #print(url,filename)
    resp = requests.get(url, stream=True).raw
    img = Image.open(resp)
    if img.mode in ("RGBA", "P"): 
        img = img.convert("RGB")
    img.save(filename,"JPEG")
    return True

def download_card(card):
    out_path = "./pics/"+str(card.id)+".jpg"
    img_url = "https://ygoprodeck.com/pics/"+str(card.id)+".jpg"
    if not download_image(img_url,out_path):
        print("Failed to Download "+card.name)
        return False
    return True


def download_set(ids,delay=1):
    blacklist = load_blacklist()

    print(f"Total: {len(ids)} cards.")
    ids_on_blacklist = ids.intersection(blacklist)
    ids = ids-ids_on_blacklist
    print("Downloading",len(ids),"cards...")

    print(f"Skipping {len(ids_on_blacklist)} cards.")
    failed_ids = set()
    for index,id in enumerate(ids):
        update_progress(index/len(ids))
        try:
            card = yugioh.get_card(card_id=id)
        except KeyError:
            log("Failed to get card info for id",id)
            failed_ids.add(id)
            continue
        if id in blacklist:
            log(card.name,"already downloaded")
            continue
        if download_card(card):
            blacklist.add(id)
            log("Downloaded",card.name)
        else:
            failed_ids.add(id)
            
        time.sleep(delay)
        write_blacklist(blacklist)
    return {"failed" : failed_ids,"downloaded":ids}


class Deck:
    def __init__(self,path):
        self.path = path
        self.name = os.path.basename(path).replace(".ydk","")
        self._ids = None
    def get_ids(self):
        if self._ids:
            return self._ids
        self._ids = set()
        # Read all card ids from deckfile
        with open(self.path,"r") as deckfile:
            lines = deckfile.readlines()
            for line in lines:
                if not "#" in line and not "!" in line:
                    line = line.strip()
                    if line:
                        self._ids.add(line)
        return self._ids
    def __str__(self):
        return "Deck "+self.name


def get_deck_directory(let_user_choose=False):
    default_dirs = ["C:/ProjectIgnis/deck/","D:/ProjectIgnis/deck/","/home/timo/Games/ProjectIgnis/deck/"]
    if let_user_choose:
        default_dirs = []
    for d in default_dirs:
        if len(list(glob.glob(d+"*.ydk"))) > 0:
            print("Found decks in",d)
            return d
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askdirectory(title="Select the directory that contains your decks")
    return file_path+"/"
    


def main():
    deck_dir = get_deck_directory()
    
    deck_paths = list(glob.glob(deck_dir+"*.ydk"))
    decks = [Deck(x) for x in deck_paths]

    for index,deck in enumerate(decks):
        print(index,"-",deck.name)

    decks_to_download = input("Please enter the deck ids you want to download(separatet by comma) or '*' if you want to download all of them\n")
    if("*" in decks_to_download):
        decks_to_download = list(range(len(decks)))
    else:
        decks_to_download = decks_to_download.split(",")
        decks_to_download = [int(x.strip()) for x in decks_to_download]

    if not os.path.isdir("./pics"):
        os.mkdir("./pics")

    ids_to_download = set()
    for index in decks_to_download:
        if(index>len(decks) or index < 0):
            print("Invalid Index:",index)
            return
        deck = decks[index]
        print("Collecting",deck)

        ids_to_download = ids_to_download.union(deck.get_ids())
    result = download_set(ids_to_download)
    update_progress(1)
    failed = result["failed"]
    print("\n-------Done----------\n")

    print("Downloaded",len(result["downloaded"]),"cards.")
    if len(failed)>0:
        for id in failed:
            print("Failed to download id",id)

    
    input()

    edopro_pics_dir = os.path.join(os.path.join(deck_dir,os.path.pardir),"pics")
    if len(result["downloaded"])>0 and os.path.isdir(edopro_pics_dir):
        try:
            os.startfile(edopro_pics_dir)
        except AttributeError:
            pass

    

if __name__=="__main__":
    main()