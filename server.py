import os
import sys
import json
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

try:
    import psutil
except ImportError:
    psutil = None

PORT = 8000
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis-data")
NOTES_DIR = os.path.join(DATA_DIR, "notes")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

for directory in [DATA_DIR, NOTES_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)


class JarvisRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            self.handle_status_api()
        elif self.path == "/api/settings":
            self.handle_settings_get()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/command":
            self.handle_command_api()
        elif self.path == "/api/settings":
            self.handle_settings_post()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_status_api(self):
        cpu = psutil.cpu_percent(interval=None) if psutil else 15.0
        ram = psutil.virtual_memory().percent if psutil else 42.0

        data = {
            "status": "ONLINE",
            "cpu_percent": cpu,
            "ram_percent": ram,
            "time": datetime.now().strftime("%H:%M:%S"),
            "timestamp": time.time()
        }
        self.send_json_response(200, data)

    def handle_settings_get(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
            except Exception:
                settings = {}
        else:
            settings = {"userName": "Sir", "assistantName": "Jarvis"}
        self.send_json_response(200, settings)

    def handle_settings_post(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            new_settings = json.loads(post_data.decode("utf-8"))
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(new_settings, f, indent=4)
            self.send_json_response(200, {"status": "success", "message": "Settings updated"})
        except Exception as e:
            self.send_json_response(400, {"status": "error", "message": str(e)})

    def handle_command_api(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            req = json.loads(post_data.decode("utf-8"))
            cmd = req.get("command", "").strip()
            response_text = self.execute_jarvis_command(cmd)
            self.send_json_response(200, {"status": "success", "response": response_text})
        except Exception as e:
            self.send_json_response(500, {"status": "error", "response": f"Execution error: {str(e)}"})

    def execute_jarvis_command(self, cmd):
        if not cmd:
            return "No command provided."

        cmd_lower = cmd.lower()

        if "time" in cmd_lower:
            now_str = datetime.now().strftime("%I:%M %p, %B %d, %Y")
            return f"The current time is {now_str}."

        if "status" in cmd_lower or "telemetry" in cmd_lower:
            cpu = psutil.cpu_percent(interval=None) if psutil else 15
            ram = psutil.virtual_memory().percent if psutil else 42
            return f"System Status: OPTIMAL. CPU Utilization: {cpu}%, Memory Usage: {ram}%. WebGL HUD Online."

        if "note" in cmd_lower:
            note_content = cmd.split("note", 1)[-1].strip()
            if note_content:
                filename = f"note_{int(time.time())}.txt"
                filepath = os.path.join(NOTES_DIR, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(note_content)
                return f"Note recorded and saved to jarvis-data/notes/{filename}: '{note_content}'"
            return "Please provide note text (e.g. 'note Buy supplies')."

        if "who are you" in cmd_lower or "identify" in cmd_lower:
            return "I am JARVIS — Just A Rather Very Intelligent System. Autonomous AI Command Assistant."

        if "help" in cmd_lower or "protocol" in cmd_lower:
            return "Available protocols: 'time', 'status', 'note <text>', 'identify', 'initialize'."

        if "initialize" in cmd_lower or "init" in cmd_lower:
            return "Protocols initialized. All subsystem modules synchronized and operational."

        return f"Acknowledged command: '{cmd}'. Core system processing request."

    def send_json_response(self, code, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def run_server(port=PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, JarvisRequestHandler)
    print(f"[JARVIS SERVER] Running Mission Control HUD backend on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[JARVIS SERVER] Shutting down server gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    port_arg = PORT
    if len(sys.argv) > 1:
        try:
            port_arg = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port_arg)
