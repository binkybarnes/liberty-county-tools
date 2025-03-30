import time
import pydirectinput

# Set how often you want to press "1" (in seconds)
interval = 3

while True:
    pydirectinput.press('1')  # Simulate pressing the "1" key
    time.sleep(interval)  # Wait for the next press
