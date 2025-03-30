import tkinter as tk
import threading
from pynput import mouse, keyboard

class CoordinateGetter:
    def __init__(self, root):
        self.root = root
        self.root.title("Coordinate Getter")

        # Status label
        self.status_label = tk.Label(root, text="Press '-' to start", font=("Arial", 14))
        self.status_label.pack(pady=10)

        # Coordinate label (remains visible after stopping)
        self.coord_label = tk.Label(root, text="X: -, Y: -", font=("Arial", 14))
        self.coord_label.pack(pady=10)

        self.running = False
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

        self.mouse_controller = mouse.Controller()

    def on_key_press(self, key):
        """Toggles coordinate tracking when '-' is pressed."""
        try:
            if key.char == '-':
                if self.running:
                    self.running = False
                    self.status_label.config(text="Press '-' to start")
                else:
                    self.running = True
                    self.status_label.config(text="Tracking...")
                    threading.Thread(target=self.track_coordinates, daemon=True).start()
        except AttributeError:
            pass  # Handle special keys if needed

    def track_coordinates(self):
        """Continuously updates mouse coordinates while running."""
        while self.running:
            x, y = self.mouse_controller.position
            self.coord_label.config(text=f"X: {x}, Y: {y}")
            self.root.update()
            self.root.after(50)  # Update every 50ms

# Run the GUI
root = tk.Tk()
app = CoordinateGetter(root)
root.mainloop()
