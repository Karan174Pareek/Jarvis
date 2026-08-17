# JARVIS OS — Production AI Operating System & Autonomous Assistant

![Repository](https://img.shields.io/badge/Jarvis-v4.2-3ed6ff)
![Status](https://img.shields.io/badge/Status-Production%20Grade-emerald)
![Database](https://img.shields.io/badge/Database-SQLite%20Persistent-blue)
![Security](https://img.shields.io/badge/Security-PBKDF2%20%2B%20Per--User%20Isolation-darkgreen)

**JARVIS OS** is a production-grade personal AI operating system built with a modular Python backend, persistent SQLite database, multi-user authentication, controlled action registry, task manager, background reminder scheduler, encrypted notes vault, per-user file management, long-term memory, and a native PyQt6 Mission Control HUD interface.

---

## 🌟 Key System Capabilities

- **Zero Fake Data**: 100% real application state backed by a persistent SQLite database (`jarvis_production.db`). Empty states are displayed when no user records exist.
- **Multi-User Authentication & Isolation**: PBKDF2/SHA256 salted password hashing, token-based session management, and per-user data isolation across all database queries and file storage.
- **Controlled AI Action Registry**: Controlled tool execution system (`command_system.py`) that parses natural language intent into type-checked system operations (creating tasks, scheduling reminders, saving notes, setting memories) without allowing unsafe code execution.
- **Conversational AI Engine**: Provider abstraction (`ai_service.py`) supporting Gemini API and local intelligent fallbacks, with message persistence and conversation context history in SQLite (`chat_service.py`).
- **Task & Reminder Scheduler**: Complete task manager (`task_service.py`) and background daemon thread (`reminder_service.py`) that triggers active due reminders and emits notifications.
- **Notes & Knowledge Vault**: Markdown notes manager (`notes_service.py`) with tag organization and full-text search.
- **Secure File Vault & Document Indexing**: Per-user file storage (`file_service.py`) with text content extraction and document search.
- **Controlled Long-Term Memory**: Memory storage engine (`memory_service.py`) allowing users to store, view, delete, and clear explicit personal preferences and workflows.
- **Global Search Engine**: Unified multi-entity search (`global_search.py`) spanning user messages, tasks, notes, files, and memories.
- **Native PyQt6 Stitch Mission Control HUD**: Dark glassmorphic desktop interface (`#0e1417` HUD glass, `#3ed6ff` cyan glow), custom-painted Arc Reactor orb visualizer (`JarvisOrbWidget`), live CPU/RAM telemetry badges, digital clock, and protocol controls.

---

## 🛠 System Architecture

```
Jarvis/
├── database.py           # SQLite connection pool, session manager, & schema initialization
├── models.py             # Database ORM/table models (Users, Sessions, Tasks, Reminders, Notes, Files, etc.)
├── auth_service.py       # Password hashing (PBKDF2+SHA256), login, registration, & session tokens
├── ai_service.py         # AI provider abstraction (Gemini / OpenAI / Fallbacks)
├── chat_service.py       # Conversation & message persistence and search
├── command_system.py     # Controlled AI action registry & intent parser
├── task_service.py       # Task CRUD, status tracking, and priority levels
├── reminder_service.py   # Reminder scheduling & background daemon thread
├── notification_service.py# System notification engine
├── notes_service.py      # Encrypted notes vault & full-text search
├── file_service.py       # Secure per-user file vault & text indexer
├── search_service.py     # Wikipedia, Open-Meteo weather API, & web search retrieval
├── memory_service.py     # Controlled long-term memory engine
├── global_search.py      # Unified search across all user entities
├── security.py           # Input sanitization, path traversal prevention, & audit logging
├── voice_service.py      # Asynchronous STT/TTS voice engine
├── jarvis.py             # Core Assistant Application & PyQt6 Mission Control HUD GUI
└── jarvis-data/          # SQLite database storage & per-user file directories
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Required packages: `PyQt6`, `psutil`, `requests`, `pyautogui`, `SpeechRecognition`

```bash
pip install PyQt6 psutil requests pyautogui SpeechRecognition
```

### Running the Application

Launch the native desktop application:
```bash
python jarvis.py
```

---

## 🔒 Security & Data Isolation

- **Password Security**: Passwords are hashed using `PBKDF2` with `SHA-256` using 100,000 iterations and a unique 16-byte random salt per user.
- **Data Isolation**: Every SQL query strictly filters by `user_id = ?`. User A can never query or view User B's conversations, tasks, notes, files, or memories.
- **Audit Logging**: Every system action and command execution is logged to the `activity_logs` table via `SecurityService.log_activity()`.

---

## 🔗 Repository

GitHub Repository: [https://github.com/Karan174Pareek/Jarvis.git](https://github.com/Karan174Pareek/Jarvis.git)
