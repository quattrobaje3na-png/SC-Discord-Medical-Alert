
![medical alert logo](https://github.com/user-attachments/assets/18fc39f4-b75b-4c3e-9092-9b3a4da138b9)

# SC-Discord-Medical-Alert (v1.0)

**SC-Discord-Medical-Alert** is a lightweight Python-based visual monitoring tool designed for Star Citizen. By analyzing the visual state of the game client in real-time, it bridges the gap between in-game emergencies and out-of-game coordination.

✨ Key Features

* Monitors display in real time to identify Incapacitated and Repawned states 
* Sends instant, low-profile notifications to your chosen Discord channel via a provided Webhook.
* Automatically pauses scanning when the game is minimized to save resources and prevent false triggers.
* No need to edit JSON files manually; a setup window handles your configuration on the first launch.
* Each Player has to run the application locally and tie into the discord webhook and provide their Discord or In Game Username. 

🚀 Getting Started

1. Prerequisites
* **Python 3.x**: Ensure Python is installed on your system.
* **Tesseract OCR**: This tool requires Tesseract to monitor your game window.
    * Download and install it from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
    * *Note: Default install path is assumed to be `C:\Program Files\Tesseract-OCR\tesseract.exe`.*

2. Installation
Clone the repository or download the source code, then install the required Python libraries:

```bash
pip install pyautogui pytesseract numpy opencv-python pygetwindow pillow requests
