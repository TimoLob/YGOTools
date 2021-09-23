import builtins
from deckDownloader import Deck,Downloader 

import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

import glob
import os
import threading

class Select_Deck_Window:
    def __init__(self):
        self.current_path = "C:/ProjectIgnis/deck/"
        
        window = self.build_window()
        self.update_directory()
        if len(self.decks)<1:
            self.current_path = "D:/ProjectIgnis/deck/"
            self.update_directory()
        
        window.mainloop()

    def choose_dir_callback(self):
        path = tk.filedialog.askdirectory(mustexist = True)
        if not path:
            return
        self.current_path=path+"/"
        self.update_directory()

    def update_directory(self):
        self._path_var.set("Current Path : "+self.current_path)
        self._avail_deck_list.delete(0,tk.END)
        self._selected_deck_list.delete(0,tk.END)

        # Load .ydk files from directory
        deck_paths = list(glob.glob(self.current_path+"*.ydk"))
        self.decks = [Deck(x) for x in deck_paths]
        for deck in self.decks:
            self._avail_deck_list.insert(tk.END, deck.name)


    def select_deck(self):
        selection = self._avail_deck_list.curselection()
        for x in selection[::-1]:
            deck = self._avail_deck_list.get(x)
            self._avail_deck_list.delete(x)
            self._selected_deck_list.insert(tk.END,deck)


    def select_all(self):
        decks = self._avail_deck_list.get(0,tk.END)
        self._avail_deck_list.delete(0,tk.END)
        for x in decks:
            self._selected_deck_list.insert(tk.END,x)

    def deselect_deck(self):
        selection = self._selected_deck_list.curselection()
        for x in selection[::-1]:
            deck = self._selected_deck_list.get(x)
            self._selected_deck_list.delete(x)
            self._avail_deck_list.insert(tk.END,deck)

    def deselect_all(self):
        decks = self._selected_deck_list.get(0,tk.END)
        self._selected_deck_list.delete(0,tk.END)
        for x in decks:
            self._avail_deck_list.insert(tk.END,x)

    def on_close(self):
        self._window.destroy()

    def build_window(self):
        self._window = tk.Tk()
        self._window.protocol("WM_DELETE_WINDOW",self.on_close)
        self._window.title("HD Card Downloader")

        # ROW 0 - Directory Selector

        row = 0
        self._choose_dir_btn = tk.Button(self._window,text="Choose .ydk directory",command=self.choose_dir_callback)
        self._choose_dir_btn.grid(row=row,column=0)

        self._path_var = tk.StringVar(self._window)
        
        self._current_path_label = tk.Label(self._window,textvariable=self._path_var)
        self._current_path_label.grid(row=row,column=2)
        

        # ROW 1 - Labels for both deck lists
        row = 1
        avail_label = tk.Label(self._window,text="Available Decks")
        avail_label.grid(row = row,column = 0)

        selected_label = tk.Label(self._window,text="Selected Decks")
        selected_label.grid(row = row,column = 2)

        # ROW 2 - Scrollable Deck Lists
        row = 2
        # Subgrid - List of available decks
        avail_deck_frame = tk.Frame(self._window)
        scrollbar = tk.Scrollbar(avail_deck_frame)
        self._avail_deck_list = tk.Listbox(avail_deck_frame, yscrollcommand = scrollbar.set,selectmode=tk.MULTIPLE)
        #for line in range(100):
        #   self._avail_deck_list.insert(tk.END, "This is line number " + str(line))

        scrollbar.config( command = self._avail_deck_list.yview )
        self._avail_deck_list.grid(row=0,column=0,sticky = tk.W+tk.E)
        scrollbar.grid(row=0,column=1,sticky=tk.N+tk.S)
        avail_deck_frame.grid(row=row,column=0,sticky=tk.W+tk.E)


        # Subgrid - Buttons to move decks
        move_frame = tk.Frame(self._window)

        select_deck_button = tk.Button(move_frame,text=">",command=self.select_deck)
        select_deck_button.grid(row = 0,column=0,sticky=tk.W+tk.E)

        select_all_deck_button = tk.Button(move_frame,text=">>>",command=self.select_all)
        select_all_deck_button.grid(row = 1,column=0,sticky=tk.W+tk.E)

        deselect_deck_button = tk.Button(move_frame,text="<",command=self.deselect_deck)
        deselect_deck_button.grid(row = 2,column=0,sticky=tk.W+tk.E)

        deselect_all_deck_button = tk.Button(move_frame,text="<<<",command=self.deselect_all)
        deselect_all_deck_button.grid(row = 3,column=0,sticky=tk.W+tk.E)
        move_frame.grid(row=2,column=1)

        # Subgrid - list of selected decks
        selected_deck_frame = tk.Frame(self._window)
        scrollbar2 = tk.Scrollbar(selected_deck_frame)
        self._selected_deck_list = tk.Listbox(selected_deck_frame, yscrollcommand = scrollbar2.set )
        # for line in range(100):
        #     self._selected_deck_list.insert(tk.END, "This is line number " + str(line))

        scrollbar2.config( command = self._selected_deck_list.yview )
        self._selected_deck_list.grid(row=0,column=0,sticky = tk.W+tk.E)
        scrollbar2.grid(row=0,column=1,sticky=tk.N+tk.S)
        selected_deck_frame.grid(row=row,column=2,sticky=tk.W+tk.E)

        # ROW 3 - Download Button
        row = 3
        self._download_btn = tk.Button(self._window,text="Download",command=self.start_download)
        self._download_btn.grid(row=row,column=0,sticky="w")


        return self._window

    def start_download(self):

        decknames = self._selected_deck_list.get(0,tk.END)
        if len(decknames)<1:
            return
        decks_to_download = set()
        for deckname in decknames:
            for deck in self.decks:
                if deckname == deck.name:
                    decks_to_download.add(deck)
        

        downloader = DeckDownloaderGUI(self._window)
        for deck in decks_to_download:
            downloader.add_deck(deck)

        
        downloader.start()
        


