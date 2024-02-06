import glob
import os
from mido import MidiFile

class Song:
    def __init__(self, path):
        midi_path = path + '/*.[mM][iI][dD]'
        matches = glob.glob(midi_path)

        if matches:
            self.file_path = matches[0]
        else:
            self.file_path = None

    def __str__(self):
        return self.file_path

    def display_name(self):
        if self.file_path:
            file_name = os.path.basename(self.file_path)
            abbrev = file_name[:4].upper()
            return abbrev

        return 'none'

    def open_midi(self):
        if self.file_path:
            midi_file = MidiFile(self.file_path)
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
