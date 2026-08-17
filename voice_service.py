import os
import time
import subprocess
import threading
from PyQt6.QtCore import QObject, pyqtSignal

try:
    import speech_recognition as sr
except ImportError:
    sr = None

class VoiceSignalBridge(QObject):
    voice_command_received = pyqtSignal(str)
    status_changed = pyqtSignal(str) # idle, listening, speaking, thinking, error
    log_emitted = pyqtSignal(str)

class VoiceEngine:
    def __init__(self):
        self.bridge = VoiceSignalBridge()
        self.speech_process = None
        self.is_listening = False
        self.is_continuous = False
        self.wake_word = "jarvis"
        self._thread = None

    def speak(self, text: str):
        """Asynchronous, non-blocking PowerShell TTS Synthesis."""
        if not text:
            return
        self.stop_speaking()
        self.bridge.status_changed.emit("speaking")

        def run_tts():
            try:
                clean_text = text.replace('"', "'")
                ps_cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{clean_text}")'
                self.speech_process = subprocess.Popen(["powershell", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.speech_process.wait()
            except Exception as e:
                print("[TTS ERROR]:", e)
            finally:
                self.bridge.status_changed.emit("idle")

        t = threading.Thread(target=run_tts, daemon=True)
        t.start()

    def stop_speaking(self):
        if self.speech_process:
            try:
                subprocess.run(f"taskkill /F /T /PID {self.speech_process.pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            self.speech_process = None
        self.bridge.status_changed.emit("idle")

    def start_listening(self, continuous: bool = False):
        if self.is_listening:
            return
        self.is_listening = True
        self.is_continuous = continuous
        self._thread = threading.Thread(target=self._listening_loop, daemon=True)
        self._thread.start()
        self.bridge.log_emitted.emit(f"[VOICE] STT Listening thread started (Continuous: {continuous}).")

    def stop_listening(self):
        self.is_listening = False
        self.bridge.status_changed.emit("idle")
        self.bridge.log_emitted.emit("[VOICE] STT Listening thread stopped.")

    def _listening_loop(self):
        if sr is None:
            self.bridge.log_emitted.emit("[VOICE ERROR] speech_recognition library not available.")
            self.bridge.status_changed.emit("error")
            return

        recognizer = sr.Recognizer()
        microphone = None
        try:
            microphone = sr.Microphone()
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
        except Exception as e:
            self.bridge.log_emitted.emit(f"[VOICE ERROR] Microphone initialization error: {e}")
            self.bridge.status_changed.emit("error")
            return

        active_prompt = False

        while self.is_listening:
            try:
                if self.is_continuous or active_prompt:
                    self.bridge.status_changed.emit("listening")
                else:
                    self.bridge.status_changed.emit("idle")

                with microphone as source:
                    timeout_sec = 4 if (self.is_continuous or active_prompt) else 5
                    limit_sec = 6 if (self.is_continuous or active_prompt) else 5
                    audio = recognizer.listen(source, timeout=timeout_sec, phrase_time_limit=limit_sec)

                self.bridge.status_changed.emit("thinking")
                text = recognizer.recognize_google(audio).lower().strip()
                self.bridge.log_emitted.emit(f"[VOICE INPUT] Recognized: '{text}'")

                if self.is_continuous:
                    if "stop listening" in text or "deactivate mic" in text:
                        self.is_continuous = False
                        self.speak("Voice listening deactivated.")
                        continue
                    if text:
                        self.bridge.voice_command_received.emit(text)
                        time.sleep(2.0)
                elif active_prompt:
                    if text:
                        self.bridge.voice_command_received.emit(text)
                    active_prompt = False
                else:
                    if self.wake_word in text:
                        cleaned = text.replace(self.wake_word, "").strip()
                        if cleaned:
                            self.bridge.voice_command_received.emit(cleaned)
                        else:
                            self.speak("Yes, sir? Standing by.")
                            active_prompt = True

            except (sr.WaitTimeoutError, sr.UnknownValueError):
                if active_prompt:
                    active_prompt = False
                continue
            except Exception as e:
                self.bridge.log_emitted.emit(f"[VOICE EXCEPTION]: {e}")
                time.sleep(1)
