import tkinter as tk
import pyautogui
import pydirectinput
import pygetwindow as gw
import time
import threading


class AutoClicker:
    def __init__(self, master):
        self.master = master
        master.title("Roblox AutoClicker")
        
        # Internal state
        self.active = False
        self.sample_coord = None
        self.monitor_thread = None

        self.windows = gw.getWindowsWithTitle("Roblox")
        
        # Create GUI elements
        self.info_label = tk.Label(master, text="Hover over sample area and press 's' to capture coordinate.")
        self.info_label.pack(pady=5)
        
        self.set_sample_btn = tk.Button(master, text="Set Sample Coordinate", command=self.set_sample_coord)
        self.set_sample_btn.pack(pady=5)
        
        self.start_btn = tk.Button(master, text="Start Monitoring", command=self.start_monitor)
        self.start_btn.pack(pady=5)
        
        self.status_label = tk.Label(master, text="Status: Idle")
        self.status_label.pack(pady=5)
        
        self.stop_btn = tk.Button(master, text="Stop Monitoring", command=self.stop_monitor, state="disabled")
        self.stop_btn.pack(pady=5)
    
    def set_sample_coord(self):
        self.info_label.config(text="Hover over sample area and press 's' to capture coordinate.")
        self.master.bind('<s>', self.capture_sample_coord)
    
    def capture_sample_coord(self, event):
        self.sample_coord = pyautogui.position()
        self.info_label.config(text=f"Sample Coordinate set at: {self.sample_coord}")
        self.master.unbind('<s>')
    
    def start_monitor(self):
        if not self.sample_coord:
            self.info_label.config(text="Please set the sample coordinate first.")
            return
        self.active = True
        self.start_btn.config(state="disabled")
        self.set_sample_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Status: Monitoring...")
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.monitor_thread.start()
    
    def stop_monitor(self):
        self.active = False
        self.start_btn.config(state="normal")
        self.set_sample_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Status: Stopped")
    
    def focus_roblox(self):
        # Try to find and focus the Roblox window by title.
        
        if self.windows:
            roblox_window = self.windows[0]
            roblox_window.activate()
            time.sleep(0.01)  # brief pause to ensure focus
        else:
            self.info_label.config(text="Roblox window not found.")
    
    def monitor(self):
        # Define the reference color (black) and tolerance
        default_color = (0, 0, 0)
        tolerance = 20

        while self.active:
            current_color = pyautogui.screenshot().getpixel(self.sample_coord)

            # print(f"current color: {current_color}")
            # Check if current_color differs significantly from black.
            if any(abs(c - r) > tolerance for c, r in zip(current_color, default_color)):
                # print(f"color changed {current_color}")
                self.focus_roblox()
                x, y = self.sample_coord
                # uses pydirectinput, moves the mouse there and moves it rel or it wont click
                # pydirectinput.moveTo(x, y)
                # pydirectinput.moveTo(928, 1025)
                # pydirectinput.moveRel(1, 0, duration=0)
                pydirectinput.click()
                clicked_msg = f"Clicked at {self.sample_coord} (color: {current_color}). Set new sample coordinate for next round."
                self.info_label.config(text=clicked_msg)
                print(clicked_msg)
                # Stop monitoring after one click.
                self.active = False
                self.master.after(0, self.stop_monitor)
                break
            # time.sleep(0.0001)


# Run the GUI
root = tk.Tk()
app = AutoClicker(root)
root.mainloop()
