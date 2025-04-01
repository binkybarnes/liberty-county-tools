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


# constants for bar monitor
TARGET_COLOR_BAR = np.array((164, 165, 162))
COLOR_TOLERANCE_BAR = 30
OFFSET = 2

if getattr(sys, "frozen", False):
    # If running as a packaged app
    base_path = sys._MEIPASS
else:
    # If running as a regular script
    base_path = os.path.dirname(__file__)


class LibertySuite:
    def __init__(self, master):
        # Sound files
        self.toggle_sound = os.path.join(base_path, "sounds/toggle_sound.mp3")
        self.coordinate_set_sound = os.path.join(
            base_path, "sounds/coordinate_set_sound.mp3"
        )
        self.click_sound = os.path.join(base_path, "sounds/click_sound.mp3")

        # Main window setup
        self.master = master
        master.title("Liberty County Tools")
        master.geometry("400x120")  # Increased width
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
            text="Vertical Bar Clicker",
            style="Red.TButton",
            command=self.toggle_bar_monitoring,
            width=20,
        )
        self.bar_button.pack(side=tk.LEFT, padx=(0, 10))

        self.set_bar_coordinate_button = ttk.Button(
            self.bar_frame,
            text="Set Coordinate: [",
            style="Red.TButton",
            command=self.toggle_bar_coordinate,
            width=15,
        )
        self.set_bar_coordinate_button.pack(side=tk.LEFT, padx=(0, 10))

        self.bar_status = ttk.Label(self.bar_frame, text="Idle")
        self.bar_status.pack(side=tk.LEFT)

        # Color Change Clicker Section
        self.color_frame = ttk.Frame(main_frame, style="TFrame")
        self.color_frame.pack(fill=tk.X, pady=10)

        self.color_button = ttk.Button(
            self.color_frame,
            text="Color Change Clicker",
            style="Red.TButton",
            command=self.toggle_color_monitoring,
            width=20,
        )
        self.color_button.pack(side=tk.LEFT, padx=(0, 10))

        self.set_color_coordinate_button = ttk.Button(
            self.color_frame,
            text="Set Coordinate: ]",
            style="Red.TButton",
            command=self.toggle_color_coordinate,
            width=15,
        )
        self.set_color_coordinate_button.pack(side=tk.LEFT, padx=(0, 10))

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

        self.bar_monitor_dict = None
        self.color_monitor_dict = None

        # Create mouse controller using pynput.mouse
        self.mouse = Controller()

        # Start keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    # Bar Clicker ┏━•❃°•°❀°•°❃•━┓
    def toggle_bar_coordinate(self):
        if self.bar_monitor_dict:
            self.reset_bar_coordinate()
        else:
            self.set_bar_coordinate()

    def set_bar_coordinate(self):
        self.bar_center_coord = self.mouse.position
        x, y = self.bar_center_coord
        self.bar_monitor_dict = {
            "top": y + OFFSET,
            "left": x,
            "width": 1,
            "height": 2 * OFFSET + 1,
        }
        self.set_bar_coordinate_button.configure(style="Green.TButton")
        self.color_status.configure(text="Monitoring")
        sound_thread(self.coordinate_set_sound)

    def reset_bar_coordinate(self):
        self.set_bar_coordinate_button.configure(style="Red.TButton")
        self.bar_monitor_dict = None

    def toggle_bar_monitoring(self):
        if not self.bar_monitoring:
            self.bar_start_monitoring()
        else:
            self.bar_stop_monitoring()

    def bar_start_monitoring(self):
        self.bar_monitoring = True
        self.bar_button.configure(style="Green.TButton")
        self.bar_status.configure(text="waiting4coord")
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
            cooldown_time -= 1
        self.bar_status.configure(text="Ready")
        self.bar_cooldown_active = False

    def bar_monitor(self):
        with mss() as sct:
            while self.bar_monitoring:
                if not self.bar_monitor_dict:
                    time.sleep(0.001)
                    continue

                img = sct.grab(self.bar_monitor_dict)
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

                    self.reset_bar_coordinate()

    # Bar Clicker ┗━•❃°•°❀°•°❃•━┛

    # Color Clicker ┏━•❃°•°❀°•°❃•━┓
    def toggle_color_coordinate(self):
        if self.color_monitor_dict:
            self.reset_color_coordinate()
        else:
            self.set_color_coordinate()

    def set_color_coordinate(self):
        # Set reference color
        self.color_sample_coord = self.mouse.position
        x, y = self.color_sample_coord
        with mss() as sct:
            monitor = {"top": y, "left": x, "width": 1, "height": 1}
            self.color_reference_color = sct.grab(monitor).pixel(0, 0)

        self.color_monitor_dict = {"top": y, "left": x, "width": 1, "height": 1}
        self.set_color_coordinate_button.configure(style="Green.TButton")
        self.color_status.configure(text="Monitoring")
        sound_thread(self.coordinate_set_sound)

    def reset_color_coordinate(self):
        self.set_color_coordinate_button.configure(style="Red.TButton")
        self.color_reference_color = None
        self.color_monitor_dict = None

    def toggle_color_monitoring(self):
        if not self.color_monitoring:
            self.color_start_monitoring()
        else:
            self.color_stop_monitoring()

    def color_start_monitoring(self):
        self.color_monitoring = True
        self.color_button.configure(style="Green.TButton")
        self.color_status.configure(text="waiting4coord")
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
        with mss() as sct:
            while self.color_monitoring:
                # color reference color is set on set_coordinate
                if not self.color_monitor_dict:
                    time.sleep(0.001)
                    continue
                current_color = sct.grab(self.color_monitor_dict).pixel(0, 0)
                # reset_color_coordinate() can get rid of these while the loop is running
                # i need a if statement after sct grab because its the slowest statement
                # and it makes it so the reset variables get reset when sct grab is running
                if not self.color_reference_color:
                    time.sleep(0.001)
                    continue
                if any(
                    abs(c - r) > 20
                    for c, r in zip(current_color, self.color_reference_color)
                ):
                    self.mouse.click(Button.left, 1)
                    sound_thread(self.click_sound)

                    self.reset_color_coordinate()  # sets color reference color and monitor dict to none

    # Color Clicker ┗━•❃°•°❀°•°❃•━┛

    def on_press(self, key):
        try:
            # Vertical Bar Clicker (hotkey '[')
            if key.char == "[":
                self.toggle_bar_coordinate()
            # Color Change Clicker (hotkey ']')
            elif key.char == "]":
                self.toggle_color_coordinate()
        except AttributeError:
            pass


# Run the GUI
root = tk.Tk()
app = LibertySuite(root)


icon_path = os.path.join(base_path, "kuromi.png")

icon_image = PhotoImage(file=icon_path)
root.iconphoto(True, icon_image)

root.mainloop()
