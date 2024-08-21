import glob
import os
from mido import MidiFile

class Song:
    def __init__(self, path):
        self.base_path = path

        midi_path = path + '/*.[mM][iI][dD]'
        midi_matches = glob.glob(midi_path)

        if midi_matches:
            self.midi_file_path = midi_matches[0]
        else:
            self.midi_file_path = None

        wav_path = path + '/*.mp3'
        wav_matches = glob.glob(wav_path)

        if wav_matches:
            self.wav_file_path = wav_matches[0]
        else:
            self.wav_file_path = None

    def __str__(self):
        return self.midi_file_path

    def display_name(self):
        file_name = os.path.basename(self.base_path)
        abbrev = file_name[:4].upper()
        return abbrev

    def open_midi(self):
        if self.midi_file_path:
            midi_file = MidiFile(self.midi_file_path)
            first = next(midi_file.play()) # this forces more stuff to load so it plays right away
            return midi_file

        return None

class Songs:
    def __init__(self):
        midi_folders = sorted(glob.glob("/home/crushcurl/app/midi/*"))
        self.songs = list(map(lambda f:Song(f), midi_folders))

    def get(self, i):
        return self.songs[i]

    def count(self):
        return len(self.songs)
