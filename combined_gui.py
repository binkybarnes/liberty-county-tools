import tkinter as tk
from tkinter import ttk
import threading
import pygame
from pynput import keyboard
from mss import mss
import pydirectinput
from PIL import ImageGrab
import numpy as np

class LibertySuite:
    def __init__(self, master):
        # Initialize pygame for sound
        pygame.mixer.init()

        # Sound files
        self.click_sound = pygame.mixer.Sound("click_sound.mp3")
        self.toggle_sound = pygame.mixer.Sound("toggle_sound.mp3")

        # Main window setup
        self.master = master
        master.title("Liberty County Tools")
        master.geometry("270x150")  # Increased width
        master.configure(bg="#2c3e50")

        # Custom font
        custom_font = ("Segoe UI", 10)
        custom_font_bold = ("Segoe UI", 10, "bold")

        # Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles with new font
        self.style.configure('TLabel', 
            background="#2c3e50", 
            foreground="white", 
            font=custom_font
        )
        self.style.configure('TFrame', 
            background="#2c3e50"
        )
        
        # Button styles with new font and colors
        self.style.configure('Green.TButton', 
            background='#2ecc71', 
            foreground='white', 
            font=custom_font_bold
        )
        self.style.configure('Red.TButton', 
            background='#e74c3c', 
            foreground='white', 
            font=custom_font_bold
        )
        self.style.map('Green.TButton', 
            background=[('active', '#27ae60')]
        )
        self.style.map('Red.TButton', 
            background=[('active', '#c0392b')]
        )

        # Frame for overall layout
        main_frame = ttk.Frame(master, style='TFrame')
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Vertical Bar Clicker Section
        self.bar_frame = ttk.Frame(main_frame, style='TFrame')
        self.bar_frame.pack(fill=tk.X, pady=10)

        self.bar_button = ttk.Button(
            self.bar_frame, 
            text="Vertical Bar Clicker", 
            style='Red.TButton', 
            command=self.toggle_bar_monitoring,
            width=25
        )
        self.bar_button.pack(side=tk.LEFT, padx=(0,10))

        self.bar_status = ttk.Label(self.bar_frame, text="Idle")
        self.bar_status.pack(side=tk.LEFT)

        # Color Change Clicker Section
        self.color_frame = ttk.Frame(main_frame, style='TFrame')
        self.color_frame.pack(fill=tk.X, pady=10)

        self.color_button = ttk.Button(
            self.color_frame, 
            text="Color Change Clicker", 
            style='Red.TButton', 
            command=self.toggle_color_monitoring,
            width=25
        )
        self.color_button.pack(side=tk.LEFT, padx=(0,10))

        self.color_status = ttk.Label(self.color_frame, text="Idle")
        self.color_status.pack(side=tk.LEFT)

        # Internal state for both clickers
        self.bar_monitoring = False
        self.bar_center_coord = None
        self.color_monitoring = False
        self.color_sample_coord = None
        self.color_reference_color = None

        # Start keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def toggle_bar_monitoring(self):
        if not self.bar_monitoring:
            # Start monitoring
            self.bar_center_coord = pydirectinput.position()
            self.bar_start_monitoring()
        else:
            # Stop monitoring
            self.bar_stop_monitoring()

    def bar_start_monitoring(self):
        self.bar_monitoring = True
        self.bar_button.configure(style='Green.TButton')
        self.bar_status.configure(text="Monitoring")
        threading.Thread(target=self.bar_monitor, daemon=True).start()
        self.toggle_sound.play()

    def bar_stop_monitoring(self):
        self.bar_monitoring = False
        self.bar_button.configure(style='Red.TButton')
        self.bar_status.configure(text="Idle")
        self.toggle_sound.play()

    def bar_monitor(self):
        TARGET_COLOR = np.array((164, 165, 162))
        COLOR_TOLERANCE = 30
        OFFSET = 2

        x, y = self.bar_center_coord
        monitor = {"top": y + OFFSET, "left": x, "width": 1, "height": 2 * OFFSET + 1}
        
        with mss() as sct:
            while self.bar_monitoring:
                img = sct.grab(monitor)
                upper_color = img.pixel(0, 0)
                lower_color = img.pixel(0, 2 * OFFSET)
                
                if (np.all(np.abs(upper_color - TARGET_COLOR) <= COLOR_TOLERANCE) and 
                    np.all(np.abs(lower_color - TARGET_COLOR) <= COLOR_TOLERANCE) and 
                    np.all(lower_color == upper_color)):
                    pydirectinput.click()
                    self.click_sound.play()
                    self.bar_stop_monitoring()
                    break

    def toggle_color_monitoring(self):
        if not self.color_monitoring:
            # Set reference color
            self.color_sample_coord = pydirectinput.position()
            x, y = self.color_sample_coord
            bbox = (x, y, x + 1, y + 1)
            screenshot = ImageGrab.grab(bbox)
            self.color_reference_color = screenshot.getpixel((0, 0))
            self.color_start_monitoring()
        else:
            self.color_stop_monitoring()

    def color_start_monitoring(self):
        self.color_monitoring = True
        self.color_button.configure(style='Green.TButton')
        self.color_status.configure(text="Monitoring")
        threading.Thread(target=self.color_monitor, daemon=True).start()
        self.toggle_sound.play()

    def color_stop_monitoring(self):
        self.color_monitoring = False
        self.color_button.configure(style='Red.TButton')
        self.color_status.configure(text="Idle")
        self.toggle_sound.play()

    def color_monitor(self):
        x, y = self.color_sample_coord
        monitor = {"top": y, "left": x, "width": 1, "height": 1}
        
        with mss() as sct:
            while self.color_monitoring:
                current_color = sct.grab(monitor).pixel(0, 0)
                
                if any(abs(c - r) > 20 for c, r in zip(current_color, self.color_reference_color)):
                    pydirectinput.click()
                    self.click_sound.play()
                    self.color_stop_monitoring()
                    break

    def on_press(self, key):
        try:
            # Vertical Bar Clicker (hotkey '[')
            if key.char == '[':
                self.toggle_bar_monitoring()

            # Color Change Clicker (hotkey ']')
            elif key.char == ']':
                self.toggle_color_monitoring()
        except AttributeError:
            pass

# Run the GUI
root = tk.Tk()
app = LibertySuite(root)
root.mainloop()