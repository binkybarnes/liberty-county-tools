import tkinter as tk
from mss import mss
import numpy as np
import pydirectinput
import time
import threading
import pygame
from pynput import keyboard
from PIL import ImageGrab
import pyautogui

# Initialize pygame for sound
pygame.mixer.init()

# Sound files (replace these with your own .wav files)
click_sound = pygame.mixer.Sound("click_sound.mp3")  # Replace with your click sound file
toggle_sound = pygame.mixer.Sound("toggle_sound.mp3")  # Replace with your toggle sound file

# Target color for the bar
TARGET_COLOR = np.array((164, 165, 162))
COLOR_TOLERANCE = 30  # Allowed deviation for each channel
# 129,128,128,  165,164,165 color range of bar

# Vertical offset from the reference center (in pixels)
OFFSET = 2



class VerticalBarAutoClicker:
    def __init__(self, master):
        self.master = master
        master.title("Vertical Bar AutoClicker")
        
        # Internal state
        self.monitoring = False
        self.center_coord = None  # This will be the user-selected center of the horizontal line.
        self.monitor_thread = None
        
        # Create GUI elements
        self.info_label = tk.Label(master, text="Press '[' to capture the center coordinate and start monitoring.")
        self.info_label.pack(pady=5)
        
        self.status_label = tk.Label(master, text="Status: Idle")
        self.status_label.pack(pady=5)
    
    def start_monitoring(self):
        self.monitoring = True
        self.status_label.config(text="Status: Monitoring...")
        self.info_label.config(text="Monitoring vertical samples... Press '[' to cancel.")
        self.monitor_thread = threading.Thread(target=self.monitor, daemon=True)  # daemon thread so it doesn't block
        self.monitor_thread.start()
        toggle_sound.play()
    
    def stop_monitoring(self):
        self.monitoring = False
        self.status_label.config(text="Status: Idle")
        self.info_label.config(text="Press '[' to capture the center coordinate and start monitoring again.")
        toggle_sound.play()
    
    def monitor(self):
        # The two sample coordinates are fixed relative to the center coordinate.
        x, y = self.center_coord
        upper_coord = (x, y - OFFSET)
        lower_coord = (x, y + OFFSET)

        # num_loops = 0
        # start_time = time.time()

        bbox = (x, y - OFFSET, x + 1, y + OFFSET + 1)
        monitor = {"top": y + OFFSET, "left": x, "width": 1, "height": 2 * OFFSET + 1}
        with mss() as sct:
            while self.monitoring:
                # num_loops += 1
                
                # mss
                img = sct.grab(monitor)
                upper_color = img.pixel(0, 0)
                lower_color = img.pixel(0, 2 * OFFSET)
                
                # Compare both sample colors to the target color using numpy (fast array comparison)
                if np.all(np.abs(upper_color - TARGET_COLOR) <= COLOR_TOLERANCE) and \
                np.all(np.abs(lower_color - TARGET_COLOR) <= COLOR_TOLERANCE) and \
                np.all(lower_color == upper_color):
                    # When both pixels match the target color, click.
                    pydirectinput.click()
                    click_sound.play()
                    self.stop_monitoring()
                    break
                
                # No sleep; continuously check the pixels without delay
                # But we add a very short time to avoid 100% CPU usage
                # time.sleep(0.001)
                # elapsed_time = time.time() - start_time  # Calculate elapsed time
                # if elapsed_time >= 1:  # Every second, log loops per second
                #     lps = num_loops / elapsed_time
                #     print(f"Loops per second: {lps:.2f}")
                    
                #     # Reset for the next interval
                #     num_loops = 0
                #     start_time = time.time()


    def set_center_and_toggle(self):
        if not self.monitoring:
            # Capture current mouse position as center coordinate
            self.center_coord = pydirectinput.position()
            self.info_label.config(text=f"Center coordinate set at: {self.center_coord}. Starting monitoring...")
            self.start_monitoring()
        else:
            self.stop_monitoring()

# Function to listen for the '[' key press
def on_press(key):
    try:
        if key.char == '[':
            app.set_center_and_toggle()
    except AttributeError:
        pass

# Set up the listener for the hotkey
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Run the GUI
root = tk.Tk()
app = VerticalBarAutoClicker(root)
root.mainloop()