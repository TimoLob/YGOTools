import yugioh
from PIL import Image
import time
import os
import requests
import glob
import tkinter as tk
from tkinter import filedialog

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
    outPath = "./pics/"+str(card.id)+".jpg"
    imgUrl = "https://ygoprodeck.com/pics/"+str(card.id)+".jpg"
    if not download_image(imgUrl,outPath):
        print("Failed to Download "+card.name)
        return False
    return True


def download_deck(deck,delay=1):
    blacklist = load_blacklist()
    ids = deck.get_ids()
    
    for id in ids:
        card = yugioh.get_card(card_id=id)
        if id in blacklist:
            print(card.name,"in blacklist")
            continue
        if download_card(card):
            blacklist.add(id)
            print("Downloaded",card.name)
            
        time.sleep(delay)
        write_blacklist(blacklist)


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


def get_deck_directory(alwaysLetUserChoose=False):
    default_dirs = ["C:/ProjectIgnis/deck/","D:/ProjectIgnis/deck/","~/Games/ProjectIgnis/deck/"]
    if alwaysLetUserChoose:
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
    
    deckDir = get_deck_directory()
    
    deck_paths = list(glob.glob(deckDir+"*.ydk"))
    decks = [Deck(x) for x in deck_paths]

    for index,deck in enumerate(decks):
        print(index,"-",deck.name)

    decksToDownload = input("Please enter the deck ids you want to download(separatet by comma)\n").split(",")
    decksToDownload = [int(x.strip()) for x in decksToDownload]


    if not os.path.isdir("./pics"):
        os.mkdir("./pics")

    for index in decksToDownload:
        deck = decks[index]
        print("--- Downloading",deck,"---")
        download_deck(deck)
    print("-------Done----------")
    input()

    edopro_pics_dir = os.path.join(os.path.join(deckDir,os.path.pardir),"pics")
    if os.path.isdir(edopro_pics_dir):
        os.startfile(edopro_pics_dir)

    

if __name__=="__main__":
    main()