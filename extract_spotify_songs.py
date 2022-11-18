#%%
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import env
import os
import time
import random
import requests
from pydub import AudioSegment

#%%
scope = "user-library-read"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=env.CLIENT_ID,
                              client_secret= env.CLIENT_SECRET,
                              redirect_uri=env.REDIRECT_URI,
                              scope=scope))

#%%
# stores playlist song names, track artist, track ID and preview url into a list of dictionaries
# optional max parameter will limit playlist size based on songs with a preview url
def get_playlist_info(playlist_id, max=float('inf')):
    playlist_info = []
    offset = 0
    counter = 0
    playlist = sp.playlist_tracks(playlist_id, offset=offset)

    while (len(playlist['items']) != 0):
        # iterate through playlist in segments of <= 100
        for idx, track in enumerate(playlist['items']):
            current = track['track']
            playlist_info.append({'name': current['name'],
                                  'artist': current['artists'][0]['name'],
                                  'id': current['id'],
                                  'preview': current['preview_url'],
                                  'playlist': playlist_id})
            if current['preview_url']:
                counter+=1
            if counter >= max:
                return playlist_info
        offset += len(playlist['items'])    # checks next set of songs
        playlist = sp.playlist_tracks(playlist_id, offset=offset)
    return playlist_info

#downloads audio as mp3
def download_track(track):
    # store in folder named Audio
    if not os.path.exists('Audio'):
        os.makedirs('Audio')

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
                # Clean up filename
                thisName = thisName.replace('/', '')
                thisName = thisName.replace('\\', '')
                thisName = thisName.replace('.', '')
                saveName = 'Audio/' + thisFolder + '/' + thisArtist + "_" + thisName + "_" + thisID + '.mp3'
                saveName = saveName.replace(" ", "_")
                saveName = saveName.replace(":", "")
                saveName = saveName.replace("!", "")
                saveName = saveName.replace('"', '')
                saveName = saveName.replace('-', '')
                saveName = saveName.replace('?', '')
                saveName = saveName.replace('<', '')
                saveName = saveName.replace('>', '')
                saveName = saveName.replace('\\', '')
                saveName = saveName.replace('*', '')
                saveName = saveName.replace('|', '')

                open(saveName, 'wb').write(thisSample.content)
                convert_me = AudioSegment.from_mp3(saveName)
                convert_me.export(saveName.replace(".mp3", ".wav"),
                                  format="wav")
                # add to database
                success = 1
        except:
            success = 0
    else:
        success = 0
    output = (thisID, success)
    return output

# downloads entire playlist given playlist ID
def download_playlist(playlist_ID):
    playlist = get_playlist_info(playlist_ID)
    for song in playlist:
        print(download_track(song))
#%%
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

for playlist, id in playlists.items():
    songs = get_playlist_info(id, max=50)
    for song in songs:
        song['playlist'] = playlist
        print(download_track(song))

#%%
# import pandas as pd
# import numpy as np
# import librosa
# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# genres = list(os.listdir(f'{ROOT_DIR}/Audio/'))
#
# y, sr = librosa.load(f'{ROOT_DIR}/Audio/{genres[0]}/Freddie_King_Stumble_0RTjFVHvqjTdpX2NawwyXI.mp3')
# print('y:', y, '\n')
# print('y shape:', np.shape(y), '\n')
# print('Sample Rate (KHz):', sr, '\n')
#
# # Verify length of the audio
# print('Check Len of Audio:', 661794/22050)