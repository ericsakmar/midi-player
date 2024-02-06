import os
from time import sleep
from Adafruit_LED_Backpack import AlphaNum4
import RPi.GPIO as GPIO

# i used to start this in /etc/rc.local

display = AlphaNum4.AlphaNum4()

UP_PIN = 17
DOWN_PIN = 23
BANK_ONE_PIN = 18
BANK_TWO_PIN = 27
BANK_THREE_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(UP_PIN, GPIO.IN)
GPIO.setup(DOWN_PIN, GPIO.IN)
GPIO.setup(BANK_ONE_PIN, GPIO.IN)
GPIO.setup(BANK_TWO_PIN, GPIO.IN)
GPIO.setup(BANK_THREE_PIN, GPIO.IN)

banks = os.listdir('/home/pi/sounds/')
bank = 0

display.begin()

def show(message):
    display.clear()
    display.print_str(message)
    display.write_display()

def play(slot):
    sounds = os.listdir("/home/pi/sounds/%s/"%(banks[bank]))
    sounds.sort()
    os.system("mpg123 -q /home/pi/sounds/%s/%s &"%(banks[bank], sounds[slot]))

show(banks[bank])

while True:
    if (GPIO.input(UP_PIN) == False):
        bank += 1
        if bank >= len(banks):
            bank = 0
        show(banks[bank])

    if (GPIO.input(DOWN_PIN) == False):
        bank -= 1
        if bank < 0:
            bank = len(banks) - 1
        show(banks[bank])

    if (GPIO.input(BANK_ONE_PIN) == False):
        play(0)

    if (GPIO.input(BANK_TWO_PIN) == False):
        play(1)

    if (GPIO.input(BANK_THREE_PIN) == False):
        play(2)

    sleep(0.2)
