from bs4 import BeautifulSoup
import requests
import re
import os
import eyed3
import sys

#user will enter the directory path and this will be stored as path
path = input("paste path: ")

#create a few empty lists
audiofiles = []
songs = []
genius_path = []
all_song_lyrics = []

#create a variable to see show user how many songs had their lyrics found. if this is less than the total amount of mp3s come the end of the script, no text files will be created
success = 0

#the directory may contain files which aren't mp3s. This filters the files in the directory and only adds .mp3s to the SONGS list
for item in os.listdir(path):
    if item.endswith('.mp3'):
        songs.append(item)

#this loop uses the eyed3 module. For each mp3 found above, the file is loaded and then a string which will be used in the genius.com request later is created and added to the GENIUS_PATH list
for iteration, mp3 in enumerate(songs):
    audiofiles.append(eyed3.load(path +"\\" +songs[iteration]))
    genius_path.append(re.sub(" ", "-", " ".join([audiofiles[iteration].tag.artist, audiofiles[iteration].tag.title])))

#this checks to make sure the directory contains some mp3s. If no mp3s are in the directory, the script is exited
if len(songs) < 1:
    print("There are no .mp3 files in this directory")
    sys.exit()

#main loop which scrapes the lyrics from genius.com and then adds the lyrics to the ALL_SONG_LYRICS list. 
for artist_title in genius_path:
    songLyrics = ""
    tries = 0
    while (len(songLyrics) == 0) and (tries < 10):
        
        artist_title = re.sub("[’, ']", "", artist_title)
        url = "http://genius.com/" + artist_title +"-lyrics"

        req = requests.get(url)

        src = req.content
        soup = BeautifulSoup(req.text, "html.parser")
        lyricDivs = soup.find_all(class_="lyrics")


        for div in lyricDivs:
            songLyrics = songLyrics.join([songLyrics, div.text])

        tries += 1
        if tries == 10 and len(songLyrics) == 0:
            print("I've tried " + str(tries) + " times and I couldn't find lyrics for " + artist_title)
        elif len(songLyrics) > 0:
            success += 1
            all_song_lyrics.append(songLyrics)

#Checks to make sure all songs have had their lyrics found.
if success/len(genius_path) == 1:
    
    #loops through all the songs and creates a .txt file which corresponds to each mp3 file
    for iteration, song_lyrics in enumerate(all_song_lyrics):
        print(audiofiles[iteration].tag.title)
        song_name = "".join([audiofiles[iteration].tag.title, ".txt"])
        with open(path + "\\" + song_name, 'w', encoding='utf-8') as f:
            f.write(song_lyrics)

    #lets the user know the process was successful
    print("Success! " + str(success) + "\\" + str(len(genius_path)) + " songs had their lyrics found")

#lets the user know the process was unsuccessful. 
else:
    print("I couldn't find lyrics for all songs in the directory. The mp3 song titles may be incorrect or contain special characters. I have not created any .txt files as a result")
