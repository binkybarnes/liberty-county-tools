import tkinter as tk
import threading
import time
import pydirectinput
import mss
from pynput import keyboard
from PIL import Image, ImageTk
import tempfile
import subprocess

# Constants
TARGET_COLOR = (178, 178, 178)
TOLERANCE = 5
TICK_COORD = (957, 396)

class SafeCracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Safe Cracker")

        tk.Label(root, text="Starting Tick:").grid(row=0, column=0)
        self.start_var = tk.IntVar()
        start_entry = tk.Entry(root, textvariable=self.start_var)
        start_entry.grid(row=0, column=1)
        start_entry.bind("<Return>", self.confirm_start)

        tk.Label(root, text="Target Number:").grid(row=1, column=0)
        self.target_var = tk.IntVar()
        target_entry = tk.Entry(root, textvariable=self.target_var)
        target_entry.grid(row=1, column=1)
        target_entry.bind("<Return>", self.confirm_target)

        self.confirm_start_button = tk.Button(root, text="Confirm Start", command=self.confirm_start, bg="red", fg="white")
        self.confirm_start_button.grid(row=0, column=2)

        self.confirm_target_button = tk.Button(root, text="Confirm Target", command=self.confirm_target, bg="red", fg="white")
        self.confirm_target_button.grid(row=1, column=2)

        self.start_button = tk.Button(root, text="Start Tick Counting (= to Toggle)", command=self.start)
        self.start_button.grid(row=2, column=0, columnspan=2)
        
        self.allow_click_button = tk.Button(root, text="allow click (- to toggle)", command=self.toggle_allow_click, bg="red", fg="white")
        self.allow_click_button.grid(row=3, column=0, columnspan=2)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=2, columnspan=2)

        self.running = False
        self.listening = False
        self.direction = -1  # Starts counting backward

        self.x, self.y = TICK_COORD
        self.current_tick = 0
        self.start_tick = None 
        self.current_target = None

        self.allow_click = False


    def toggle_allow_click(self):
        self.allow_click = not self.allow_click
        if self.allow_click:
            self.allow_click_button.config(bg="green")
            print('- pressed, allowed click')
        else:
            print('- pressed, disallowed click')
            self.allow_click_button.config(bg="red")

    def start(self):
        """Triggered by first click, starts counting ticks immediately"""
        print("Starting tick counting...")
        self.capture_start_tick()
        self.listening = False
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.track_ticks, daemon=True).start()

    def stop(self):
        """Stops everything"""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def confirm_start(self, event=None):
        """User confirms the starting tick"""
        if self.start_tick:
            self.start_tick = None
            self.confirm_start_button.config(bg="red")
            print(f"Starting Tick removed")
        else: 
            self.start_tick = self.start_var.get()
            self.confirm_start_button.config(bg="green")
            print(f"Starting Tick set: {self.start_tick}")

    def confirm_target(self, event=None):
        """User confirms the target tick"""
        if self.current_target:
            self.current_target = self.target_var.get()
            self.confirm_target_button.config(bg="red")
            print(f"Target Tick removed")
        else:
            self.current_target = self.target_var.get()
            self.confirm_target_button.config(bg="green")
            print(f"Target Tick set: {self.current_target}")

    def capture_start_tick(self):
        """Capture the initial tick (the starting position)"""
        monitor = {"top": self.y - 50, "left": self.x - 50, "width": 100, "height": 100}  
        with mss.mss() as sct:
            screenshot = sct.grab(monitor)
            img_path = tempfile.mktemp(suffix='.png')
            Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb).save(img_path)
            print("Partial screenshot captured.")
        self.display_image(img_path)

    def display_image(self, img_path):
        """Display the screenshot in the tkinter window"""
        img = Image.open(img_path).resize((300, 300))
        img_tk = ImageTk.PhotoImage(img)
        self.img_label = tk.Label(self.root, image=img_tk)
        self.img_label.image = img_tk  
        self.img_label.grid(row=5, column=1, rowspan=2)
        subprocess.Popen(['start', img_path], shell=True)  

    def track_ticks(self):
        """Counts ticks, reversing on click"""
        monitor = {"top": self.y, "left": self.x, "width": 1, "height": 1}
        with mss.mss() as sct:
            last_color = None
            while self.running:
                img = sct.grab(monitor)
                current_color = img.pixel(0, 0)

                # Check if color matches target
                if last_color is not None and all(abs(current_color[i] - TARGET_COLOR[i]) <= TOLERANCE for i in range(3)):
                    self.current_tick = (self.current_tick + self.direction) % 100  # Modulo 100
                    print(f"Tick: {self.current_tick}")

                    if self.allow_click and self.start_tick is not None and self.current_target is not None and (self.current_tick + self.start_tick) % 100 == self.current_target:
                        pydirectinput.click()
                        self.direction *= -1  # Reverse direction after click
                        self.current_target = None  
                        self.allow_click = False
                        self.confirm_target_button.config(bg="red")
                        print(f"Clicked at {self.current_tick}! Direction reversed.")

                last_color = current_color

    def on_press(self, key):
        """Hotkey to toggle listening for first click"""
        try:
            if key.char == '=':
                self.start()
            if key.char == '-':
                self.toggle_allow_click()
        except AttributeError:
            pass

# Set up the keyboard listener
keyboard_listener = keyboard.Listener(on_press=lambda key: app.on_press(key))
keyboard_listener.start()

# Run the GUI
root = tk.Tk()
app = SafeCracker(root)
root.mainloop()
