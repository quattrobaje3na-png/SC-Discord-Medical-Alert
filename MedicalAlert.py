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
from PIL import Image, ImageEnhance
import discord
import threading

# --- CONFIGURATION ---
CONFIG_FILE = "sc_alert_config.json"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
APP_BRANDING = "Youtube: CMDR Quattro: SC-Discord-Medical-Alert"
RESPAWN_DISPLAY_DURATION = 60 

def first_time_setup():
    def save_config():
        data = {
            "webhook_url": entry_webhook.get().strip(),
            "player_name": entry_name.get().strip(),
            "bot_token": entry_bot.get().strip(),
            "channel_id": int(entry_channel.get().strip()) if entry_channel.get().strip().isdigit() else 0
        }
        if not all(data.values()):
            messagebox.showwarning("Error", "All fields required.")
            return
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)
        setup_root.destroy()

    setup_root = tk.Tk()
    setup_root.title("Setup")
    setup_root.geometry("450x400")
    setup_root.configure(bg="#2c2f33")
    tk.Label(setup_root, text="Player Name:").pack()
    global entry_name; entry_name = tk.Entry(setup_root, width=50); entry_name.pack()
    tk.Label(setup_root, text="Webhook URL:").pack()
    global entry_webhook; entry_webhook = tk.Entry(setup_root, width=50); entry_webhook.pack()
    tk.Label(setup_root, text="Bot Token:").pack()
    global entry_bot; entry_bot = tk.Entry(setup_root, width=50); entry_bot.pack()
    tk.Label(setup_root, text="Channel ID:").pack()
    global entry_channel; entry_channel = tk.Entry(setup_root, width=50); entry_channel.pack()
    tk.Button(setup_root, text="Save", command=save_config).pack(pady=20)
    setup_root.mainloop()

class SquadOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Squad Status")
        self.root.attributes("-topmost", True)
        self.root.geometry("350x250+100+100")
        self.root.configure(bg="#1a1a1a")
        self.label = tk.Label(self.root, text="--- SQUAD STATUS ---\nWaiting...", 
                              font=("Consolas", 10, "bold"), fg="#ff6600", bg="#1a1a1a", 
                              pady=10, justify="left", anchor="nw")
        self.label.pack(fill="both", expand=True, padx=10)
        self.players = {}

    def update_squad(self, name, status):
        self.players[name] = status
        self.refresh_display()
        # Timer logic for Dead & Respawning
        if status == "Dead & Respawning":
            print(f">>> UI: Locking status for {name} for {RESPAWN_DISPLAY_DURATION}s")
            self.root.after(RESPAWN_DISPLAY_DURATION * 1000, lambda: self.set_alive_after_delay(name))

    def set_alive_after_delay(self, name):
        # Only clear if they are still in the respawn state
        if self.players.get(name) == "Dead & Respawning":
            self.players[name] = "ALIVE"
            self.refresh_display()

    def refresh_display(self):
        display = "--- SQUAD STATUS ---\n\n"
        for p, s in self.players.items():
            icon = "💀" if s == "INCAP" else "🚩" if s == "Dead & Respawning" else "🛡️"
            display += f"{icon} {p}: {s}\n"
        self.label.config(text=display)

overlay_app = None
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"\n>>> LISTENER ACTIVE: Logged in as {client.user}\n")

@client.event
async def on_message(message):
    global overlay_app
    if message.author == client.user: return
    try:
        with open(CONFIG_FILE, "r") as f:
            conf = json.load(f)
            if message.channel.id != conf.get("channel_id"): return
        content = message.content.upper()
        name, status = "", ""
        if "INCAPACITATED" in content:
            name = message.content.split("**")[1].split()[0]
            status = "INCAP"
        elif "RESPAWNED" in content:
            name = message.content.split("**")[1].split()[0]
            status = "Dead & Respawning"
        if name and status and overlay_app:
            overlay_app.root.after(0, overlay_app.update_squad, name, status)
    except: pass

def send_alert(config, status_message, color):
    payload = {"embeds": [{"description": f"**{config['player_name']} {status_message}**", "color": color}]}
    try: requests.post(config['webhook_url'], json=payload, timeout=5)
    except: pass

def run_monitor(config):
    global overlay_app
    width, height = pyautogui.size()
    region_incap = (0, int(height/2), int(width/2), int(height/2))
    region_death = (0, 0, width, height)
    last_state, black_screen_start, last_alert_time = None, None, 0
    COOLDOWN = 60

    if overlay_app:
        overlay_app.root.after(0, overlay_app.update_squad, config['player_name'], "ALIVE")

    while True:
        try:
            active_window = gw.getActiveWindow()
            if not (active_window and "Star Citizen" in active_window.title):
                time.sleep(2); continue

            current_time = time.time()
            
            # 1. PRIORITY: BLACK SCREEN DETECTION
            full_screen = pyautogui.screenshot(region=region_death)
            death_gray = cv2.cvtColor(np.array(full_screen), cv2.COLOR_RGB2GRAY)
            black_percent = (np.sum(death_gray < 5) / death_gray.size) * 100

            if black_percent > 95:
                if black_screen_start is None: black_screen_start = current_time
                if (current_time - black_screen_start >= 2.5):
                    if last_state != "dead":
                        send_alert(config, "has Respawned", 15417403)
                        if overlay_app: 
                            overlay_app.root.after(0, overlay_app.update_squad, config['player_name'], "Dead & Respawning")
                        last_state = "dead"; last_alert_time = current_time
                time.sleep(1.0)
                continue
            else:
                black_screen_start = None

            # 2. INCAP DETECTION
            incap_area = pyautogui.screenshot(region=region_incap)
            incap_gray = cv2.cvtColor(np.array(incap_area), cv2.COLOR_RGB2GRAY)
            _, thresh = cv2.threshold(incap_gray, 150, 255, cv2.THRESH_BINARY)
            text = pytesseract.image_to_string(thresh, config='--psm 11').lower()

            if "incapacitated" in text:
                if last_state != "incap" and (current_time - last_alert_time > COOLDOWN):
                    send_alert(config, "is INCAPACITATED!", 16734720)
                    if overlay_app: 
                        overlay_app.root.after(0, overlay_app.update_squad, config['player_name'], "INCAP")
                    last_state = "incap"; last_alert_time = current_time
            
            # 3. REVIVAL RESET (FIXED)
            # Only reset automatically if we were INCAP. 
            # If we were 'dead' (Respawning), let the 60s timer handle the reset.
            elif last_state == "incap" and "incapacitated" not in text:
                if overlay_app: 
                    overlay_app.root.after(0, overlay_app.update_squad, config['player_name'], "ALIVE")
                last_state = None

        except Exception as e:
            print(f"Monitor Error: {e}")
        time.sleep(1.0)

if __name__ == "__main__":
    if not os.path.exists(CONFIG_FILE): first_time_setup()
    with open(CONFIG_FILE, "r") as f: user_config = json.load(f)
    overlay_app = SquadOverlay()
    threading.Thread(target=lambda: client.run(user_config["bot_token"]), daemon=True).start()
    threading.Thread(target=run_monitor, args=(user_config,), daemon=True).start()
    overlay_app.root.mainloop()
