#!/usr/bin/env python

# External module imports, making sure we have root superuser privileges
import time
import RPi.GPIO as GPIO  # Required for GPIO access. Make sure we have root superuser privileges!

# Definitions (user changeable)
buzzerPin = 17  # Broadcom pin 17 (P1 pin 11)
freq_l = 600  # tone low frequency
freq_h = 800  # tone high frequency

# Definitions
dc = 50  # duty cycle (0-100) for PWM pin
buzzer = None


def init():
    global buzzer

    GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
    GPIO.setup(buzzerPin, GPIO.OUT)  # Buzzer pin set as output
    buzzer = GPIO.PWM(buzzerPin, freq_l)  # Initialize PWM on lower frequency tone


# If no argument is passed to this function then it will play for 30 seconds
def play(duration=30):
    try:
        buzzer.start(dc)
    except AttributeError:
        print("Error: Buzzer not previously initialized! You must call init() before play().")
        return

    loops = duration // 0.5  # integer division

    while loops > 0:
        buzzer.ChangeFrequency(freq_l)
        time.sleep(0.2)
        buzzer.ChangeFrequency(freq_h)
        time.sleep(0.2)

        loops -= 1

    # Cleanup
    buzzer.stop()  # stop PWM
    GPIO.cleanup()  # cleanup all used GPIOs
