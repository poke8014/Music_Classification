import spotipy
from spotipy.oauth2 import SpotifyOAuth
import env
import os
import time
import random
import re
import requests
from pydub import AudioSegment

scope = "user-library-read"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=env.CLIENT_ID,
                              client_secret= env.CLIENT_SECRET,
                              redirect_uri=env.REDIRECT_URI,
                              scope=scope))

# stores playlist song names, track artist, track ID and preview url into a list of dictionaries
def get_playlist_info(playlist_id):
    playlist_info = []
    offset = 0      # use offset to iterate through playlists with more than 100 songs
    playlist = sp.playlist_tracks(playlist_id, offset=offset)   # can only fetch 100 songs at a time

    while (len(playlist['items']) != 0):
        # iterate through playlist in segments of <= 100
        for idx, track in enumerate(playlist['items']):
            current = track['track']
            playlist_info.append({'name': current['name'],
                                  'artist': current['artists'][0]['name'],
                                  'id': current['id'],
                                  'preview': current['preview_url'],
                                  'playlist': playlist_id})
        offset += len(playlist['items'])    # checks next set of songs
        playlist = sp.playlist_tracks(playlist_id, offset=offset)   # update offset
    return playlist_info

#downloads audio as wav file
def download_track(track):
    # store in folder named Audio
    if not os.path.exists('../Audio'):
        os.makedirs('../Audio')

    thisName = track['name']
    thisArtist = track['artist']
    thisID = track['id']
    thisUrl = track['preview']
    thisFolder = track['playlist']

    # store in subdirectory named after playlist ID
    # check if folder exist
    os.makedirs('Audio/' + thisFolder + '/', exist_ok=True)

    if thisUrl != None:
        time.sleep(random.randrange(0,42)/100)
        # maybe do a check if file exists here. Would need to move "thisname"
        try:
            thisSample = requests.get(thisUrl)
            if len(thisSample.content) > 0:

                saveName = 'Audio/' + thisFolder + '/' + thisArtist + "_" + thisName + "_" + thisID
                # Clean up filename
                saveName = re.sub(r'[^0-9a-zA-Z\_/]+', '', saveName) + '.mp3'

                # save mp3, convert to wav, delete mp3
                open(saveName, 'wb').write(thisSample.content)
                convert_me = AudioSegment.from_mp3(saveName)
                convert_me.export(saveName.replace(".mp3", ".wav"),
                                  format="wav")
                os.remove(saveName)
                # add to database
                success = 1
        except:
            success = 0
    else:
        success = 0
    output = (thisID, success)
    return output

# downloads entire playlist given playlist ID
def download_playlist(playlist_ID, max=float('inf')):
    playlist = get_playlist_info(playlist_ID)
    counter = 0
    for song in playlist:
        id, downloaded = download_track(song)
        print(id, downloaded)
        counter += downloaded
        if counter >= max:
            break

playlists = {'pop':"37i9dQZF1DX0kbJZpiYdZl",        # Hot Hits USA
             'blues':"37i9dQZF1DXd9rSDyQguIk",      # Blues Classics
             'classical':"37i9dQZF1DWWEJlAGA9gs0",  # Classical Essentials
             'country':"37i9dQZF1DWZBCPUIUs2iR",    # Country's Greatest Hits
             'indie':"37i9dQZF1DX26DKvjp0s9M",      # Essential Indie
             'hiphop':"37i9dQZF1DXbkfWVLd8wE3",     # Hip-Hop Classics Party
             'jazz':"37i9dQZF1DXbITWG1ZJKYt",       # Jazz Classics
             'metal':"37i9dQZF1DWWOaP4H0w5b0",      # Metal Essentials
             'reggae':"37i9dQZF1DWSiyIBdVQrkk",     # One Love
             'rock':"37i9dQZF1DWXRqgorJj26U"}       # Rock Classics

# loops through all playlists and downloads MAX number of songs with preview
for playlist, song_id in playlists.items():
    # max=float('inf')
    max = 50
    songs = get_playlist_info(song_id)
    counter = 0
    for song in songs:
        song['playlist'] = playlist
        id, downloaded = download_track(song)
        counter += downloaded
        print(id, downloaded)
        if counter >= max:
            break
