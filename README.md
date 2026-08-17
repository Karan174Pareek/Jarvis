# JARVIS OS — Native Mission Control HUD Desktop Application

![Repository](https://img.shields.io/badge/Jarvis-v4.2-3ed6ff)
![Status](https://img.shields.io/badge/Status-Optimal-emerald)
![Interface](https://img.shields.io/badge/Desktop%20UI-Native%20PyQt6%20Stitch%20HUD-blueviolet)

**JARVIS OS** is a native **PyQt6 desktop application** built with high-density **Stitch Mission Control HUD** aesthetics, inspired by aeronautic Head-Up Displays (HUDs) and Tony Stark's JARVIS interface. It runs completely locally on your system without requiring an external web browser or web server.

---

## 🌟 Key Features

- **Stitch HUD Design System**: Dark glass aesthetic (`#0e1417` surface-dim), `#3ed6ff` luminous cyan accents, custom dark container panels, and sharp geometric layouts.
- **Arc Reactor Visualizer**: Native custom-painted segmented HUD orb (`JarvisOrbWidget`) with state animations (*IDLE*, *LISTENING*, *SPEAKING*, *THINKING*).
- **Top Telemetry Header Bar**: Live system metrics header displaying CPU %, RAM %, Latency, System Temp, and a real-time digital clock.
- **Side Navigation Protocol Panel**: Direct access to Mission Control tabs (*CHAT TERMINAL*, *DIAGNOSTICS*, *LOGS VAULT*, *SMART NODES*, *SECURITY FEED*, *CONFIG PANEL*).
- **Interactive Command Console**: Real-time voice and text command processing with timestamped feed output.
- **Biometric Security Core**: Built-in PIN authorization screen with webcam intruder snapshot logging.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages: `PyQt6`, `psutil`, `requests`, `pyautogui`, `SpeechRecognition`

```bash
pip install PyQt6 psutil requests pyautogui SpeechRecognition
```

### Running the Application

Launch the native PyQt6 desktop application directly:
```bash
python jarvis.py
```

---

## 📁 Repository Structure

```
Jarvis/
├── jarvis.py             # Core Assistant Engine & Native PyQt6 Stitch HUD Application
├── jarvis-data/          # Configuration, notes vault, and security intruder snapshots
│   ├── settings.json
│   ├── notes/
│   └── intruders/
├── .gitignore
└── README.md             # Project documentation
```

---

## 🔗 Repository

GitHub Repository: [https://github.com/Karan174Pareek/Jarvis.git](https://github.com/Karan174Pareek/Jarvis.git)
