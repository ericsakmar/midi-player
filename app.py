import os
import threading
import RPi.GPIO as GPIO
import glob
import time
from pygame import mixer
import mido

from song import Song, Songs
from display import Display
from midi import Midi

# set-up guide: https://learn.adafruit.com/matrix-7-segment-led-backpack-with-the-raspberry-pi/configuring-your-pi-for-i2c
# https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
# https://www.circuitbasics.com/how-to-set-up-buttons-and-switches-on-the-raspberry-pi/
# https://learn.adafruit.com/read-only-raspberry-pi/overview

# sets up buttons
NEXT_PIN = 24
PREV_PIN = 23
PLAY_PIN = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(NEXT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PREV_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PLAY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

mixer.pre_init(buffer=2048)
mixer.init()
mixer.music.set_volume(0.5)

MIDI_IN_CHANNEL = 9 # it's actually 10, this is the channel for the pi itself (selecting songs, etc)
DRUM_MACHINE_CHANNEL = 10 # actually 11, this is the Lofi's PROJECT CHANNEL
SONG_PLAYBACK_CC = 1
SONG_PLAYBACK_START = 127
SONG_PLAYBACK_STOP = 0

# globals
midi = Midi()
display = Display()
songs = Songs()
selected_index = 0
selected_midi = None
playing = False

def update_display():
    abbrev = songs.get(selected_index).display_name()

    if playing:
        abbrev += '.'

    display.print(abbrev)

def select(index):
    global selected_index
    global selected_midi
    global playing

    stop()
    display.print('load')

    selected_index = index
    selected_midi = songs.get(index).open_midi()
    update_display()

def next():
    nextIndex = selected_index + 1
    if nextIndex < songs.count():
        select(nextIndex)

def previous():
    nextIndex = selected_index - 1
    if nextIndex >= 0:
        select(nextIndex)

def play():
    global playing

    playing = True
    update_display()

    play_wav()
    start_drums()

    # we'll bring this back later
    # play_midi()

# synchronous, returns when the wav is over
def play_wav():
    wav = songs.get(selected_index).wav_file_path

    if wav:
        mixer.music.load(wav)
        mixer.music.play()

        while mixer.music.get_busy():
            if playing == False:
                mixer.music.stop()

def play_midi():
    global playing

    try:
        for msg in selected_midi.play():
            midi.output_port.send(msg)

            if playing == False:
                break
    except:
        # some don't have midi files, and that's ok
        pass

def stop():
    global playing

    stop_drums()
    playing = False
    update_display()

def start():
    playThread = threading.Thread(target=play, daemon=True)
    playThread.start()

def togglePlay():
    if not playing:
        playThread = threading.Thread(target=play, daemon=True)
        playThread.start()
    else:
        stop()

def start_drums():
    # msg = mido.Message('start')
    msg = mido.Message('control_change',
                       channel=DRUM_MACHINE_CHANNEL,
                       control=SONG_PLAYBACK_CC,
                       value=SONG_PLAYBACK_START
                       )
    midi.output_port.send(msg)

def stop_drums():
    # msg = mido.Message('stop')
    msg = mido.Message('control_change',
                       channel=DRUM_MACHINE_CHANNEL,
                       control=SONG_PLAYBACK_CC,
                       value=SONG_PLAYBACK_START
                       )
    midi.output_port.send(msg)

def is_start(msg):
    # old
    # return msg.type == 'start'

    # lofi-xt 12 style
    return msg.type == 'control_change' and msg.channel == DRUM_MACHINE_CHANNEL and msg.control == SONG_PLAYBACK_CC and msg.value == SONG_PLAYBACK_START

def is_stop(msg):
    # old
    # return msg.type == 'stop'

    # lofi-xt 12 style
    return msg.type == 'control_change' and msg.channel == DRUM_MACHINE_CHANNEL and msg.control == SONG_PLAYBACK_CC and msg.value == SONG_PLAYBACK_STOP


# listens for midi input
def input():
    for msg in midi.input_port:
        if msg.type == 'program_change' and msg.channel == MIDI_IN_CHANNEL:
            select(msg.program)

        elif is_start(msg):
            start()

        elif is_stop(msg):
            stop()

        else:
            # pass the message on through
            midi.output_port.send(msg)

# manual overrides
# i put this in its own thread because it GPIO.add_event_detect was acting funny with long load times
def buttons():
    while True:
        if (GPIO.input(NEXT_PIN) == False):
            next()

        if (GPIO.input(PREV_PIN) == False):
            previous()

        if (GPIO.input(PLAY_PIN) == False):
            togglePlay()

        time.sleep(0.2)


# main init
select(0)

# TODO wrap in try/catch and show ERR message?
inputThread = threading.Thread(target=input, daemon=True)
buttonThread = threading.Thread(target=buttons, daemon=True)

inputThread.start()
buttonThread.start()

inputThread.join()
buttonThread.join()
