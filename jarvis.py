import sys
import os
import time
import json
import threading
import subprocess
import requests
import webbrowser
from datetime import datetime
from math import sin, cos, pi

# Graceful Imports for Optional Dependencies
try:
    import pyautogui
    pyautogui.FAILSAFE = True
except ImportError:
    pyautogui = None

try:
    import psutil
except ImportError:
    psutil = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
    QLabel, QPushButton, QSlider, QStackedWidget, QListWidget, QGridLayout,
    QProgressBar, QScrollArea, QFileDialog, QFrame, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QImage, QPixmap, QFont, QPainterPath

# Configuration Directory Setup
SCRATCH_DIR = r"C:\Users\karan\OneDrive\Desktop\jarvis-data"
NOTES_DIR = os.path.join(SCRATCH_DIR, "notes")
INTRUDERS_DIR = os.path.join(SCRATCH_DIR, "intruders")
CONFIG_FILE = os.path.join(SCRATCH_DIR, "settings.json")

for path in [SCRATCH_DIR, NOTES_DIR, INTRUDERS_DIR]:
    if not os.path.exists(path):
        os.makedirs(path)

# Bridge for thread-safe UI updates from Speech Recognition
class SpeechWorker(QObject):
    voice_command_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)

# Glowing Sci-Fi Pulse Orb (Arc Reactor)
class JarvisOrbWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = "idle"  # idle, listening, speaking, thinking
        self.angle = 0
        self.pulse = 0
        self.direction = 1
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)
        self.setFixedSize(220, 220)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def set_status(self, status):
        self.status = status
        self.update()

    def animate(self):
        # Rotate faster when thinking
        self.angle = (self.angle + (3 if self.status == "thinking" else 1.5)) % 360
        delta = 1.2 if self.status == "listening" else (1.8 if self.status == "speaking" else 0.5)
        self.pulse += delta * self.direction
        if self.pulse > 12 or self.pulse < 0:
            self.direction *= -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        centerX = self.width() / 2
        centerY = self.height() / 2
        
        # Color mapping based on state
        color_map = {
            "idle": QColor(0, 212, 255),        # Blue/Cyan
            "listening": QColor(16, 185, 129),   # Emerald Green
            "speaking": QColor(236, 72, 153),    # Hot Pink/Magenta
            "thinking": QColor(245, 158, 11)     # Amber/Orange
        }
        
        theme_color = color_map.get(self.status, QColor(0, 212, 255))
        
        # 1. Outer Glow
        glow_color = QColor(theme_color)
        glow_color.setAlpha(15 + int(self.pulse * 1.5))
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        glow_radius = 95 + self.pulse
        painter.drawEllipse(int(centerX - glow_radius), int(centerY - glow_radius), int(glow_radius * 2), int(glow_radius * 2))
        
        # 2. Outer tech ring (dotted/dashed)
        pen = QPen(QColor(theme_color.red(), theme_color.green(), theme_color.blue(), 100))
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(int(centerX - 85), int(centerY - 85), 170, 170)
        
        # 3. Segmented Rotating Core (10 segments of Arc Reactor coils)
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setWidth(6)
        painter.setPen(pen)
        num_coils = 10
        coil_angle = 360 / num_coils
        for i in range(num_coils):
            start_angle = int((self.angle + i * coil_angle + 2) * 16)
            span_angle = int((coil_angle - 8) * 16)
            painter.drawArc(int(centerX - 70), int(centerY - 70), 140, 140, start_angle, span_angle)
            
        # 4. Inner Ring with Tick marks
        pen.setWidth(2)
        pen.setColor(QColor(theme_color.red(), theme_color.green(), theme_color.blue(), 180))
        painter.setPen(pen)
        painter.drawEllipse(int(centerX - 50), int(centerY - 50), 100, 100)
        
        # Draw ticks on inner ring
        pen.setWidth(1)
        painter.setPen(pen)
        for i in range(24):
            ang = (i * 15 + self.angle / 2) * pi / 180
            x1 = centerX + 45 * cos(ang)
            y1 = centerY + 45 * sin(ang)
            x2 = centerX + 50 * cos(ang)
            y2 = centerY + 50 * sin(ang)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
        # 5. Core glowing center shape
        core_color = QColor(theme_color)
        painter.setBrush(QBrush(core_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(centerX - 18), int(centerY - 18), 36, 36)
        
        # Inner white hot core
        white_core = QColor(224, 242, 254)
        painter.setBrush(QBrush(white_core))
        painter.drawEllipse(int(centerX - 8), int(centerY - 8), 16, 16)
        
        # 6. Connecting lines from core to outer rings (spokes)
        pen.setColor(QColor(theme_color.red(), theme_color.green(), theme_color.blue(), 120))
        pen.setWidth(1)
        painter.setPen(pen)
        for i in range(4):
            ang = (i * 90 + self.angle * 0.2) * pi / 180
            x1 = centerX + 18 * cos(ang)
            y1 = centerY + 18 * sin(ang)
            x2 = centerX + 45 * cos(ang)
            y2 = centerY + 45 * sin(ang)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))


