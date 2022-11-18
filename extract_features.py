import os
import pandas as pd
import numpy as np
import librosa
import re
import csv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
preview_length = 30     # seconds

# takes in file location and returns an array of audio features extracted using librosa
def extract_features(file, genre, offset=None, duration=None, ver=''):
    name = re.split('[^a-zA-Z0-9]+', file)  # split on non-alphanumeric chars
    row = [(name[-2]+ver)]    # song id
    y, sr = librosa.load(file, offset=offset, duration=duration)  # audio time series and sampling rate
    row.append(len(y))      # length
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
    harmony, perceptr = librosa.effects.hpss(y)
    tempo, _ = librosa.beat.beat_track(y=y, sr = sr)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)

    row.extend([np.mean(chroma_stft), np.var(chroma_stft),
               np.mean(rms), np.var(rms),
               np.mean(spectral_centroid), np.var(spectral_centroid),
               np.mean(spectral_bandwidth), np.var(spectral_bandwidth),
               np.mean(rolloff), np.var(rolloff),
               np.mean(zero_crossing_rate), np.var(zero_crossing_rate),
               np.mean(harmony), np.var(harmony),
               np.mean(perceptr), np.var(perceptr),
               tempo])

    for mfcc in mfccs:
        row.extend([np.mean(mfcc), np.var(mfcc)])
    row.append(genre)

    return row

# creating header for file
def make_header():
    header = ['filename', 'length']
    labels = ['chroma_stft', 'rms', 'spectral_centroid',
              'spectral_bandwidth', 'rolloff',
              'zero_crossing_rate', 'harmony',
              'perceptr']
    header.append('tempo')
    for label in labels:
        header.extend([f'{label} mean', f'{label} var'])
    for i in range(1, 21):
        header.append(f'mfcc{i}')
    header.append('label')

    return header

# extracts features from all songs in Audio folder and returns a csv file
def extract():
    file = open('spotify_features_sec.csv', 'w', newline='')
    header = make_header()
    with file:
        writer = csv.writer(file)
        writer.writerow(header)
        for genre in os.listdir(f'{ROOT_DIR}/Audio/'):
            for song in os.listdir(f'{ROOT_DIR}/Audio/{genre}'):
                print(song)
                row = extract_features(f'{ROOT_DIR}/Audio/{genre}/{song}', genre)
                writer.writerow(row)

# extracts features from subsections of the song
def extract_sections(seconds):
    file = open(f'spotify_features_{seconds}sec.csv', 'w', newline='')
    header = make_header()
    with file:
        writer = csv.writer(file)
        writer.writerow(header)
        for genre in os.listdir(f'{ROOT_DIR}/Audio/'):
            for song in os.listdir(f'{ROOT_DIR}/Audio/{genre}'):
                for i in range(preview_length//seconds):
                    print(song+str(i))
                    offset = i * seconds
                    duration=offset + seconds
                    row = extract_features(f'{ROOT_DIR}/Audio/{genre}/{song}',
                                           genre,
                                           offset=offset,
                                           duration=duration,
                                           ver=f'.{i}')
                    writer.writerow(row)
# uncomment to run
# extract()
# extract_sections(3)