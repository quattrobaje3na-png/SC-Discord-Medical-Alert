
![medical alert logo](https://github.com/user-attachments/assets/18fc39f4-b75b-4c3e-9092-9b3a4da138b9)

This updated README reflects the new SC Squad Medical Monitor (v2.0) features, including the high-speed blur-resistant OCR, the shared Squad Status Overlay, and the mandatory GitHub app installation.

SC Squad Medical Monitor (v2.0)
SC Squad Medical Monitor is a tactical Python utility for Star Citizen that bridges the gap between in-game emergencies and squad coordination. It synchronizes local screen analysis with a shared Discord feed to provide a live Squad Status Overlay over your game session. Track Incapacitated or Respawning players in real-time, ensuring no casualty goes unnoticed during high-stakes operations.

Requires downloading the Python app here: GitHub Repository Link

✨ Key Features
Live Squad Overlay: An always-on-top HUD element showing the real-time health and respawn status of your entire squad.

Intelligent Vision Engine: Uses blur-resistant OCR to detect the "Incapacitated" state even through heavy depth-of-field effects.

Dual-Trigger Alerts: Monitors for both medical emergencies (Incap) and hard deaths (Black Screen detection).

Tactical Respawn Timer: Status locks to "Dead & Respawning" for 60 seconds after death to ensure teammates are aware of your downtime.

Automatic Resource Management: Pauses scanning when the game is minimized to save CPU/GPU overhead and prevent false triggers.

Zero-Manual Config: Integrated setup window handles all Webhook, Bot Token, and Channel configuration on first launch.

🛡️ Disclaimer
This tool is a third-party community project and is not affiliated with or endorsed by Cloud Imperium Games (CIG). The developer does not claim ownership of Star Citizen or its assets. This tool uses non-invasive visual OCR to detect game states. Using third-party software with Star Citizen carries a theoretical risk; the developer is not responsible for any actions taken against your account.

🚀 Getting Started
Prerequisites
Python 3.x: Ensure Python is installed and added to your PATH.

Tesseract OCR: Required for screen monitoring. Download from UB-Mannheim/tesseract.

Note: Default install path is assumed to be C:\Program Files\Tesseract-OCR\tesseract.exe.

Discord App: You must create a Discord Bot in the Developer Portal and enable the Message Content Intent.

Installation
Clone the repository and install the required Python libraries:

Bash
pip install pyautogui pytesseract numpy opencv-python pygetwindow pillow requests discord.py
First-Time Setup
Each player runs the application locally. On launch, provide:

Player Name: Your Discord or In-Game Username.

Webhook URL: The Discord channel integration URL.

Bot Token: Your Discord App/Bot token.

Channel ID: The numerical ID of the Discord channel used for alerts.

⚖️ Legal & Privacy
Terms of Service

Privacy Policy
