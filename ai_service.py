import json
import requests

class AIService:
    @staticmethod
    def generate_response(prompt: str, context_history: list = None, api_key: str = "", assistant_name: str = "Jarvis", user_name: str = "Sir") -> str:
        prompt_clean = prompt.strip()
        if not prompt_clean:
            return "Standing by, sir."

        system_instruction = (
            f"You are {assistant_name}, a highly intelligent, polite, and loyal AI assistant "
            f"(inspired by Tony Stark's JARVIS). Address the user as '{user_name}'. "
            f"Keep responses concise, human-like, helpful, and professional."
        )

        # 1. Try Gemini API if key provided
        if api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                
                contents = []
                # System prompt
                contents.append({"role": "user", "parts": [{"text": system_instruction}]})
                contents.append({"role": "model", "parts": [{"text": f"Understood, {user_name}. How may I assist you?"}]})
                
                # Context history
                if context_history:
                    for msg in context_history[-10:]: # last 10 messages for context window
                        role = "user" if msg.get("sender") == "user" else "model"
                        contents.append({"role": role, "parts": [{"text": msg.get("text", "")}]})

                contents.append({"role": "user", "parts": [{"text": prompt_clean}]})
                
                response = requests.post(url, headers=headers, json={"contents": contents}, timeout=8).json()
                if "candidates" in response and response["candidates"]:
                    text = response["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text:
                        return text
            except Exception as e:
                print(f"[AI SERVICE] Gemini API request error: {e}")

        # 2. Local intelligent response engine (Fallback)
        lower_p = prompt_clean.lower()
        if "who are you" in lower_p or "identify" in lower_p:
            return f"I am {assistant_name} — Just A Rather Very Intelligent System. Your autonomous personal AI operating assistant."

        if "hello" in lower_p or "hi" in lower_p or "hey" in lower_p:
            return f"Greetings, {user_name}. All primary subsystems are optimal. How can I assist you today?"

        return f"Acknowledged, {user_name}. Processing request: '{prompt_clean}'."
