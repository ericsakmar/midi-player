import os
import threading
import RPi.GPIO as GPIO
import mido
import glob
import time
from song import Song, Songs
from display import Display

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



# sets up midi
# TODO wrap in try/catch??
midi_ports = mido.get_output_names() # current usb2midi can use either
midi_in_name = [p for p in midi_ports if 'MIDI 1' in p][0]
midi_out_name = [p for p in midi_ports if 'MIDI 2' in p][0]
midi_output_port = mido.open_output(midi_out_name)
MIDI_IN_CHANNEL = 9 # it's actually 10

# globals
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
        midi_output_port.send(msg)

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


# listens for input
def input():
    with mido.open_input(midi_in_name) as port:
        while True:
            # midi messages
            for msg in port.iter_pending():
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


# GPIO.add_event_detect(NEXT_PIN, GPIO.FALLING, callback=next, bouncetime=200)
# GPIO.add_event_detect(PREV_PIN, GPIO.FALLING, callback=previous, bouncetime=200)
# GPIO.add_event_detect(PLAY_PIN, GPIO.FALLING, callback=togglePlay, bouncetime=200)

# main init
select(0)

# TODO wrap in try/catch and show ERR message?
inputThread = threading.Thread(target=input, daemon=True)
buttonThread = threading.Thread(target=buttons, daemon=True)

inputThread.start()
buttonThread.start()

inputThread.join()
buttonThread.join()
