import time
from mss import mss
import pyautogui

# Test pixel coordinates (adjust if needed)
x, y = 100, 100
iterations = 5000  # Number of times each function will run

# MSS Method


def get_pixel_mss(x, y):
    monitor = {"top": y, "left": x, "width": 1, "height": 1}
    start = time.time()
    with mss() as sct:
        for _ in range(iterations):
            img = sct.grab(monitor)
            pixel = img.pixel(0, 0)
    elapsed = time.time() - start
    print(f"MSS: {iterations / elapsed:.2f} pixels per second")



# PyAutoGUI Method
def get_pixel_pyautogui(x, y):
    start = time.time()
    for _ in range(iterations):
        pyautogui.pixel(x, y)
    elapsed = time.time() - start
    print(f"PyAutoGUI: {iterations / elapsed:.2f} pixels per second")




# Run benchmarks
print("Running benchmarks...")
x, y = 100, 100 
get_pixel_mss(x, y)
get_pixel_pyautogui(x, y)
