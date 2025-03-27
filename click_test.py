import pydirectinput
import pygetwindow as gw
import time

def focus_roblox():
    # Find the Roblox window by its title
    windows = gw.getWindowsWithTitle("Roblox")
    if windows:
        roblox_window = windows[0]
        roblox_window.activate()
        # time.sleep(0.01)  # Pause to ensure the window is focused
        return True
    else:
        print("Roblox window not found.")
        return False

def click_test():
    if focus_roblox():
        # Move the mouse relative by 1 pixel to trigger pointer recalibration.
        
        # Click at the target coordinates
        # pydirectinput.moveTo(928, 1025)
        # pydirectinput.moveTo(928, 375)
        # pydirectinput.moveRel(1, 0, duration=0)
        pydirectinput.click()
        print("Clicked at (928, 1025)")

click_test()