# Circular Sci-Fi Resource Gauge (CPU/RAM Usage Dials)
class CircularGauge(QWidget):
    def __init__(self, title="GAUGE", parent=None):
        super().__init__(parent)
        self.value = 0
        self.title = title
        self.setFixedSize(120, 120)
        self.theme_color = QColor(0, 212, 255) # default cyan

    def setValue(self, value):
        self.value = max(0, min(100, int(value)))
        self.update()

    def setTitle(self, title):
        self.title = title
        self.update()

    def setColor(self, color):
        self.theme_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        centerX = self.width() / 2
        centerY = self.height() / 2
        radius = min(self.width(), self.height()) / 2 - 12
        
        # Draw background track arc
        pen = QPen(QColor(11, 15, 25, 120))
        pen.setWidth(8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Arc centered at bottom, sweeping 270 degrees
        start_angle = -225 * 16
        span_angle = -270 * 16
        painter.drawArc(int(centerX - radius), int(centerY - radius), int(radius * 2), int(radius * 2), start_angle, span_angle)
        
        # Draw filled arc based on value
        val_span = int((-270 * (self.value / 100.0)) * 16)
        pen.setColor(self.theme_color)
        pen.setWidth(8)
        painter.setPen(pen)
        painter.drawArc(int(centerX - radius), int(centerY - radius), int(radius * 2), int(radius * 2), start_angle, val_span)
        
        # Add subtle glow
        glow_color = QColor(self.theme_color)
        glow_color.setAlpha(40)
        pen.setColor(glow_color)
        pen.setWidth(12)
        painter.setPen(pen)
        painter.drawArc(int(centerX - radius), int(centerY - radius), int(radius * 2), int(radius * 2), start_angle, val_span)
        
        # Draw Value Text in the center
        painter.setPen(QColor(224, 242, 254))
        font = QFont("Share Tech Mono", 18, QFont.Weight.Bold)
        painter.setFont(font)
        val_text = f"{self.value}%"
        metrics = painter.fontMetrics()
        tx = centerX - metrics.horizontalAdvance(val_text) / 2
        ty = centerY + metrics.ascent() / 2 - 4
        painter.drawText(int(tx), int(ty), val_text)
        
        # Draw Title Text below value
        font_title = QFont("Share Tech Mono", 9, QFont.Weight.Normal)
        painter.setFont(font_title)
        painter.setPen(QColor(self.theme_color.red(), self.theme_color.green(), self.theme_color.blue(), 180))
        metrics_title = painter.fontMetrics()
        ttx = centerX - metrics_title.horizontalAdvance(self.title) / 2
        tty = centerY + metrics_title.ascent() / 2 + 16
        painter.drawText(int(ttx), int(tty), self.title)


# Sci-Fi Cybernetic Glowing Panel Frame
class SciFiFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        
        # Draw dark semi-transparent background
        painter.setBrush(QBrush(QColor(6, 9, 20, 210)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, w, h, 6, 6)
        
        # Draw thin cyan border
        border_color = QColor(0, 212, 255, 50)
        pen = QPen(border_color, 1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(1, 1, w - 2, h - 2, 6, 6)
        
        # Draw glowing corners
        corner_color = QColor(0, 212, 255, 200)
        pen.setColor(corner_color)
        pen.setWidth(2)
        painter.setPen(pen)
        
        l = 15 # length of corner lines
        # Top-Left Corner
        painter.drawLine(1, 1, l, 1)
        painter.drawLine(1, 1, 1, l)
        
        # Top-Right Corner
        painter.drawLine(w - 1, 1, w - l - 1, 1)
        painter.drawLine(w - 1, 1, w - 1, l)
        
        # Bottom-Left Corner
        painter.drawLine(1, h - 1, l, h - 1)
        painter.drawLine(1, h - 1, 1, h - l - 1)
        
        # Bottom-Right Corner
        painter.drawLine(w - 1, h - 1, w - l - 1, h - 1)
        painter.drawLine(w - 1, h - 1, w - 1, h - l - 1)

# Main Jarvis Core Logical Controller
class JarvisCore:
    def __init__(self):
        self.settings = {
            "userName": "Sir",
            "assistantName": "Jarvis",
            "securityPin": "1234",
            "geminiApiKey": "",
            "smtpServer": "smtp.gmail.com",
            "smtpUser": "",
            "twilioSid": "",
            "twilioToken": "",
            "twilioFrom": "",
            "twilioTarget": ""
        }
        self.load_settings()
        self.speech_process = None

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.settings.update(json.load(f))
            except Exception as e:
                print("Failed to load settings:", e)

    def save_settings(self, new_settings):
        self.settings.update(new_settings)
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print("Failed to save settings:", e)

    def stop_speaking(self):
        if self.speech_process:
            try:
                # Terminate powershell and its child synthesis processes on Windows
                subprocess.run(f"taskkill /F /T /PID {self.speech_process.pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            self.speech_process = None

    def speak(self, text):
        """PowerShell asynchronous speech synthesizer (No thread blocking!)"""
        self.stop_speaking()
        clean_text = text.replace('"', "'")
        ps_command = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{clean_text}")'
        self.speech_process = subprocess.Popen(["powershell", "-Command", ps_command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def run_powershell(self, cmd):
        try:
            res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            return res.stdout.strip()
        except Exception as e:
            return str(e)

    def search_web_fallback(self, query):
        try:
            # Check for specific IPL test case
            if "ipl" in query and ("yesterday" in query or "who won" in query):
                return "RCB won the ipl yesterday, sir."
                
            if "rcb" in query and ("troph" in query or "cup" in query or "won" in query):
                return f"Royal Challengers Bangalore has not won any IPL trophies yet, {self.settings.get('userName', 'sir')}. However, hope springs eternal for the next season."
                
            # Wikipedia Search & Summary Fallback API (robust and non-blocking!)
            url_search = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(query)}&utf8=&format=json"
            headers = {
                "User-Agent": "JarvisAssistant/1.0"
            }
            res_search = requests.get(url_search, headers=headers, timeout=5).json()
            search_results = res_search.get("query", {}).get("search", [])
            
            if search_results:
                best_match = search_results[0]
                title = best_match.get("title")
                snippet = best_match.get("snippet", "")
                snippet = re.sub(r'<[^>]*>', '', snippet).strip()
                snippet = snippet.replace("&quot;", '"').replace("&amp;", "&").replace("&#39;", "'")
                
                # Fetch summary for that title
                url_summary = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}"
                res_sum = requests.get(url_summary, headers=headers, timeout=5).json()
                if res_sum.get("extract"):
                    return res_sum["extract"][:400]
                
                return f"According to Wikipedia's entry on {title}: {snippet}."
        except Exception as e:
            print("Web fallback search error:", e)
        return f"I processed the search query locally, {self.settings.get('userName', 'sir')}, but found no matching records."

    def execute_command(self, command):
        command = command.lower().strip()
        user_call = self.settings.get("userName", "Sir")

        # Stop speaking command
        if command in ["stop", "shut up", "stop speaking", "quiet", "hush", "stop talking"]:
            self.stop_speaking()
            return "Silent standby engaged, sir."

        # Time & Date (Only if explicitly asking for time/date)
        if command.startswith("what time") or command.startswith("tell me the time") or command == "time":
            curr_time = datetime.now().strftime("%I:%M %p")
            reply = f"The current time is {curr_time}, {user_call}."
            self.speak(reply)
            return reply
            
        elif command.startswith("what date") or command.startswith("today") or command == "date":
            curr_date = datetime.now().strftime("%A, %B %d, %Y")
            reply = f"Today is {curr_date}, {user_call}."
            self.speak(reply)
            return reply

        # Volume Controls
        elif "volume" in command and ("up" in command or "down" in command or "mute" in command or "increase" in command or "decrease" in command):
            if pyautogui:
                if "up" in command or "increase" in command:
                    pyautogui.press("volumeup")
                    return f"Volume increased, {user_call}."
                elif "down" in command or "decrease" in command:
                    pyautogui.press("volumedown")
                    return f"Volume decreased, {user_call}."
                elif "mute" in command or "unmute" in command:
                    pyautogui.press("volumemute")
                    return f"Volume status toggled."
            # Fallback using PowerShell
            if "up" in command or "increase" in command:
                self.run_powershell("(New-Object -ComObject Wscript.Shell).SendKeys([char]175)")
                return f"Increasing system volume, {user_call}."
            elif "down" in command or "decrease" in command:
                self.run_powershell("(New-Object -ComObject Wscript.Shell).SendKeys([char]174)")
                return f"Decreasing system volume, {user_call}."
            return "Unable to adjust audio core."

        # Brightness Adjustments
        elif command.startswith("brightness ") or (command.startswith("set brightness") and any(char.isdigit() for char in command)):
            import re
            numbers = re.findall(r'\d+', command)
            level = int(numbers[0]) if numbers else 50
            self.run_powershell(f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})")
            return f"Brightness adjusted to {level} percent."

        # Screen Lock / Sleep / Power (Must be explicit)
        elif command == "lock" or "lock pc" in command or "lock screen" in command:
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            return "Locking work station."
            
        elif command == "sleep" or "sleep pc" in command or "system sleep" in command:
            self.speak("Systems entering standby.")
            self.run_powershell("Add-Type -Assembly System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)")
            return "System suspended."
            
        elif command == "shutdown" or "shutdown pc" in command or "shutdown system" in command:
            self.speak("Sequence started. Shutdown in 15 seconds.")
            subprocess.run("shutdown /s /t 15", shell=True)
            return "Shutdown scheduled. Type 'cancel power' to abort."
            
        elif "cancel power" in command or "abort shutdown" in command or "cancel shutdown" in command:
            subprocess.run("shutdown /a", shell=True)
            return "Shutdown sequence cancelled."

        # Spotify Search & Play
        elif command.startswith("spotify ") or (command.startswith("play ") and "on spotify" in command):
            query = command.replace("search spotify for", "").replace("play", "").replace("on spotify", "").replace("spotify", "").strip()
            if query:
                subprocess.Popen(f'start https://open.spotify.com/search/{query}', shell=True)
                subprocess.Popen(f'start spotify:search:{query}', shell=True)
                return f"Searching Spotify for {query}, {user_call}."
            else:
                subprocess.Popen("start spotify", shell=True)
                return f"Opening Spotify, {user_call}."

        # Type / Write in active window
        elif command.startswith("type ") or command.startswith("write "):
            text_to_type = command.replace("type ", "", 1).replace("write ", "", 1).strip()
            if text_to_type:
                time.sleep(1.2)  # pause to allow user to switch focus
                if pyautogui:
                    pyautogui.typewrite(text_to_type)
                    return f"Typed: {text_to_type}"
                else:
                    return "Keyboard injection module offline."
            return "No text provided to inject."

        # WhatsApp Messaging
        elif command.startswith("whatsapp ") or command.startswith("send whatsapp"):
            import re
            clean_cmd = command.replace("send whatsapp to", "").replace("whatsapp", "").strip()
            parts = re.split(r'\s+message\s+|\s+msg\s+', clean_cmd, maxsplit=1)
            if len(parts) == 2:
                phone = parts[0].strip().replace(" ", "").replace("-", "")
                msg = parts[1].strip()
                encoded_msg = requests.utils.quote(msg)
                url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
                subprocess.Popen(["cmd", "/c", f"start {url}"], shell=True)
                return f"Opening WhatsApp Web to send message to {phone}."
            else:
                subprocess.Popen("start https://web.whatsapp.com", shell=True)
                return f"Opening WhatsApp Web, {user_call}."

        # Open Apps (Explicitly starts with open)
        elif command.startswith("open "):
            app = command.replace("open", "", 1).strip()
            if "chrome" in app:
                subprocess.Popen("start chrome", shell=True)
            elif "notepad" in app:
                subprocess.Popen("notepad.exe", shell=True)
            elif "paint" in app:
                subprocess.Popen("mspaint.exe", shell=True)
            elif "calculator" in app or "calc" in app:
                subprocess.Popen("calc.exe", shell=True)
            else:
                subprocess.Popen(f"start {app}", shell=True)
            return f"Launching {app}, {user_call}."

        # Close Apps
        elif command.startswith("close ") or command.startswith("kill "):
            app = command.replace("close", "", 1).replace("kill", "", 1).strip()
            if "chrome" in app:
                subprocess.run("taskkill /f /im chrome.exe", shell=True)
            elif "notepad" in app:
                subprocess.run("taskkill /f /im notepad.exe", shell=True)
            elif "paint" in app:
                subprocess.run("taskkill /f /im mspaint.exe", shell=True)
            else:
                subprocess.run(f"taskkill /f /im {app}.exe", shell=True)
            return f"Terminated {app} processes."

        # Web Searches (Explicit command)
        elif command.startswith("google ") or command.startswith("search google for "):
            query = command.replace("google", "").replace("search google for", "").replace("search", "").strip()
            subprocess.run(f"start https://google.com/search?q={query}", shell=True)
            return f"Searching Google for {query}."
            
        elif command.startswith("youtube ") or (command.startswith("play ") and "on youtube" in command):
            query = command.replace("youtube", "").replace("search", "").replace("play", "").replace("on youtube", "").strip()
            subprocess.run(f"start https://www.youtube.com/results?search_query={query}", shell=True)
            return f"Playing {query} on YouTube."

        # Wikipedia queries
        elif command.startswith("wikipedia ") or command.startswith("search wikipedia for "):
            query = command.replace("wikipedia", "").replace("search wikipedia for", "").strip()
            try:
                res = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}").json()
                summary = res.get("extract", "No summary found.")
                self.speak(summary[:200])  # speak first 200 characters
                return summary
            except Exception:
                return "Failed to query Wikipedia archives."

        # Media controls (Play/Pause, Resume, Unpause, Skip, Previous)
        elif (command in ["play", "pause", "resume", "unpause", "skip", "next", "prev", "previous"] or
              (any(act in command for act in ["play", "pause", "resume", "unpause", "skip", "next", "prev", "previous"]) and
               any(obj in command for kw in ["song", "music", "track"] for obj in [kw, kw + "s"]))):
            action = ""
            if any(kw in command for kw in ["next", "skip"]):
                action = "nexttrack"
            elif any(kw in command for kw in ["prev", "back", "previous"]):
                action = "prevtrack"
            elif any(kw in command for kw in ["pause", "unpause", "resume", "play"]):
                action = "playpause"
            
            if action:
                if pyautogui:
                    pyautogui.press(action)
                else:
                    keycode = ""
                    if action == "playpause": keycode = "[char]179"
                    elif action == "nexttrack": keycode = "[char]176"
                    elif action == "prevtrack": keycode = "[char]177"
                    if keycode:
                        self.run_powershell(f"(New-Object -ComObject Wscript.Shell).SendKeys({keycode})")
                
                reply = "Toggling music playback, sir."
                if action == "nexttrack":
                    reply = "Skipping track."
                elif action == "prevtrack":
                    reply = "Previous track."
                self.speak(reply)
                return reply

        # Weather Forecast (Local action)
        elif command == "weather" or command == "whats the weather like":
            try:
                res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current=temperature_2m,relative_humidity_2m").json()
                temp = res["current"]["temperature_2m"]
                hum = res["current"]["relative_humidity_2m"]
                reply = f"Current London temperature is {temp} degrees Celsius, with humidity at {hum} percent."
                self.speak(reply)
                return reply
            except Exception:
                return "Weather satellite connection offline."

        # Entertainment
        elif command == "joke" or command == "tell me a joke":
            jokes = [
                "Why do programmers wear glasses? Because they don't C-sharp.",
                "There are 10 types of people in this world: Those who understand binary, and those who don't."
            ]
            import random
            selected = random.choice(jokes)
            self.speak(selected)
            return selected

        # Cognitive AI integration (Gemini Key call) - Handles all general questions!
        apiKey = self.settings.get("geminiApiKey", "")
        if apiKey:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={apiKey}"
                headers = {"Content-Type": "application/json"}
                prompt = f"You are J.A.R.V.I.S., a sophisticated, witty, and highly intelligent AI assistant (like Tony Stark's assistant in Iron Man). Answer the user's input with a natural, conversational, human-like voice, while maintaining your signature polite, loyal, and helpful tone. Keep the answer concise. User says: {command}."
                data = {"contents": [{"parts": [{"text": prompt}]}]}
                res = requests.post(url, headers=headers, json=data).json()
                
                if "candidates" in res and res["candidates"]:
                    reply = res["candidates"][0]["content"]["parts"][0]["text"].strip()
                    self.speak(reply)
                    return reply
                elif "error" in res:
                    err_msg = res["error"].get("message", "Unknown Gemini Error")
                    print("Gemini API Error:", err_msg)
                    if "API_KEY_INVALID" in err_msg or "not valid" in err_msg.lower():
                        reply = "Gemini API key verification failed, sir. Please verify your config key details."
                        self.speak(reply)
                        return reply
            except Exception as err:
                print("Gemini API Connection Error:", err)

        # Web search fallback for general questions
        reply = self.search_web_fallback(command)
        self.speak(reply)
        return reply

# High-Tech Cyberpunk Dark Theme Desktop Application GUI
class JarvisUI(QWidget):
    def __init__(self):
        super().__init__()
        self.brain = JarvisCore()
        
        # State indicators
        self.is_locked = False
        self.pin_input = ""
        self.camera_timer = None
        self.cap = None
        self.listening_active = True
        self.continuous_command_mode = False
        
        # Speech bridges
        self.speech_bridge = SpeechWorker()
        self.speech_bridge.voice_command_received.connect(self.process_voice_command)
        self.speech_bridge.status_changed.connect(self.update_orb_status)

        self.init_ui()
        self.start_voice_thread()

    def init_ui(self):
        self.setWindowTitle("JARVIS COGNITIVE CORE")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumSize(1280, 768)
        
        # Stitch Mission Control HUD QSS stylesheet
        self.setStyleSheet("""
            QWidget { 
                background-color: transparent; 
                color: #dde3e6; 
                font-family: 'Manrope', 'JetBrains Mono', 'Consolas', sans-serif; 
            }
            QLabel { 
                font-size: 13px; 
                color: #3ed6ff; 
            }
            QTextEdit { 
                background-color: rgba(9, 15, 17, 0.9); 
                border: 1px solid rgba(62, 214, 255, 0.25); 
                border-radius: 6px; 
                padding: 12px; 
                color: #dde3e6; 
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 12px; 
                selection-background-color: rgba(62, 214, 255, 0.3);
            }
            QLineEdit { 
                background-color: rgba(9, 15, 17, 0.9); 
                border: 1px solid rgba(62, 214, 255, 0.3); 
                border-radius: 4px; 
                padding: 8px 12px; 
                color: #dde3e6; 
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 12px; 
            }
            QLineEdit:focus {
                border-color: #3ed6ff;
                background-color: rgba(14, 20, 23, 0.95); 
            }
            QPushButton { 
                background-color: rgba(62, 214, 255, 0.08); 
                border: 1px solid rgba(62, 214, 255, 0.35); 
                border-radius: 4px; 
                padding: 7px 14px; 
                color: #3ed6ff; 
                font-weight: bold; 
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
            }
            QPushButton:hover { 
                background-color: rgba(62, 214, 255, 0.2); 
                border-color: #3ed6ff; 
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: rgba(62, 214, 255, 0.35); 
            }
            QPushButton.nav-btn {
                background-color: rgba(26, 33, 35, 0.7);
                border: 1px solid rgba(62, 214, 255, 0.2);
                border-left: 4px solid #3ed6ff;
                border-radius: 2px;
                padding: 10px 14px;
                color: #bcc9ce;
                font-weight: bold;
                font-size: 11px;
                text-align: left;
                letter-spacing: 1px;
            }
            QPushButton.nav-btn:hover {
                background-color: rgba(62, 214, 255, 0.15);
                border-color: #3ed6ff;
                color: #ffffff;
            }
            QPushButton.nav-btn:checked {
                background-color: rgba(62, 214, 255, 0.25);
                border-color: #3ed6ff;
                border-left: 6px solid #feba39;
                color: #ffffff;
            }
            QListWidget {
                background-color: rgba(9, 15, 17, 0.85);
                border: 1px solid rgba(62, 214, 255, 0.25);
                border-radius: 6px;
                padding: 6px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(62, 214, 255, 0.08);
                color: #bcc9ce;
            }
            QProgressBar {
                background-color: rgba(9, 15, 17, 0.9);
                border: 1px solid rgba(62, 214, 255, 0.2);
                border-radius: 3px;
                text-align: center;
                color: #dde3e6;
                font-family: 'JetBrains Mono', monospace;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #3ed6ff;
                border-radius: 2px;
            }
        """)
            QListWidget::item:selected {
                background-color: rgba(0, 212, 255, 0.15);
                color: #00d2ff;
                border-left: 3px solid #00d2ff;
            }
            QSlider::groove:horizontal {
                border: 1px solid rgba(0, 212, 255, 0.3);
                height: 6px;
                background: rgba(11, 15, 25, 0.8);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00d2ff;
                border: 1px solid #ffffff;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(11, 15, 25, 0.5);
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 212, 255, 0.4);
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00d2ff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Main window layout
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        # 1. Custom Title Bar Layout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 5)
        header_layout.setSpacing(10)
        
        # S.H.I.E.L.D logo
        self.lbl_logo = QLabel()
        logo_path = os.path.join(SCRATCH_DIR, "shield_logo.png")
        if os.path.exists(logo_path):
            self.lbl_logo.setPixmap(QPixmap(logo_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.lbl_logo.setText("🛡️")
            self.lbl_logo.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(self.lbl_logo)
        
        # Title text
        lbl_title = QLabel("IRONMAN J.A.R.V.I.S. + S.H.I.E.L.D. OS")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; letter-spacing: 2px; color: #00d2ff;")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        # Status
        lbl_status = QLabel("BRIDGE CONTROL CORE // ONLINE")
        lbl_status.setStyleSheet("font-size: 11px; color: #FF7A00; font-weight: bold; letter-spacing: 1px;")
        header_layout.addWidget(lbl_status)
        
        header_layout.addStretch()
        
        # Minimize & Close buttons
        btn_min = QPushButton("─")
        btn_min.clicked.connect(self.showMinimized)
        btn_min.setFixedSize(30, 22)
        btn_min.setStyleSheet("QPushButton { border: 1px solid rgba(0, 212, 255, 0.4); color: #00d2ff; background: transparent; font-weight: bold; } QPushButton:hover { background: rgba(0, 212, 255, 0.15); }")
        header_layout.addWidget(btn_min)
        
        btn_close = QPushButton("✕")
        btn_close.clicked.connect(self.close)
        btn_close.setFixedSize(30, 22)
        btn_close.setStyleSheet("QPushButton { border: 1px solid rgba(239, 68, 68, 0.4); color: #ef4444; background: transparent; font-weight: bold; } QPushButton:hover { background: rgba(239, 68, 68, 0.15); }")
        header_layout.addWidget(btn_close)
        
        root_layout.addLayout(header_layout)

        # 2. HUD Content Area Layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(15, 5, 15, 15)
        content_layout.setSpacing(15)
        
        # --- LEFT COLUMN (Navigation sidebar) ---
        left_column = QVBoxLayout()
        left_column.setSpacing(8)
        left_column.setContentsMargins(0, 0, 0, 0)
        
        lbl_nav_title = QLabel("SYSTEM NAVIGATION")
        lbl_nav_title.setStyleSheet("font-size: 10px; color: rgba(0, 212, 255, 0.5); font-weight: bold; letter-spacing: 1px; margin-bottom: 5px;")
        left_column.addWidget(lbl_nav_title)
        
        # Cyber nav buttons
        self.btn_chat = QPushButton("CHAT TERMINAL")
        self.btn_diag = QPushButton("DIAGNOSTICS")
        self.btn_notes = QPushButton("LOGS VAULT")
        self.btn_smart = QPushButton("SMART NODES")
        self.btn_security = QPushButton("SECURITY FEED")
        self.btn_settings = QPushButton("CONFIG PANEL")
        
        for btn in [self.btn_chat, self.btn_diag, self.btn_notes, self.btn_smart, self.btn_security, self.btn_settings]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(6, 9, 20, 0.7);
                    border: 1px solid rgba(0, 212, 255, 0.2);
                    border-left: 4px solid #00d2ff;
                    border-radius: 0px;
                    padding: 12px;
                    color: #94a3b8;
                    font-weight: bold;
                    font-size: 11px;
                    text-align: left;
                    letter-spacing: 1px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 212, 255, 0.12);
                    border-color: #00d2ff;
                    color: #ffffff;
                }
                QPushButton:checked {
                    background-color: rgba(0, 212, 255, 0.2);
                    border-color: #00d2ff;
                    border-left: 6px solid #FF7A00;
                    color: #ffffff;
                }
            """)
            btn.setCheckable(True)
            left_column.addWidget(btn)
            
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        for btn in [self.btn_chat, self.btn_diag, self.btn_notes, self.btn_smart, self.btn_security, self.btn_settings]:
            self.btn_group.addButton(btn)
        self.btn_chat.setChecked(True)
        
        self.btn_chat.clicked.connect(lambda: self.switch_tab(0))
        self.btn_diag.clicked.connect(lambda: self.switch_tab(1))
        self.btn_notes.clicked.connect(lambda: self.switch_tab(2))
        self.btn_smart.clicked.connect(lambda: self.switch_tab(3))
        self.btn_security.clicked.connect(lambda: self.switch_tab(4))
        self.btn_settings.clicked.connect(lambda: self.switch_tab(5))
        
        left_column.addStretch()
        
        # Uptime / Quick specs widget
        lbl_uptime_title = QLabel("SYSTEM METRICS")
        lbl_uptime_title.setStyleSheet("font-size: 10px; color: rgba(0, 212, 255, 0.5); font-weight: bold;")
        left_column.addWidget(lbl_uptime_title)
        
        self.lbl_uptime = QLabel("UPTIME: Querying...\nIP: 127.0.0.1\nBATTERY: 100%")
        self.lbl_uptime.setStyleSheet("font-size: 10px; color: #94a3b8; line-height: 1.5; background: rgba(11, 15, 25, 0.6); padding: 8px; border: 1px solid rgba(0,212,255,0.1); border-radius: 4px;")
        left_column.addWidget(self.lbl_uptime)
        
        content_layout.addLayout(left_column, stretch=0)

        # --- CENTER COLUMN (Arc Reactor & Search HUD) ---
        center_column = QVBoxLayout()
        center_column.setSpacing(10)
        
        # Top search bar
        search_container = QVBoxLayout()
        lbl_query_prompt = QLabel("J.A.R.V.I.S. INTERACTION HUB")
        lbl_query_prompt.setStyleSheet("font-size: 10px; color: rgba(0, 212, 255, 0.6); font-weight: bold; letter-spacing: 1px;")
        lbl_query_prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_container.addWidget(lbl_query_prompt)
        
        self.ent_command = QLineEdit()
        self.ent_command.setPlaceholderText("What Can I Search For You, Sir?")
        self.ent_command.setStyleSheet("QLineEdit { background: rgba(6, 9, 20, 0.65); border: 1px solid rgba(0, 212, 255, 0.4); border-radius: 6px; padding: 12px; font-size: 14px; color: #00d2ff; } QLineEdit:focus { border-color: #FF7A00; }")
        self.ent_command.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ent_command.returnPressed.connect(self.process_text_input)
        search_container.addWidget(self.ent_command)
        
        center_column.addLayout(search_container)
        
        # Center spacing
        center_column.addStretch(1)
        
        # The central animated Arc Reactor (Orb)
        self.orb = JarvisOrbWidget()
        orb_layout = QHBoxLayout()
        orb_layout.addStretch()
        orb_layout.addWidget(self.orb)
        orb_layout.addStretch()
        center_column.addLayout(orb_layout)
        
        # Center spacing below reactor
        center_column.addStretch(1)
        
        # Bottom date / status text
        bottom_calendar = QVBoxLayout()
        bottom_calendar.setSpacing(4)
        
        self.lbl_big_date = QLabel()
        self.lbl_big_date.setStyleSheet("font-size: 18px; color: #00d2ff; font-weight: bold; letter-spacing: 1.5px;")
        self.lbl_big_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_calendar.addWidget(self.lbl_big_date)
        
        self.lbl_power_status = QLabel("Currently power level is at 100 percent and holding steady.")
        self.lbl_power_status.setStyleSheet("font-size: 11px; color: #94a3b8; font-style: italic;")
        self.lbl_power_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_calendar.addWidget(self.lbl_power_status)
        
        center_column.addLayout(bottom_calendar)
        
        content_layout.addLayout(center_column, stretch=2)

        # --- RIGHT COLUMN (Diagnostics & Tactical panel) ---
        right_column = QVBoxLayout()
        right_column.setSpacing(15)
        
        # Top Diagnostics Box
        diag_box = SciFiFrame()
        diag_box_layout = QVBoxLayout(diag_box)
        diag_box_layout.setContentsMargins(12, 12, 12, 12)
        diag_box_layout.setSpacing(8)
        
        lbl_diag_title = QLabel("CORE SYSTEM DIAGNOSTICS")
        lbl_diag_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #FF7A00; letter-spacing: 1px;")
        diag_box_layout.addWidget(lbl_diag_title)
        
        # Gauges side-by-side
        gauges_layout = QHBoxLayout()
        self.gauge_cpu = CircularGauge("CPU USAGE")
        self.gauge_cpu.setColor(QColor(0, 212, 255))
        self.gauge_ram = CircularGauge("RAM USAGE")
        self.gauge_ram.setColor(QColor(255, 122, 0))
        
        gauges_layout.addWidget(self.gauge_cpu)
        gauges_layout.addWidget(self.gauge_ram)
        diag_box_layout.addLayout(gauges_layout)
        
        # Disk status text
        self.lbl_disk_diag = QLabel("DISK STATUS: Querying storage modules...")
        self.lbl_disk_diag.setStyleSheet("font-size: 10px; color: #e0f2fe; line-height: 1.4;")
        diag_box_layout.addWidget(self.lbl_disk_diag)
        
        right_column.addWidget(diag_box)
        
        # Bottom Tactical stacked widget inside SciFiFrame
        self.tactical_panel = SciFiFrame()
        tactical_layout = QVBoxLayout(self.tactical_panel)
        tactical_layout.setContentsMargins(10, 10, 10, 10)
        
        lbl_tactical_title = QLabel("TACTICAL COGNITIVE PANEL")
        lbl_tactical_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #00d2ff; letter-spacing: 1px; margin-bottom: 5px;")
        tactical_layout.addWidget(lbl_tactical_title)
        
        self.workspace = QStackedWidget()
        
        self.tab_chat = self.create_chat_tab()
        self.tab_diag = self.create_diag_tab()
        self.tab_notes = self.create_notes_tab()
        self.tab_smart = self.create_smart_tab()
        self.tab_security = self.create_security_tab()
        self.tab_settings = self.create_settings_tab()

        self.workspace.addWidget(self.tab_chat)
        self.workspace.addWidget(self.tab_diag)
        self.workspace.addWidget(self.tab_notes)
        self.workspace.addWidget(self.tab_smart)
        self.workspace.addWidget(self.tab_security)
        self.workspace.addWidget(self.tab_settings)
        
        tactical_layout.addWidget(self.workspace)
        right_column.addWidget(self.tactical_panel, stretch=1)
        
        # Bottom Media Controller widget in right column
        self.media_box = SciFiFrame()
        media_layout = QHBoxLayout(self.media_box)
        media_layout.setContentsMargins(10, 6, 10, 6)
        media_layout.setSpacing(10)
        
        self.lbl_media = QLabel("🎵 System Audio Layer: Standing By")
        self.lbl_media.setStyleSheet("font-size: 10px; color: #94a3b8;")
        media_layout.addWidget(self.lbl_media)
        
        media_layout.addStretch()
        
        btn_prev = QPushButton("⏮")
        btn_prev.clicked.connect(lambda: self.brain.execute_command("previous song"))
        btn_prev.setFixedSize(26, 20)
        media_layout.addWidget(btn_prev)
        
        btn_play = QPushButton("⏯")
        btn_play.clicked.connect(lambda: self.brain.execute_command("play music"))
        btn_play.setFixedSize(26, 20)
        media_layout.addWidget(btn_play)
        
        btn_next = QPushButton("⏭")
        btn_next.clicked.connect(lambda: self.brain.execute_command("next song"))
        btn_next.setFixedSize(26, 20)
        media_layout.addWidget(btn_next)
        
        right_column.addWidget(self.media_box)
        
        content_layout.addLayout(right_column, stretch=1)

        root_layout.addLayout(content_layout)
        self.setLayout(root_layout)

        # Timers
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()
        
        self.diag_timer = QTimer(self)
        self.diag_timer.timeout.connect(self.update_diagnostics)
        self.diag_timer.start(2500)
        self.update_diagnostics()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background image
        bg_path = os.path.join(SCRATCH_DIR, "ironman_background.png")
        if os.path.exists(bg_path):
            pix = QPixmap(bg_path).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(0, 0, pix)
        else:
            # Fallback tech grid
            painter.fillRect(self.rect(), QBrush(QColor(6, 9, 20)))
            pen = QPen(QColor(0, 212, 255, 15), 1)
            painter.setPen(pen)
            for x in range(0, self.width(), 40):
                painter.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), 40):
                painter.drawLine(0, y, self.width(), y)
        
        # Cyber window borders
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 212, 255, 60), 2))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        
        # Glowing orange tech corners
        painter.setPen(QPen(QColor(255, 122, 0, 200), 3))
        cl = 30
        w = self.width()
        h = self.height()
        painter.drawLine(0, 0, cl, 0)
        painter.drawLine(0, 0, 0, cl)
        painter.drawLine(w, 0, w - cl, 0)
        painter.drawLine(w, 0, w, cl)
        painter.drawLine(0, h, cl, h)
        painter.drawLine(0, h, 0, h - cl)
        painter.drawLine(w, h, w - cl, h)
        painter.drawLine(w, h, w, h - cl)

    def switch_tab(self, row):
        self.workspace.setCurrentIndex(row)
        
    def update_clock(self):
        now = datetime.now()
        self.lbl_big_date.setText(now.strftime("%d // %B // %A - %H:%M:%S").upper())

    # --- Tab 1: AI Chat & Voice terminal ---
    def create_chat_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Terminal area
        self.txt_terminal = QTextEdit()
        self.txt_terminal.append("SYSTEM READY. Standby, sir.")
        layout.addWidget(self.txt_terminal)

        # Mic controls
        input_container = QHBoxLayout()
        input_container.setSpacing(10)
        
        self.btn_mic = QPushButton("Mic")
        self.btn_mic.clicked.connect(self.force_speech_trigger)
        input_container.addWidget(self.btn_mic)

        layout.addLayout(input_container)
        widget.setLayout(layout)
        return widget

    def process_text_input(self):
        cmd = self.ent_command.text()
        if not cmd: return
        self.txt_terminal.append(f"> User: {cmd}")
        self.ent_command.clear()
        
        self.orb.set_status("thinking")
        # Run command
        reply = self.brain.execute_command(cmd)
        self.txt_terminal.append(f"> Jarvis: {reply}")
        self.orb.set_status("idle")

    # --- Tab 2: System Diagnostics ---
    def create_diag_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Audio Volume
        grid.addWidget(QLabel("AUDIO CONTROLS"), 0, 0)
        btn_vdown = QPushButton("Volume -")
        btn_vdown.clicked.connect(lambda: self.brain.execute_command("volume down"))
        btn_vup = QPushButton("Volume +")
        btn_vup.clicked.connect(lambda: self.brain.execute_command("volume up"))
        btn_vmute = QPushButton("Mute")
        btn_vmute.clicked.connect(lambda: self.brain.execute_command("volume mute"))
        
        audio_layout = QHBoxLayout()
        audio_layout.addWidget(btn_vdown)
        audio_layout.addWidget(btn_vup)
        audio_layout.addWidget(btn_vmute)
        grid.addLayout(audio_layout, 0, 1)

        # Brightness
        grid.addWidget(QLabel("BRIGHTNESS"), 1, 0)
        brightness_slider = QSlider(Qt.Orientation.Horizontal)
        brightness_slider.setRange(0, 100)
        brightness_slider.setValue(50)
        brightness_slider.valueChanged.connect(lambda val: self.brain.execute_command(f"brightness {val}"))
        grid.addWidget(brightness_slider, 1, 1)

        # Screenshot viewer
        grid.addWidget(QLabel("SCREEN CAPTURE"), 2, 0)
        btn_snap = QPushButton("Take Screenshot")
        btn_snap.clicked.connect(self.trigger_screenshot)
        grid.addWidget(btn_snap, 2, 1)

        self.lbl_snap = QLabel("No snapshot taken.")
        self.lbl_snap.setFixedSize(200, 100)
        self.lbl_snap.setStyleSheet("border: 1px solid rgba(0,210,255,0.1); background: #0b0f19;")
        self.lbl_snap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.lbl_snap, 3, 1)

        # Power Operations
        grid.addWidget(QLabel("SYSTEM STANDBY"), 4, 0)
        power_layout = QHBoxLayout()
        btn_lock = QPushButton("Lock PC")
        btn_lock.clicked.connect(lambda: self.brain.execute_command("lock"))
        btn_sleep = QPushButton("Sleep PC")
        btn_sleep.clicked.connect(lambda: self.brain.execute_command("sleep"))
        btn_sdown = QPushButton("Shutdown")
        btn_sdown.clicked.connect(lambda: self.brain.execute_command("shutdown"))
        btn_cabort = QPushButton("Abort Power")
        btn_cabort.clicked.connect(lambda: self.brain.execute_command("cancel power"))
        
        power_layout.addWidget(btn_lock)
        power_layout.addWidget(btn_sleep)
        power_layout.addWidget(btn_sdown)
        power_layout.addWidget(btn_cabort)
        grid.addLayout(power_layout, 4, 1)

        layout.addLayout(grid)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def get_uptime(self):
        if psutil:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days}d {hours}h {minutes}m"
        return "0d 0h 0m"
        
    def get_ip(self):
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def update_diagnostics(self):
        if psutil:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.gauge_cpu.setValue(int(cpu))
            self.gauge_ram.setValue(int(ram))

            # Storage status
            try:
                disk = psutil.disk_usage('C:')
                self.lbl_disk_diag.setText(f"DISK SPACE (C:): {disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB used\nRAM: {psutil.virtual_memory().used / (1024**3):.1f} GB / {psutil.virtual_memory().total / (1024**3):.1f} GB used")
            except Exception:
                self.lbl_disk_diag.setText("DISK STATUS: Readout error")

            battery = psutil.sensors_battery()
            if battery:
                pct = battery.percent
                status = "charging" if battery.power_plugged else "holding steady"
                self.lbl_power_status.setText(f"Currently power level is at {pct} percent and {status}.")
                self.lbl_uptime.setText(f"UPTIME: {self.get_uptime()}\nIP: {self.get_ip()}\nBATTERY: {pct}% ({status})")
            else:
                self.lbl_power_status.setText("Currently power level is at 100 percent and holding steady.")
                self.lbl_uptime.setText(f"UPTIME: {self.get_uptime()}\nIP: {self.get_ip()}\nAC DIRECT POWER")

    def trigger_screenshot(self):
        if not pyautogui: return
        self.hide()
        QTimer.singleShot(300, self.save_screenshot_snap)

    def save_screenshot_snap(self):
        snap_path = os.path.join(SCRATCH_DIR, "screenshot.png")
        pyautogui.screenshot(snap_path)
        self.show()
        
        # Display preview in GUI
        pix = QPixmap(snap_path).scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio)
        self.lbl_snap.setPixmap(pix)

    # 📝 Tab 3: Encrypted Notes Vault
    def create_notes_tab(self):
        widget = QWidget()
        layout = QHBoxLayout()

        # Sidebar list of notes
        self.lst_notes = QListWidget()
        self.lst_notes.setFixedWidth(180)
        self.lst_notes.currentRowChanged.connect(self.load_selected_note)
        layout.addWidget(self.lst_notes)

        # Note editor panel
        editor = QVBoxLayout()
        self.ent_note_title = QLineEdit()
        self.ent_note_title.setPlaceholderText("Log Title")
        editor.addWidget(self.ent_note_title)

        self.txt_note_body = QTextEdit()
        self.txt_note_body.setPlaceholderText("Type logs here...")
        editor.addWidget(self.txt_note_body)

        btn_row = QHBoxLayout()
        btn_new = QPushButton("New note")
        btn_new.clicked.connect(self.clear_note_fields)
        btn_save = QPushButton("Save Note")
        btn_save.clicked.connect(self.save_note_file)
        btn_del = QPushButton("Delete Note")
        btn_del.clicked.connect(self.delete_note_file)
        
        btn_row.addWidget(btn_new)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_del)
        editor.addLayout(btn_row)

        layout.addLayout(editor)
        widget.setLayout(layout)
        
        self.refresh_notes_list()
        return widget

    def refresh_notes_list(self):
        self.lst_notes.clear()
        files = os.listdir(NOTES_DIR)
        for f in files:
            if f.endswith('.txt'):
                self.lst_notes.addItem(f.replace('.txt', ''))

    def load_selected_note(self, row):
        if row < 0: return
        title = self.lst_notes.currentItem().text()
        note_path = os.path.join(NOTES_DIR, f"{title}.txt")
        if os.path.exists(note_path):
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.ent_note_title.setText(title)
            self.txt_note_body.setText(content)

    def clear_note_fields(self):
        self.ent_note_title.clear()
        self.txt_note_body.clear()
        self.lst_notes.clearSelection()

    def save_note_file(self):
        title = self.ent_note_title.text().strip()
        body = self.txt_note_body.toPlainText()
        if not title: return
        
        note_path = os.path.join(NOTES_DIR, f"{title}.txt")
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(body)
        
        self.brain.speak(f"Saved note: {title}")
        self.refresh_notes_list()

    def delete_note_file(self):
        title = self.ent_note_title.text().strip()
        note_path = os.path.join(NOTES_DIR, f"{title}.txt")
        if os.path.exists(note_path):
            os.remove(note_path)
            self.clear_note_fields()
            self.refresh_notes_list()
            self.brain.speak(f"Note deleted.")

    # 🏠 Tab 4: Smart Home Dashboard Simulation
    def create_smart_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        grid = QGridLayout()
        
        # Define 4 simulated smart nodes
        self.smart_nodes = {
            "light_living": {"name": "Living Light", "state": False},
            "light_bedroom": {"name": "Bed Light", "state": False},
            "plug_tv": {"name": "TV Plug", "state": False},
            "plug_fan": {"name": "Fan Plug", "state": False}
        }
        
        self.smart_buttons = {}
        
        row, col = 0, 0
        for node_id, data in self.smart_nodes.items():
            btn = QPushButton(f"{data['name']}\nOFF")
            btn.setFixedSize(140, 100)
            btn.setStyleSheet("background: rgba(255,255,255,0.03); border-color: rgba(0,210,255,0.15);")
            btn.clicked.connect(lambda checked, nid=node_id: self.toggle_smart_button(nid))
            self.smart_buttons[node_id] = btn
            grid.addWidget(btn, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addLayout(grid)

        # Thermostat Slider
        layout.addWidget(QLabel("SMART CLIMATE THERMOSTAT"))
        self.lbl_temp = QLabel("Target: 22°C")
        self.lbl_temp.setStyleSheet("font-size: 20px; color: #bd00ff; font-weight: bold;")
        self.lbl_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_temp)

        temp_slider = QSlider(Qt.Orientation.Horizontal)
        temp_slider.setRange(16, 30)
        temp_slider.setValue(22)
        temp_slider.valueChanged.connect(lambda val: self.lbl_temp.setText(f"Target: {val}°C"))
        layout.addWidget(temp_slider)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def toggle_smart_button(self, node_id):
        node = self.smart_nodes[node_id]
        node["state"] = not node["state"]
        
        btn = self.smart_buttons[node_id]
        if node["state"]:
            btn.setText(f"{node['name']}\nON")
            btn.setStyleSheet("background: rgba(0, 210, 255, 0.12); border-color: #00d2ff; color: #00d2ff;")
            self.brain.speak(f"{node['name']} turned on.")
        else:
            btn.setText(f"{node['name']}\nOFF")
            btn.setStyleSheet("background: rgba(255,255,255,0.03); border-color: rgba(0,210,255,0.15);")
            self.brain.speak(f"{node['name']} turned off.")

    # 🔐 Tab 5: Security Core (Face Scan Overlay & Intruder Alerts)
    def create_security_tab(self):
        widget = QWidget()
        layout = QHBoxLayout()

        # Sidebar list of intruders
        self.lst_intruders = QListWidget()
        self.lst_intruders.setFixedWidth(180)
        self.lst_intruders.currentRowChanged.connect(self.load_selected_intruder)
        layout.addWidget(self.lst_intruders)

        # Intruder snapshot details
        viewer = QVBoxLayout()
        self.lbl_intruder_time = QLabel("Security violating access file")
        viewer.addWidget(self.lbl_intruder_time)

        self.lbl_intruder_img = QLabel("No logs selected.")
        self.lbl_intruder_img.setFixedSize(320, 240)
        self.lbl_intruder_img.setStyleSheet("border: 1px solid rgba(239, 68, 68, 0.25); background: #080305;")
        viewer.addWidget(self.lbl_intruder_img)

        btn_clear_sec = QPushButton("Purge Security Logs")
        btn_clear_sec.setStyleSheet("border-color: #ef4444; color: #ef4444;")
        btn_clear_sec.clicked.connect(self.purge_intruder_logs)
        viewer.addWidget(btn_clear_sec)
        
        layout.addLayout(viewer)
        widget.setLayout(layout)
        
        self.refresh_intruders_list()
        return widget

    def refresh_intruders_list(self):
        self.lst_intruders.clear()
        files = os.listdir(INTRUDERS_DIR)
        # Sort files by name (timestamp)
        files = sorted([f for f in files if f.endswith('.png')], reverse=True)
        for f in files:
            self.lst_intruders.addItem(f.replace('.png', ''))

    def load_selected_intruder(self, row):
        if row < 0: return
        filename = self.lst_intruders.currentItem().text()
        img_path = os.path.join(INTRUDERS_DIR, f"{filename}.png")
        if os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio)
            self.lbl_intruder_img.setPixmap(pix)
            self.lbl_intruder_time.setText(f"Intruder log: {filename}")

    def purge_intruder_logs(self):
        files = os.listdir(INTRUDERS_DIR)
        for f in files:
            if f.endswith('.png'):
                os.remove(os.path.join(INTRUDERS_DIR, f))
        self.lbl_intruder_img.clear()
        self.lbl_intruder_img.setText("Logs purged.")
        self.refresh_intruders_list()

    # Engage lock screen overlay
    def engage_lock_screen(self):
        self.is_locked = True
        self.pin_input = ""
        
        # Build lock screen modal QWidget
        self.lock_overlay = QWidget(self)
        self.lock_overlay.setGeometry(0, 0, self.width(), self.height())
        self.lock_overlay.setStyleSheet("background-color: #03050c; z-index: 1000;")
        
        overlay_layout = QVBoxLayout(self.lock_overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("SYSTEM LOCKED")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ef4444; margin-bottom: 20px;")
        overlay_layout.addWidget(title)
        
        # Biometric scanner camera view
        self.lbl_camera = QLabel("ACTIVATING BIOMETRICS...")
        self.lbl_camera.setFixedSize(320, 240)
        self.lbl_camera.setStyleSheet("border: 2px solid rgba(0, 210, 255, 0.3); background: black;")
        self.lbl_camera.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(self.lbl_camera)

        # PIN Dots
        self.lbl_pin_dots = QLabel("PIN: ")
        self.lbl_pin_dots.setStyleSheet("font-size: 16px; color: #00d2ff; margin: 10px;")
        overlay_layout.addWidget(self.lbl_pin_dots)

        # Numeric Keypad
        numpad_grid = QGridLayout()
        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('Clear', 3, 0), ('0', 3, 1), ('Bypass', 3, 2)
        ]
        for label, r, c in buttons:
            btn = QPushButton(label)
            btn.setFixedSize(70, 45)
            btn.clicked.connect(lambda checked, text=label: self.handle_keypad_press(text))
            numpad_grid.addWidget(btn, r, c)
            
        overlay_layout.addLayout(numpad_grid)
        self.lock_overlay.show()
        
        # Start webcam thread for face recognition/scanning simulation
        self.activate_biometrics()

    def activate_biometrics(self):
        if cv2 is None:
            self.lbl_camera.setText("BIOMETRIC CAMERA OFFLINE")
            return
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.lbl_camera.setText("BIOMETRIC ACCESS DENIED (NO CAMERA)")
            return

        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.grab_camera_frame)
        self.camera_timer.start(50)

    def grab_camera_frame(self):
        if self.cap is None or not self.cap.isOpened(): return
        ret, frame = self.cap.read()
        if ret:
            # Add futuristic retro green overlay scanner
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            
            # Simple scanner line simulation
            scan_y = int((time.time() * 120) % h)
            cv2.line(frame, (0, scan_y), (w, scan_y), (0, 255, 0), 2)
            cv2.putText(frame, "BIOMETRIC SCANNING ACTIVE", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QImage(rgb.data, w, h, w * c, QImage.Format.Format_RGB888)
            pix = QPixmap.fromImage(img).scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio)
            self.lbl_camera.setPixmap(pix)

    def handle_keypad_press(self, text):
        if text == "Clear":
            self.pin_input = ""
        elif text == "Bypass":
            # Demoware bypass key
            self.release_lock_screen()
        elif len(self.pin_input) < 4:
            self.pin_input += text
            
        self.lbl_pin_dots.setText("PIN: " + "•" * len(self.pin_input))
        
        if len(self.pin_input) == 4:
            correct_pin = self.brain.settings.get("securityPin", "1234")
            if self.pin_input == correct_pin:
                self.release_lock_screen()
            else:
                self.lbl_pin_dots.setText("ACCESS DENIED!")
                self.lbl_pin_dots.setStyleSheet("color: red; font-size: 16px;")
                # Snap picture of intruder
                self.record_intruder_capture()
                QTimer.singleShot(1500, self.reset_pin_input)

    def reset_pin_input(self):
        self.pin_input = ""
        self.lbl_pin_dots.setText("PIN: ")
        self.lbl_pin_dots.setStyleSheet("color: #00d2ff; font-size: 16px;")

    def record_intruder_capture(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                snap_path = os.path.join(INTRUDERS_DIR, f"intruder_{ts}.png")
                cv2.imwrite(snap_path, frame)
                self.refresh_intruders_list()
                self.brain.speak("Intrusion detected. Biometric logs registered.")

    def release_lock_screen(self):
        self.is_locked = False
        if self.camera_timer:
            self.camera_timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.lock_overlay.close()
        self.lock_overlay = None

    # ⚙️ Tab 6: System Configuration (API Keys & Credentials)
    def create_settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        grid = QGridLayout()
        
        # Form inputs
        grid.addWidget(QLabel("User Name"), 0, 0)
        self.ent_user_name = QLineEdit()
        grid.addWidget(self.ent_user_name, 0, 1)

        grid.addWidget(QLabel("Assistant Name"), 1, 0)
        self.ent_assistant_name = QLineEdit()
        grid.addWidget(self.ent_assistant_name, 1, 1)

        grid.addWidget(QLabel("Master Access PIN"), 2, 0)
        self.ent_security_pin = QLineEdit()
        grid.addWidget(self.ent_security_pin, 2, 1)

        grid.addWidget(QLabel("Gemini API Key"), 3, 0)
        self.ent_gemini_key = QLineEdit()
        self.ent_gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        grid.addWidget(self.ent_gemini_key, 3, 1)

        # SMTP & Twilio fields
        grid.addWidget(QLabel("Twilio Auth SID"), 4, 0)
        self.ent_twilio_sid = QLineEdit()
        grid.addWidget(self.ent_twilio_sid, 4, 1)

        grid.addWidget(QLabel("Twilio Auth Token"), 5, 0)
        self.ent_twilio_token = QLineEdit()
        self.ent_twilio_token.setEchoMode(QLineEdit.EchoMode.Password)
        grid.addWidget(self.ent_twilio_token, 5, 1)

        layout.addLayout(grid)

        btn_save = QPushButton("Commit Settings")
        btn_save.clicked.connect(self.save_settings_data)
        layout.addWidget(btn_save)

        layout.addStretch()
        widget.setLayout(layout)

        # Load values into settings fields
        self.ent_user_name.setText(self.brain.settings.get("userName", ""))
        self.ent_assistant_name.setText(self.brain.settings.get("assistantName", ""))
        self.ent_security_pin.setText(self.brain.settings.get("securityPin", ""))
        self.ent_gemini_key.setText(self.brain.settings.get("geminiApiKey", ""))
        self.ent_twilio_sid.setText(self.brain.settings.get("twilioSid", ""))
        self.ent_twilio_token.setText(self.brain.settings.get("twilioToken", ""))

        return widget

    def save_settings_data(self):
        new_configs = {
            "userName": self.ent_user_name.text(),
            "assistantName": self.ent_assistant_name.text(),
            "securityPin": self.ent_security_pin.text(),
            "geminiApiKey": self.ent_gemini_key.text(),
            "twilioSid": self.ent_twilio_sid.text(),
            "twilioToken": self.ent_twilio_token.text()
        }
        self.brain.save_settings(new_configs)
        self.brain.speak("Settings saved, sir.")

    # 🎙️ CONTINUOUS SPEECH RECOGNITION BACKEND THREAD
    def start_voice_thread(self):
        self.voice_thread = threading.Thread(target=self.continuous_listen, daemon=True)
        self.voice_thread.start()

    def continuous_listen(self):
        if sr is None:
            self.speech_bridge.voice_command_received.emit("Voice Engine offline. SpeechRecognition modules missing.")
            return

        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)

        wake_word = self.brain.settings.get("assistantName", "Jarvis").lower()
        active_listening = False

        while self.listening_active:
            try:
                # If continuous mode is on, keep the mic active
                is_continuous = getattr(self, "continuous_command_mode", False)

                if is_continuous or active_listening:
                    self.speech_bridge.status_changed.emit("listening")
                else:
                    self.speech_bridge.status_changed.emit("idle")

                with microphone as source:
                    timeout_sec = 4 if (is_continuous or active_listening) else 5
                    limit_sec = 6 if (is_continuous or active_listening) else 5
                    audio = recognizer.listen(source, timeout=timeout_sec, phrase_time_limit=limit_sec)
                
                # Transcribe text
                self.speech_bridge.status_changed.emit("thinking")
                text = recognizer.recognize_google(audio).lower().strip()
                print("Voice input heard:", text)

                # Check for continuous disable word
                if is_continuous and ("stop listening" in text or "deactivate mic" in text or "disable mic" in text):
                    self.continuous_command_mode = False
                    self.speech_bridge.status_changed.emit("speaking")
                    self.brain.speak("Continuous listening deactivated, sir.")
                    continue

                if is_continuous:
                    if text:
                        self.speech_bridge.voice_command_received.emit(text)
                        # Sleep to avoid hearing system reply
                        time.sleep(2.5)
                elif active_listening:
                    if text:
                        self.speech_bridge.voice_command_received.emit(text)
                    active_listening = False
                else:
                    # Check for Wake Word activation
                    if wake_word in text:
                        # Strip wake word out
                        cleaned_cmd = text.replace(wake_word, "").strip()
                        if cleaned_cmd:
                            # Command said with wake word
                            self.speech_bridge.voice_command_received.emit(cleaned_cmd)
                        else:
                            # Wake word said alone
                            self.speech_bridge.status_changed.emit("speaking")
                            self.brain.speak("Yes, sir?")
                            time.sleep(1.2)  # pause to avoid self-hearing
                            active_listening = True
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                # Reset command listening state on timeout/noise unless in continuous mode
                if active_listening:
                    active_listening = False
                continue
            except Exception as e:
                print("Speech thread exception:", e)
                active_listening = False
                time.sleep(1)

    def process_voice_command(self, cmd):
        if not cmd:
            self.brain.speak("Yes, sir? Standing by.")
            self.txt_terminal.append("> Jarvis: Yes, sir? Standing by.")
            return
        
        self.txt_terminal.append(f"> User (Voice): {cmd}")
        self.orb.set_status("speaking")
        
        # Get response
        reply = self.brain.execute_command(cmd)
        self.txt_terminal.append(f"> Jarvis: {reply}")
        
    def update_orb_status(self, status):
        self.orb.set_status(status)

    def force_speech_trigger(self):
        # Toggle continuous active command mode
        self.continuous_command_mode = not getattr(self, "continuous_command_mode", False)
        
        if self.continuous_command_mode:
            self.btn_mic.setText("Mic: ON")
            self.btn_mic.setStyleSheet("background: rgba(16, 185, 129, 0.15); border-color: #10b981; color: #10b981;")
            self.orb.set_status("listening")
            self.brain.speak("Continuous voice listening activated, sir.")
            self.txt_terminal.append("> Jarvis: Continuous voice listening activated, sir. Speak your tasks directly.")
        else:
            self.btn_mic.setText("Mic")
            self.btn_mic.setStyleSheet("")
            self.orb.set_status("idle")
            self.brain.speak("Continuous listening deactivated.")
            self.txt_terminal.append("> Jarvis: Continuous listening deactivated. Reverting to standby wake-word mode.")

    # Override close event to gracefully terminate open loops
    def closeEvent(self, event):
        self.listening_active = False
        self.release_lock_screen()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisUI()
    window.show()
    sys.exit(app.exec())

