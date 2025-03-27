import tkinter as tk
from mss import mss
import pydirectinput
import time
import threading
import pygame
from pynput import keyboard
from PIL import ImageGrab
import pyautogui
#this is for the atm rfid disruptor minigame

# Initialize pygame for sound
pygame.mixer.init()

# Sound files (you can replace these with any .mp3 files)
click_sound = pygame.mixer.Sound("click_sound.mp3")  # Replace with your click sound file
toggle_sound = pygame.mixer.Sound("toggle_sound.mp3")  # Replace with your toggle sound file


class AutoClicker:
    def __init__(self, master):
        self.master = master
        master.title("Color Change Clicker")

        # Internal state
        self.monitoring = False
        self.sample_coord = None
        self.reference_color = None
        self.monitor_thread = None

        # Create GUI elements
        self.info_label = tk.Label(master, text="Press ']' to start monitoring.")
        self.info_label.pack(pady=5)

        self.status_label = tk.Label(master, text="Status: Idle")
        self.status_label.pack(pady=5)

    def start_monitoring(self):
        self.monitoring = True
        self.status_label.config(text="Status: Monitoring...")
        self.info_label.config(text="Monitoring color changes... Press ']' to stop.")
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.monitor_thread.start()
        toggle_sound.play()

    def stop_monitoring(self):
        self.monitoring = False
        self.status_label.config(text="Status: Idle")
        self.info_label.config(text="Press ']' to start monitoring again.")
        toggle_sound.play()

    def monitor(self):
        x, y = self.sample_coord

        monitor = {"top": y, "left": x, "width": 1, "height": 1}
        bbox = (x, y, x + 1, y + 1)  # Single pixel bounding box

        # num_loops = 0
        # start_time = time.time()

        with mss() as sct:
            while self.monitoring:
                # num_loops += 1

                # Capture a 1x1 pixel area around the sample coordinate
                
                ## imagegrab (SLOWWWW)
                # screenshot = ImageGrab.grab(bbox)
                # current_color = screenshot.getpixel((0, 0))  # Get the color of that single pixel

                # mss
                current_color = sct.grab(monitor).pixel(0, 0)

                # Check if the current color differs from the reference color
                if any(abs(c - r) > 20 for c, r in zip(current_color, self.reference_color)):
                    pydirectinput.click()  #(clicks where the mouse is)
                    click_sound.play()  
                    self.stop_monitoring()  # Stop monitoring after one click
                    break

                # time.sleep(0.01)  # Small delay to avoid busy waiting
                # elapsed_time = time.time() - start_time  # Calculate elapsed time
                # if elapsed_time >= 1:  # Every second, log loops per second
                #     lps = num_loops / elapsed_time
                #     print(f"Loops per second: {lps:.2f}")
                    
                #     # Reset for the next interval
                #     num_loops = 0
                #     start_time = time.time()

    def set_reference_color(self):
        # Get the current position of the mouse (sample the color under the mouse)
        self.sample_coord = pydirectinput.position()
        # Capture the color at that position to use as the reference color
        x, y = self.sample_coord
        bbox = (x, y, x + 1, y + 1)
        screenshot = ImageGrab.grab(bbox)
        self.reference_color = screenshot.getpixel((0, 0))  # Set the reference color
        self.start_monitoring()  # Start monitoring after setting the reference color

# Function to listen for the ']' key
def on_press(key):
    try:
        if key.char == ']':
            if not app.monitoring:  # Only set the reference color if not already monitoring
                app.set_reference_color()  # Set the reference color and start monitoring
            else:
                app.stop_monitoring()  # Stop monitoring if already active
    except AttributeError:
        pass

# Set up listener for hotkey
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Run the GUI
root = tk.Tk()
app = AutoClicker(root)
root.mainloop()