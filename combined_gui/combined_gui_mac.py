import os
import sys
import tkinter as tk
from tkinter import PhotoImage, ttk
import threading
import time
from pynput import keyboard
from pynput.mouse import Controller, Button
from mss import mss
import numpy as np
from playsound import playsound  # Import playsound


def sound_thread(sound_path):
    threading.Thread(target=playsound, args=(sound_path,), daemon=True).start()


if getattr(sys, "frozen", False):
    # If running as a packaged app
    base_path = sys._MEIPASS
else:
    # If running as a regular script
    base_path = os.path.dirname(__file__)


class LibertySuite:
    def __init__(self, master):
        # Sound files
        self.click_sound = os.path.join(
            base_path, "sounds/click_sound.mp3"
        )  # File path for click sound
        self.toggle_sound = os.path.join(
            base_path, "sounds/toggle_sound.mp3"
        )  # File path for toggle sound

        # Main window setup
        self.master = master
        master.title("Liberty County Tools")
        master.geometry("320x130")  # Increased width
        master.configure(bg="#2c3e50")

        # Custom font
        custom_font = ("Segoe UI", 10)
        custom_font_bold = ("Segoe UI", 10, "bold")

        # Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure styles with new font
        self.style.configure(
            "TLabel", background="#2c3e50", foreground="white", font=custom_font
        )
        self.style.configure("TFrame", background="#2c3e50")

        # Button styles with new font and colors
        self.style.configure(
            "Green.TButton",
            background="#2ecc71",
            foreground="white",
            font=custom_font_bold,
        )
        self.style.configure(
            "Red.TButton",
            background="#e74c3c",
            foreground="white",
            font=custom_font_bold,
        )
        self.style.map("Green.TButton", background=[("active", "#27ae60")])
        self.style.map("Red.TButton", background=[("active", "#c0392b")])

        # Frame for overall layout
        main_frame = ttk.Frame(master, style="TFrame")
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Vertical Bar Clicker Section
        self.bar_frame = ttk.Frame(main_frame, style="TFrame")
        self.bar_frame.pack(fill=tk.X, pady=10)

        self.bar_button = ttk.Button(
            self.bar_frame,
            text="Vertical Bar Clicker: [",
            style="Red.TButton",
            command=self.toggle_bar_monitoring,
            width=25,
        )
        self.bar_button.pack(side=tk.LEFT, padx=(0, 10))

        self.bar_status = ttk.Label(self.bar_frame, text="Idle")
        self.bar_status.pack(side=tk.LEFT)

        # Color Change Clicker Section
        self.color_frame = ttk.Frame(main_frame, style="TFrame")
        self.color_frame.pack(fill=tk.X, pady=10)

        self.color_button = ttk.Button(
            self.color_frame,
            text="Color Change Clicker: ]",
            style="Red.TButton",
            command=self.toggle_color_monitoring,
            width=25,
        )
        self.color_button.pack(side=tk.LEFT, padx=(0, 10))

        self.color_status = ttk.Label(self.color_frame, text="Idle")
        self.color_status.pack(side=tk.LEFT)

        # Internal state for both clickers
        self.bar_monitoring = False
        self.bar_center_coord = None
        self.color_monitoring = False
        self.color_sample_coord = None
        self.color_reference_color = None

        self.bar_cooldown_active = False
        self.color_cooldown_active = False

        # Create mouse controller using pynput.mouse
        self.mouse = Controller()

        # Start keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def toggle_bar_monitoring(self):
        if not self.bar_monitoring:
            # Start monitoring
            self.bar_center_coord = self.mouse.position
            self.bar_start_monitoring()
        else:
            # Stop monitoring
            self.bar_stop_monitoring()

    def bar_start_monitoring(self):
        self.bar_monitoring = True
        self.bar_button.configure(style="Green.TButton")
        self.bar_status.configure(text="Monitoring")
        threading.Thread(target=self.bar_monitor, daemon=True).start()
        sound_thread(self.toggle_sound)  # Play the toggle sound using playsound

    def bar_stop_monitoring(self):
        self.bar_monitoring = False
        self.bar_button.configure(style="Red.TButton")
        self.bar_status.configure(text="Idle")
        sound_thread(self.toggle_sound)  # Play the toggle sound using playsound
        if not self.bar_cooldown_active:
            self.start_bar_cooldown()

    def start_bar_cooldown(self):
        self.bar_cooldown_active = True
        threading.Thread(target=self.bar_cooldown_timer, daemon=True).start()

    def bar_cooldown_timer(self):
        cooldown_time = 300  # 5 minutes
        while cooldown_time > 0:
            mins, secs = divmod(cooldown_time, 60)
            self.bar_status.configure(text=f"Cooldown: {mins}:{secs:02d}")
            time.sleep(1)
            cooldown_time -= 1
        self.bar_status.configure(text="Ready")
        self.bar_cooldown_active = False

    def bar_monitor(self):
        TARGET_COLOR_BAR = np.array((164, 165, 162))
        COLOR_TOLERANCE_BAR = 30
        OFFSET = 2

        x, y = self.bar_center_coord
        monitor = {"top": y + OFFSET, "left": x, "width": 1, "height": 2 * OFFSET + 1}

        with mss() as sct:
            while self.bar_monitoring:
                img = sct.grab(monitor)
                upper_color = img.pixel(0, 0)
                lower_color = img.pixel(0, 2 * OFFSET)

                if (
                    np.all(
                        np.abs(upper_color - TARGET_COLOR_BAR) <= COLOR_TOLERANCE_BAR
                    )
                    and np.all(
                        np.abs(lower_color - TARGET_COLOR_BAR) <= COLOR_TOLERANCE_BAR
                    )
                    and np.all(lower_color == upper_color)
                ):
                    self.mouse.click(Button.left, 1)
                    sound_thread(
                        self.click_sound
                    )  # Play the click sound using playsound
                    self.bar_stop_monitoring()
                    break

    def toggle_color_monitoring(self):

        if not self.color_monitoring:
            # Set reference color
            self.color_sample_coord = self.mouse.position
            x, y = self.color_sample_coord
            monitor = {"top": y, "left": x, "width": 1, "height": 1}
            with mss() as sct:
                self.color_reference_color = sct.grab(monitor).pixel(0, 0)

            self.color_start_monitoring()
        else:
            self.color_stop_monitoring()

    def color_start_monitoring(self):
        self.color_monitoring = True
        self.color_button.configure(style="Green.TButton")
        self.color_status.configure(text="Monitoring")
        threading.Thread(target=self.color_monitor, daemon=True).start()
        sound_thread(self.toggle_sound)  # Play the toggle sound using playsound

    def color_stop_monitoring(self):
        self.color_monitoring = False
        self.color_button.configure(style="Red.TButton")
        self.color_status.configure(text="Idle")
        sound_thread(self.toggle_sound)  # Play the toggle sound using playsound
        if not self.color_cooldown_active:
            self.start_color_cooldown()

    def start_color_cooldown(self):
        self.color_cooldown_active = True
        threading.Thread(target=self.color_cooldown_timer, daemon=True).start()

    def color_cooldown_timer(self):
        cooldown_time = 420  # 7 minutes
        while cooldown_time > 0:
            mins, secs = divmod(cooldown_time, 60)
            self.color_status.configure(text=f"Cooldown: {mins}:{secs:02d}")
            time.sleep(1)
            cooldown_time -= 1
        self.color_status.configure(text="Ready")
        self.color_cooldown_active = False

    def color_monitor(self):
        from PIL import ImageGrab  # Imported here since it's only used in color_monitor

        x, y = self.color_sample_coord
        monitor = {"top": y, "left": x, "width": 1, "height": 1}

        with mss() as sct:
            while self.color_monitoring:
                current_color = sct.grab(monitor).pixel(0, 0)

                if any(
                    abs(c - r) > 20
                    for c, r in zip(current_color, self.color_reference_color)
                ):
                    self.mouse.click(Button.left, 1)
                    sound_thread(
                        self.click_sound
                    )  # Play the click sound using playsound
                    self.color_stop_monitoring()
                    break

    def on_press(self, key):
        try:
            # Vertical Bar Clicker (hotkey '[')
            if key.char == "[":
                self.toggle_bar_monitoring()
            # Color Change Clicker (hotkey ']')
            elif key.char == "]":
                self.toggle_color_monitoring()
        except AttributeError:
            pass


# Run the GUI
root = tk.Tk()
app = LibertySuite(root)


icon_path = os.path.join(base_path, "kuromi.png")

icon_image = PhotoImage(file=icon_path)
root.iconphoto(True, icon_image)

root.mainloop()
