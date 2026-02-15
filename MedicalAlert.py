import pyautogui
import pytesseract
import numpy as np
import cv2
import time
import requests
import json
import os
import pygetwindow as gw
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageOps, ImageEnhance

# CONFIGURATION
CONFIG_FILE = "sc_alert_config.json"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def first_time_setup():
    """Initial setup GUI to create the config file if it doesn't exist."""
    def save_config():
        url = entry_url.get().strip()
        name = entry_name.get().strip()
        if not url or not name:
            messagebox.showwarning("Input Error", "Please fill in both fields.")
            return
        
        config_data = {"webhook_url": url, "player_name": name, "log_path": ""}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)
        
        root.destroy()

    root = tk.Tk()
    root.title("SC-Discord-Medical-Alert Setup")
    root.geometry("400x250")

    tk.Label(root, text="Initial Setup", font=("Arial", 14, "bold")).pack(pady=10)
    
    tk.Label(root, text="Discord Webhook URL:").pack()
    entry_url = tk.Entry(root, width=50)
    entry_url.pack(pady=5)

    tk.Label(root, text="Player Name (Handle):").pack()
    entry_name = tk.Entry(root, width=30)
    entry_name.pack(pady=5)

    tk.Button(root, text="Save and Start Monitoring", command=save_config, bg="#2c2f33", fg="white").pack(pady=20)
    
    root.mainloop()

def load_config():
    if not os.path.exists(CONFIG_FILE):
        first_time_setup()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return None

def send_alert(config, status_message, color):
    handle = config.get('player_name', 'Player')
    payload = {
        "embeds": [{
            "description": f"**{handle} {status_message}**",
            "color": color,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }]
    }
    try:
        requests.post(config['webhook_url'], json=payload, timeout=5)
    except: pass

def is_game_focused():
    try:
        active_window = gw.getActiveWindow()
        return active_window is not None and "Star Citizen" in active_window.title
    except: return False

def run_targeted_monitor():
    config = load_config()
    if not config: return

    print(f"--- Monitoring Active: {config['player_name']} ---")
    
    width, height = pyautogui.size()
    region_incap = (0, int(height/2), int(width/2), int(height/2))
    region_death = (0, 0, width, height)
    
    last_state = None
    black_screen_start = None
    last_alert_time = 0
    COOLDOWN = 60 

    while True:
        try:
            if not is_game_focused():
                time.sleep(2)
                continue

            current_time = time.time()
            full_screen = pyautogui.screenshot(region=region_death)
            death_gray = cv2.cvtColor(np.array(full_screen), cv2.COLOR_RGB2GRAY)
            black_percent = (np.sum(death_gray < 5) / death_gray.size) * 100

            # DEATH LOGIC
            if black_percent > 98:
                if black_screen_start is None:
                    black_screen_start = current_time
                if (current_time - black_screen_start >= 5.0):
                    if last_state != "dead":
                        send_alert(config, "has Respawned", 15417403)
                        last_alert_time = current_time
                        last_state = "dead"
                        print(f">> ALERT: Death Screen")
            else:
                black_screen_start = None

            # INCAP LOGIC
            if black_percent < 50 and last_state != "dead":
                incap_area = pyautogui.screenshot(region=region_incap)
                incap_gray = cv2.cvtColor(np.array(incap_area), cv2.COLOR_RGB2GRAY)
                pil_img = Image.fromarray(incap_gray)
                enhanced_img = ImageEnhance.Contrast(pil_img).enhance(3.0)
                text = pytesseract.image_to_string(enhanced_img, config='--psm 11').lower()

                if "incapacitated" in text:
                    if last_state != "incap" and (current_time - last_alert_time > COOLDOWN):
                        send_alert(config, "is INCAPACITATED!", 16734720)
                        last_alert_time = current_time
                        last_state = "incap"
                        print(f">> ALERT: Incapacitated")

            if black_percent < 50 and "incapacitated" not in text:
                last_state = None

        except Exception as e:
            print(f"Monitor Error: {e}")
        
        time.sleep(1.0)

if __name__ == "__main__":
    run_targeted_monitor()