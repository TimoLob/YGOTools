import yugioh
from PIL import Image
import time
import os
import requests
import glob
import tkinter as tk
from tkinter import filedialog
from abc import ABC, abstractmethod

class Downloader(ABC):
    def __init__(self,data_dir="./data",verbose = False) -> None:
        self._verbose = verbose
        self._blacklist = set()
        self._decks = set()
        self._card_ids = set()
        self._data_dir = data_dir

        self._path_to_blacklist = os.path.join(data_dir,"blacklist.txt")
        self._path_to_images = os.path.join(data_dir,"pics/")

        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)

        if not os.path.isdir(self._path_to_images):
            os.mkdir(self._path_to_images)

    def log(self,*args):
        if self._verbose:
            print(*args)
    
    def add_deck(self,deck):
        self.log("Added deck",deck)
        self._decks.add(deck)
        self._card_ids = self._card_ids.union(deck.get_ids())

    def load_blacklist(self):
        if not os.path.isfile(self._path_to_blacklist):
            return set()
        with open(self._path_to_blacklist) as infile:
            lines = infile.readlines()
            for line in lines:
                self._blacklist.add(line.strip())
        return self._blacklist

    def write_blacklist(self):
        with open(self._path_to_blacklist,"w") as outfile:
            for id in self._blacklist:
                outfile.write(id+"\n")
        

    def download_image(self,url,filename):
        resp = requests.get(url, stream=True).raw
        img = Image.open(resp)
        if img.mode in ("RGBA", "P"): 
            img = img.convert("RGB")
        img.save(filename,"JPEG")
        return True

    def download_card(self,card):
        out_path = os.path.join(self._path_to_images,str(card.id)+".jpg")
        img_url = "https://ygoprodeck.com/pics/"+str(card.id)+".jpg"
        if not self.download_image(img_url,out_path):
            print("Failed to Download "+card.name)
            return False
        return True

    @abstractmethod
    def update_progress(self,progress):
        pass

    @abstractmethod
    def onCardDownload(self,id,name=""):
        pass

    @abstractmethod
    def onFailedDownload(self,id,name=""):
        pass

    def start_download(self,delay=1):        

        ids = self._card_ids
        print(f"Total: {len(ids)} cards.")
        ids_on_blacklist = ids.intersection(self._blacklist)
        ids = ids-ids_on_blacklist
        print("Downloading",len(ids),"cards...")

        print(f"Skipping {len(ids_on_blacklist)} cards.")
        failed_ids = set()
        for index,id in enumerate(ids):
            self.update_progress(index/len(ids))
            try:
                card = yugioh.get_card(card_id=id)
            except KeyError:
                failed_ids.add(id)
                self.onFailedDownload(id)
                continue
            if id in self._blacklist:
                #self.log(card.name,"already downloaded")
                continue
            if self.download_card(card):
                self._blacklist.add(id)
                self.onCardDownload(id,name=card.name)
            else:
                failed_ids.add(id)
                self.onFailedDownload(id,name=card.name)
            
            time.sleep(delay)
        self.update_progress(1)
        return {"failed" : failed_ids,"downloaded":ids}


class CLIDownloader(Downloader):
    def __init__(self,data_dir="./data",verbose = False):
        super(CLIDownloader,self).__init__(data_dir=data_dir,verbose=verbose)

    def onCardDownload(self,id, name=""):
        self.log("Downloaded",name)

    def onFailedDownload(self, id, name=""):
        self.log("Failed to download card with id:",id,end="")
        if name:
            self.log(name)
        else:
            self.log()
    

    def update_progress(self,progress):
        progress = int(progress*100)
        print("\r [{0}] {1}%".format('#'*int(progress/10), progress),end="")

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

    downloader = CLIDownloader()
    downloader.load_blacklist()

    for index in decks_to_download:
        if(index>len(decks) or index < 0):
            print("Invalid Index:",index)
            return
        deck = decks[index]
        #ids_to_download = ids_to_download.union(deck.get_ids())
        downloader.add_deck(deck)
    result = downloader.start_download()#download_set(ids_to_download,ignore_blacklist=ignore_blacklist)
    downloader.write_blacklist()
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