# JARVIS OS — Mission Control HUD & Autonomous AI Assistant

![Repository](https://img.shields.io/badge/Jarvis-v4.2-3ed6ff)
![Status](https://img.shields.io/badge/Status-Optimal-emerald)
![UI](https://img.shields.io/badge/Interface-Stitch%20HUD-blueviolet)

**JARVIS OS** is a high-density, futuristic **Mission Control HUD** and personal AI assistant system inspired by aeronautic Head-Up Displays (HUDs) and Tony Stark's JARVIS interface. It combines a WebGL-powered reactive browser dashboard with a Python backend, system telemetry monitoring, voice recognition, and local desktop automation.

---

## 🌟 Key Features

- **Stitch HUD Interface**: Single-page web application featuring high-tech glassmorphism aesthetics (`backdrop-blur`), custom HUD layout, and dark-mode styling.
- **WebGL Background Shader**: Interactive hexagonal grid with drifting ambient particle canvas rendered via native WebGL.
- **Arc Reactor Visualizer**: Dynamic animated core orb widget representing assistant status states (*Idle*, *Listening*, *Speaking*, *Thinking*).
- **Live System Telemetry**: Real-time tracking of CPU utilization, RAM allocation, latency, system temperature, and disk storage via `psutil`.
- **Command Console Feed**: Timestamped terminal logging output with typewriter animations and interactive command execution.
- **Voice & Speech Engine**: Native browser Web Speech API integration for natural language voice controls.
- **REST & Local Backend API**: Lightweight Python HTTP server serving telemetry (`/api/status`), handling system commands (`/api/command`), and managing configuration settings (`/api/settings`).

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Recommended dependencies: `psutil`, `PyQt6`, `requests`, `pyautogui`, `SpeechRecognition`

```bash
pip install psutil PyQt6 requests pyautogui SpeechRecognition
```

### Launch Modes

#### 1. Web HUD Mode (Standalone Server)
To run the Stitch Mission Control Web HUD interface directly in your web browser:
```bash
python server.py
```
Open **`http://localhost:8000`** in your browser.

#### 2. Dual Mode (Desktop App + Background Web Server)
To launch the desktop GUI while running the Web HUD backend server simultaneously:
```bash
python jarvis.py
```

#### 3. Web HUD Auto-Browser Mode
To launch the Web server and automatically open the HUD in your default web browser:
```bash
python jarvis.py --web
```

---

## 🛠 Project Structure

```
Jarvis/
├── index.html            # Stitch Mission Control HUD Interface (HTML5)
├── static/
│   └── js/
│       └── app.js        # WebGL Shader, Telemetry Client, Orb Visualizer, Terminal JS
├── server.py             # Python HTTP REST API Server & Static File Server
├── jarvis.py             # Core Assistant Engine & PyQt6 Desktop Application
├── jarvis-data/          # System configuration, notes, and intruder snapshots
│   └── settings.json
├── .gitignore
└── README.md
```

---

## 📜 Available Commands & Protocols

- **`time`** — Displays current system time and date readout.
- **`status` / `telemetry`** — Provides diagnostic output of CPU and memory stats.
- **`note <text>`** — Records a timestamped note saved directly to `jarvis-data/notes/`.
- **`identify`** — Outputs JARVIS system identity statement.
- **`initialize`** — Executes subsystem module synchronization.

---

## 🔗 Repository

GitHub Repository: [https://github.com/Karan174Pareek/Jarvis.git](https://github.com/Karan174Pareek/Jarvis.git)