class DeckDownloaderGUI(Downloader):
    def __init__(self,root,data_dir="./data",verbose = False):
        super(DeckDownloaderGUI,self).__init__(data_dir=data_dir,verbose=False)
        self._root = root

    def start(self):
        self.load_blacklist()
        window = tk.Toplevel(self._root,height=500,width=1000)
        self.window = window
        # Row 0 - Progress bar and % display
        self.pb = ttk.Progressbar(window,orient="horizontal",mode="determinate",length=1000)
        self.pb.grid(column=0,row=0)
        self.progress_text = tk.StringVar(window)
        self.progress_text.set("0%")
        progress_label = tk.Label(window,textvariable=self.progress_text)
        progress_label.grid(row=0,column=1)

        # ROW 1 - Card Name and card image
        self.card_name = tk.StringVar()

        card_name_label = tk.Label(window,textvariable=self.card_name)
        card_name_label.grid(row=1,column=0)
        self.canvas = tk.Canvas(window,width=421,height=614)
        self.canvas.grid(row=2,column=0)

        window.protocol("WM_DELETE_WINDOW",self.on_close)

        self.thread = threading.Thread(target=self.multithreaded_download)
        self.thread.start()

        window.mainloop()

    def on_close(self):
        self.abort = True
        self.thread.join(timeout = 3)
        if not self.thread.is_alive():
            self.window.destroy()

    def onStartDownload(self,num_ids, num_on_blacklist):
        self.window.title("Downloading "+str(num_ids)+ " cards.")

    def onCardDownload(self, id, name=""):
        self.card_name.set(name)
        path = os.path.join(self._path_to_images,str(id)+".jpg")
        self.image = ImageTk.PhotoImage(file=path)
        self.canvas.create_image(0,0,image=self.image,anchor="nw")

    def onFailedDownload(self, id, name=""):
        self.log("Failed to download card with id:",id,end="")
        if name:
            self.log(name)
        else:
            self.log()

    def multithreaded_download(self):
        self.load_blacklist()
        self.start_download(delay=0.3)
        self.write_blacklist()

    def update_progress(self, progress):
        self.progress_text.set(str(int(progress*100))+"%")
        self.pb["value"] = int(progress*100)
    

def select_decks():
    sdwindow = Select_Deck_Window()

    

if __name__=="__main__":
    select_decks()

