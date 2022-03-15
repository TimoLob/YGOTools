# Downloads high Quality images from ygoprodeck.com.

## How to build

pip install pyinstaller  
pyinstaller --onefile  deckDownloader.py

## Usage

This tool is intended for use with Project Ignis - EDOPro. However, it will likely work with a lot of other programs or if you just want to download a lot of card images.

To use this tool just double click the executable.
If it auto-detects your EDOPro installation, that's great you will see a list of your decks on the left side. You can skip the next step.

First, select the folder with your ".ydk" files. To do this click the button in the top left and navigate to this folder. By default EDOPro stores your decks in "C:/ProjectIgnis/deck/".

Next, use the arrows to move the decks you want to download to the right side of the window. Use the ">" button to add a deck to the download list and "<" to remove it. You can also select every deck with the ">>>" button.

If you made your selection click the "Download" button. This will open a new window with a progress bar. Just wait until the download is done and close both windows.

Now you need to move the downloaded images manually to the correct location. Just navigate to the data folder. It should be right next to deckDownloader.exe. Now copy everything in the "pics" folder there to your EDOPro installation. This should be "C:/ProjectIgnis/pics/" by default.

