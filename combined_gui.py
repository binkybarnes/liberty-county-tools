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
OFFSET = 2

class LibertyCountyTools:
    def __init__(self, master):
        self.master = master
        master.title("Liberty County Tools")

        # Internal state for both tools
        self.monitoring_color_change = False
        self.monitoring_vertical_bar = False
        self.sample_coord = None
        self.reference_color = None
        self.center_coord = None

        # Create GUI elements with styling
        self.master.config(bg="#f0f0f0")

        self.info_label = tk.Label(master, text="Liberty County Tools", font=("Arial", 16, "bold"), bg="#f0f0f0")
        self.info_label.pack(pady=10)

        self.color_change_frame = tk.Frame(master, bg="#f0f0f0")
        self.color_change_frame.pack(pady=5, fill="x")

        self.color_change_button = tk.Button(self.color_change_frame, text="Start Color Change Monitoring", command=self.toggle_color_change_monitoring, width=25, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.color_change_button.pack(pady=5)

        self.status_label_color_change = tk.Label(self.color_change_frame, text="Status: Idle", bg="#f0f0f0")
        self.status_label_color_change.pack(pady=5)

        self.vertical_bar_frame = tk.Frame(master, bg="#f0f0f0")
        self.vertical_bar_frame.pack(pady=5, fill="x")

        self.vertical_bar_button = tk.Button(self.vertical_bar_frame, text="Start Vertical Bar Monitoring", command=self.toggle_vertical_bar_monitoring, width=25, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.vertical_bar_button.pack(pady=5)

        self.status_label_vertical_bar = tk.Label(self.vertical_bar_frame, text="Status: Idle", bg="#f0f0f0")
        self.status_label_vertical_bar.pack(pady=5)

    def toggle_color_change_monitoring(self):
        if not self.monitoring_color_change:
            self.set_reference_color()
            self.monitoring_color_change = True
            self.status_label_color_change.config(text="Status: Monitoring...")
            self.color_change_button.config(text="Stop Monitoring", bg="#f44336")
            toggle_sound.play()
        else:
            self.monitoring_color_change = False
            self.status_label_color_change.config(text="Status: Idle")
            self.color_change_button.config(text="Start Color Change Monitoring", bg="#4CAF50")
            toggle_sound.play()

    def toggle_vertical_bar_monitoring(self):
        if not self.monitoring_vertical_bar:
            self.set_center_and_toggle()
            self.monitoring_vertical_bar = True
            self.status_label_vertical_bar.config(text="Status: Monitoring...")
            self.vertical_bar_button.config(text="Stop Monitoring", bg="#f44336")
            toggle_sound.play()
        else:
            self.monitoring_vertical_bar = False
            self.status_label_vertical_bar.config(text="Status: Idle")
            self.vertical_bar_button.config(text="Start Vertical Bar Monitoring", bg="#4CAF50")
            toggle_sound.play()

    def monitor_color_change(self):
        x, y = self.sample_coord
        monitor = {"top": y, "left": x, "width": 1, "height": 1}
        bbox = (x, y, x + 1, y + 1)

        with mss() as sct:
            while self.monitoring_color_change:
                current_color = sct.grab(monitor).pixel(0, 0)
                print(current_color)
                if any(abs(c - r) > 20 for c, r in zip(current_color, self.reference_color)):
                    pydirectinput.click()
                    click_sound.play()
                    self.stop_color_change_monitoring()
                    break

    def monitor_vertical_bar(self):
        x, y = self.center_coord
        upper_coord = (x, y - OFFSET)
        lower_coord = (x, y + OFFSET)

        monitor = {"top": y + OFFSET, "left": x, "width": 1, "height": 2 * OFFSET + 1}
        with mss() as sct:
            while self.monitoring_vertical_bar:
                img = sct.grab(monitor)
                upper_color = img.pixel(0, 0)
                lower_color = img.pixel(0, 2 * OFFSET)
                if np.all(np.abs(upper_color - TARGET_COLOR) <= COLOR_TOLERANCE) and \
                np.all(np.abs(lower_color - TARGET_COLOR) <= COLOR_TOLERANCE) and \
                np.all(lower_color == upper_color):
                    pydirectinput.click()
                    click_sound.play()
                    self.stop_vertical_bar_monitoring()
                    break

    def stop_color_change_monitoring(self):
        self.monitoring_color_change = False
        self.status_label_color_change.config(text="Status: Idle")
        self.color_change_button.config(text="Start Color Change Monitoring", bg="#4CAF50")
        
    def stop_vertical_bar_monitoring(self):
        self.monitoring_vertical_bar = False
        self.status_label_vertical_bar.config(text="Status: Idle")
        self.vertical_bar_button.config(text="Start Vertical Bar Monitoring", bg="#4CAF50")

    def set_reference_color(self):
        self.sample_coord = pydirectinput.position()
        x, y = self.sample_coord
        bbox = (x, y, x + 1, y + 1)
        screenshot = ImageGrab.grab(bbox)
        self.reference_color = screenshot.getpixel((0, 0))
        self.monitor_color_change()

    def set_center_and_toggle(self):
        if not self.monitoring_vertical_bar:
            self.center_coord = pydirectinput.position()
            self.monitor_vertical_bar()
        else:
            self.stop_vertical_bar_monitoring()

# Function to listen for hotkeys
def on_press(key):
    try:
        if key.char == ']':
            if not app.monitoring_color_change:
                app.toggle_color_change_monitoring()
            else:
                app.stop_color_change_monitoring()
        elif key.char == '[':
            if not app.monitoring_vertical_bar:
                app.toggle_vertical_bar_monitoring()
            else:
                app.stop_vertical_bar_monitoring()
    except AttributeError:
        pass

# Set up the listener for the hotkey
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Run the GUI
root = tk.Tk()
app = LibertyCountyTools(root)
root.mainloop()
