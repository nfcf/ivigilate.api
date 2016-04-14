#!/usr/bin/env python
#
# This script will monitor the pwr_sw GPIO and if a falling edge is
# detected then a shutdown is immediately  initiated.

# Required for GPIO access. Make sure we have root superuser privileges
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

import time
import os # Required for executing an OS command

# GPIO definition (this is the one we check)
pwr_sw = 26

# Setup
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(pwr_sw, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin to input with a pull-up enabled


# Check
while True:
	try:
		GPIO.wait_for_edge(pwr_sw, GPIO.FALLING) # Block execution until a falling edge is detected
		time.sleep(5); # Lets avoid false triggering, button must be pressed for more than 5 seconds.
		if not GPIO.input(pwr_sw):
			GPIO.cleanup() # Maybe unecessary,since we are going to shutdown anyway...
			os.system("sudo shutdown -h now") 	# Initiate shutdown
			
		time.sleep(0.2) # Little debounce for the re-triggering
	except:
		pass
