import os
import threading
import RPi.GPIO as GPIO
import glob
import time
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

MIDI_IN_CHANNEL = 9 # it's actually 10

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

    display.print('load')
    playing = False
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

    for msg in selected_midi.play():
        midi.output_port.send(msg)

        if playing == False:
            break

    playing = False
    update_display()

def stop():
    global playing
    playing = False
    update_display()

def start():
    global playing

    if not selected_midi:
        return

    playing = True
    update_display()

    playThread = threading.Thread(target=play, daemon=True)
    playThread.start()

def togglePlay():
    global playing

    if not selected_midi:
        return

    playing = not playing
    update_display()

    if playing:
        playThread = threading.Thread(target=play, daemon=True)
        playThread.start()


# listens for midi input
def input():
    for msg in midi.input_port:
        if msg.type == 'program_change' and msg.channel == MIDI_IN_CHANNEL:
            select(msg.program)

        if msg.type == 'start':
            start()

        if msg.type == 'stop':
            stop()


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
