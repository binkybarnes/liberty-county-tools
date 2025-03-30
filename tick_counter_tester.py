import tkinter as tk

class SoftFlashingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Soft Flashing Test")

        # Create a label that will change colors
        self.canvas = tk.Canvas(root, width=300, height=200, bg="#FFFFFF")  # Default to black
        self.canvas.pack()

        # Start and Stop buttons
        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.pack()
        self.stop_button = tk.Button(root, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack()

        self.running = False
        self.flash_delay = 100  # 100ms cycle
        self.flash_duration = 10  # Show 178,178,178 for 10ms

    def start(self):
        """Starts flashing colors."""
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.flash()

    def stop(self):
        """Stops flashing."""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def flash(self):
        """Flashes color for a short duration before returning to black."""
        if self.running:
            self.canvas.config(bg="#b2b2b2")  # Show gray
            self.root.after(self.flash_duration, self.reset_flash)  # Revert after 10ms

    def reset_flash(self):
        """Resets the color to black and schedules the next flash."""
        if self.running:
            self.canvas.config(bg="#FFFFFF")  # Reset to black
            self.root.after(self.flash_delay - self.flash_duration, self.flash)  # Wait 90ms, then flash again

# Run the GUI
root = tk.Tk()
app = SoftFlashingGUI(root)
root.mainloop()
