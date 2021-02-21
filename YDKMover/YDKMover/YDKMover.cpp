// YDKMover.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include<filesystem>
#include <string>

using std::cout; using std::cin;
using std::endl; using std::vector;
using std::filesystem::exists;
using std::filesystem::directory_iterator;
using std::filesystem::perms;

int main(int argc, const char* argv[])
{
    if (argc != 2) {
        return 0;
    }
    std::filesystem::path deckPath = argv[1];

    std::filesystem::path targetPath = "D:\\ProjectIgnis\\deck\\"; // Change this for your installation

    if (!(exists(std::filesystem::path(deckPath)) && exists(std::filesystem::path(targetPath)))) {
        std::cout << "Error deck file or deck folder does not exist" << endl;
        return -1;
    }
    std::string deckName;
    std::cout << "Enter the name of the deck(leave blank to not change it)" << endl << ">>>";
    getline(cin, deckName);
    auto path = std::filesystem::path(deckPath);
    std::filesystem::path target = "";


    if (deckName.empty()) {

        target = targetPath.append(path.filename().string());
        //std::filesystem::rename(deckPath, targetPath + path.filename().string());
    }
    else {
        target = targetPath.append(deckName + ".ydk");
        //std::filesystem::rename(deckPath, targetPath + deckName + ".ydk");
    }

    //std::cout << "Moving " << deckPath << " to " << target << endl;
    if (exists(target)) {
        std::cout << "WARNING " << target << " already exists. Are you sure you want to continue(y/n)?" << endl << ">>>";
        char answer;
        std::cin >> answer;
        if (answer == 'y' || answer == 'Y') {
            std::cout << "Overwriting" << std::endl;
            std::filesystem::rename(deckPath, target);
            return 0;
        }
        else {
            std::cout << "Aborting" << std::endl;
            return 1;
        }
    }
    std::filesystem::rename(deckPath, target);
}

