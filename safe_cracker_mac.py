import tkinter as tk
from tkinter import ttk
import threading
import time
from pynput.mouse import Controller, Button
import mss
from pynput import keyboard
from PIL import Image, ImageTk
import numpy as np
import tempfile
import subprocess


# Constants
TARGET_COLOR = (178, 178, 178)
TOLERANCE = 5
TICK_COORD = (957, 396)

RED = "#c0392b"
GREEN = "#27ae60"


class SafeCracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Safe Cracker")

        # Use ttk with theme clam
        self.style = ttk.Style()
        self.style.theme_use("clam")
        # Configure button styles
        self.style.configure(
            "Red.TButton",
            foreground="white",
            background=RED,
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map("Red.TButton", background=[("active", RED)])
        self.style.configure(
            "Green.TButton",
            foreground="white",
            background=GREEN,
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map("Green.TButton", background=[("active", GREEN)])
        # Configure label style
        self.style.configure(
            "TLabel", background="#2c3e50", foreground="white", font=("Segoe UI", 10)
        )

        # Main frame configuration
        self.root.configure(bg="#2c3e50")
        main_frame = ttk.Frame(root, style="TFrame")
        main_frame.grid(padx=10, pady=10, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Starting Tick Entry and Label
        ttk.Label(main_frame, text="Starting Tick:").grid(row=0, column=0, sticky="w")
        self.start_var = tk.IntVar()
        self.start_entry = ttk.Entry(main_frame, textvariable=self.start_var)
        self.start_entry.grid(row=0, column=1, sticky="ew")
        self.start_entry.bind("<Return>", self.confirm_start)
        self.confirm_start_button = ttk.Button(
            main_frame,
            text="Confirm Start",
            command=self.confirm_start,
            style="Red.TButton",
        )
        self.confirm_start_button.grid(row=0, column=2, padx=5)

        # Target Number Entry and Label
        ttk.Label(main_frame, text="Target Number:").grid(row=1, column=0, sticky="w")
        self.target_var = tk.IntVar()
        self.target_entry = ttk.Entry(main_frame, textvariable=self.target_var)
        self.target_entry.grid(row=1, column=1, sticky="ew")
        self.target_entry.bind("<Return>", self.confirm_target)
        self.confirm_target_button = ttk.Button(
            main_frame,
            text="Confirm Target",
            command=self.confirm_target,
            style="Red.TButton",
        )
        self.confirm_target_button.grid(row=1, column=2, padx=5)

        # Start and Allow Click Buttons
        self.start_button = ttk.Button(
            main_frame,
            text="Start Tick Counting (= to Toggle)",
            command=self.start,
            style="Red.TButton",
        )
        self.start_button.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        self.allow_click_button = ttk.Button(
            main_frame,
            text="Allow Click (- to Toggle)",
            command=self.toggle_allow_click,
            style="Red.TButton",
        )
        self.allow_click_button.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        self.stop_button = ttk.Button(
            main_frame, text="Stop", command=self.stop, style="Red.TButton"
        )
        self.stop_button.grid(row=2, column=2, rowspan=2, padx=5, sticky="ns")

        # Configure grid columns to expand
        main_frame.columnconfigure(1, weight=1)

        # For displaying screenshot
        self.img_label = None

        # Internal state
        self.running = False
        self.listening = False
        self.direction = -1  # Starts counting backward
        self.x, self.y = TICK_COORD
        self.current_tick = 0
        self.start_tick = None
        self.current_target = None
        self.allow_click = False

        self.mouse = Controller()

        # Start keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def toggle_allow_click(self):
        self.allow_click = not self.allow_click
        if self.allow_click:
            self.allow_click_button.configure(style="Green.TButton")
            print("'-' pressed: Clicking enabled.")
        else:
            self.allow_click_button.configure(style="Red.TButton")
            print("'-' pressed: Clicking disabled.")

    def start(self):
        """Triggered by key or button, starts counting ticks immediately."""
        print("Starting tick counting...")
        self.capture_start_tick()
        self.listening = False
        self.running = True
        self.start_button.state(["disabled"])
        self.stop_button.state(["!disabled"])
        threading.Thread(target=self.track_ticks, daemon=True).start()

    def stop(self):
        """Stops tick counting."""
        self.running = False
        self.start_button.state(["!disabled"])
        self.stop_button.state(["disabled"])

    def confirm_start(self, event=None):
        """User confirms the starting tick."""
        if self.start_tick is not None:
            self.start_tick = None
            self.confirm_start_button.configure(style="Red.TButton")
            print("Starting Tick removed.")
        else:
            self.start_tick = self.start_var.get()
            self.confirm_start_button.configure(style="Green.TButton")
            print(f"Starting Tick set: {self.start_tick}")

    def confirm_target(self, event=None):
        """User confirms the target tick."""
        if self.current_target is not None:
            self.current_target = None
            self.confirm_target_button.configure(style="Red.TButton")
            print("Target Tick removed.")
        else:
            self.current_target = self.target_var.get()
            self.confirm_target_button.configure(style="Green.TButton")
            print(f"Target Tick set: {self.current_target}")

    def capture_start_tick(self):
        """Capture the initial tick (the safe wheel image) and display it."""
        monitor = {"top": self.y - 50, "left": self.x - 50, "width": 100, "height": 100}
        with mss.mss() as sct:
            screenshot = sct.grab(monitor)
            img_path = tempfile.mktemp(suffix=".png")
            Image.frombytes(
                "RGB", (screenshot.width, screenshot.height), screenshot.rgb
            ).save(img_path)
            print("Partial screenshot captured.")
        self.display_image(img_path)

    def display_image(self, img_path):
        """Display the screenshot in the tkinter window."""
        img = Image.open(img_path).resize((300, 300))
        img_tk = ImageTk.PhotoImage(img)
        if self.img_label is None:
            self.img_label = ttk.Label(self.root, image=img_tk, style="TLabel")
            self.img_label.image = img_tk
            self.img_label.grid(row=5, column=1, rowspan=2)
        else:
            self.img_label.configure(image=img_tk)
            self.img_label.image = img_tk
        subprocess.Popen(["start", img_path], shell=True)

    def track_ticks(self):
        """Continuously counts ticks, reversing direction on click if allowed."""
        monitor = {"top": self.y, "left": self.x, "width": 1, "height": 1}
        with mss.mss() as sct:
            last_color = None
            while self.running:
                img = sct.grab(monitor)
                current_color = img.pixel(0, 0)
                if last_color is not None and all(
                    abs(current_color[i] - TARGET_COLOR[i]) <= TOLERANCE
                    for i in range(3)
                ):
                    self.current_tick = (self.current_tick + self.direction) % 100
                    print(f"Tick: {self.current_tick}")
                    if (
                        self.allow_click
                        and self.start_tick is not None
                        and self.current_target is not None
                        and (self.current_tick + self.start_tick) % 100
                        == self.current_target
                    ):
                        self.mouse.click(Button.left, 1)
                        self.direction *= -1  # Reverse direction after click
                        self.current_target = None
                        self.allow_click = False
                        self.confirm_target_button.configure(style="Red.TButton")
                        print(f"Clicked at {self.current_tick}! Direction reversed.")
                last_color = current_color

    def on_press(self, key):
        """Keyboard hotkeys for toggling operations."""
        try:
            if key.char == "=":
                self.start()
            elif key.char == "-":
                self.toggle_allow_click()
            elif key.char == "[":
                self.toggle_bar_monitoring()
            elif key.char == "]":
                self.toggle_color_monitoring()
        except AttributeError:
            pass

    def toggle_bar_monitoring(self):
        """Toggles the vertical bar clicker."""
        if not self.bar_monitoring:
            self.bar_center_coord = self.mouse.position
            self.bar_start_monitoring()
        else:
            self.bar_stop_monitoring()

    def bar_start_monitoring(self):
        self.bar_monitoring = True
        # Use style on a ttk widget if desired; for now, just change text label color
        self.bar_button.configure(style="Green.TButton")
        self.bar_status.configure(text="Monitoring")
        threading.Thread(target=self.bar_monitor, daemon=True).start()
        self.toggle_sound.play()

    def bar_stop_monitoring(self):
        self.bar_monitoring = False
        self.bar_button.configure(style="Red.TButton")
        self.bar_status.configure(text="Idle")
        self.toggle_sound.play()
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

    def toggle_color_monitoring(self):
        """Toggles the color change clicker."""
        if not self.color_monitoring:
            self.color_sample_coord = self.mouse.position
            x, y = self.color_sample_coord
            monitor = {"top": y, "left": x, "width": 1, "height": 1}
            with mss.mss() as sct:
                screenshot = sct.grab(monitor)
                self.color_reference_color = screenshot.pixel(0, 0)
            self.color_start_monitoring()
        else:
            self.color_stop_monitoring()

    def color_start_monitoring(self):
        self.color_monitoring = True
        self.color_button.configure(style="Green.TButton")
        self.color_status.configure(text="Monitoring")
        threading.Thread(target=self.color_monitor, daemon=True).start()
        self.toggle_sound.play()

    def color_stop_monitoring(self):
        self.color_monitoring = False
        self.color_button.configure(style="Red.TButton")
        self.color_status.configure(text="Idle")
        self.toggle_sound.play()
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
        x, y = self.color_sample_coord
        monitor = {"top": y, "left": x, "width": 1, "height": 1}
        with mss.mss() as sct:
            while self.color_monitoring:
                current_color = sct.grab(monitor).pixel(0, 0)
                if any(
                    abs(c - r) > 20
                    for c, r in zip(current_color, self.color_reference_color)
                ):
                    self.mouse.click(Button.left, 1)
                    self.click_sound.play()
                    self.color_stop_monitoring()
                    break


# Run the GUI
root = tk.Tk()
app = SafeCracker(root)
root.mainloop()
