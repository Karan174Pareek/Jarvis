import re
import json
from datetime import datetime, timedelta

class CommandRegistry:
    def __init__(self):
        self.handlers = {}

    def register(self, action_name: str, handler_func):
        self.handlers[action_name] = handler_func

    def dispatch(self, user_id: int, action_name: str, **kwargs):
        if action_name not in self.handlers:
            return False, f"Unknown action: '{action_name}'"
        try:
            return self.handlers[action_name](user_id, **kwargs)
        except Exception as e:
            return False, f"Action execution error ({action_name}): {str(e)}"


# Singleton Global Command Dispatcher
registry = CommandRegistry()

def parse_intent_and_execute(user_id: int, text: str) -> tuple[bool, str]:
    text_lower = text.strip().lower()

    # 1. Task Creation Intent: "remind me to submit report tomorrow" or "task: buy supplies" or "add task ..."
    if "task:" in text_lower or text_lower.startswith("add task ") or text_lower.startswith("create task "):
        title = text.split(":", 1)[-1].strip() if ":" in text else re.sub(r'^(add|create)\s+task\s+', '', text, flags=re.IGNORECASE).strip()
        if title:
            return registry.dispatch(user_id, "create_task", title=title)

    # 2. Reminder Intent: "remind me to <title> at/in/tomorrow"
    if text_lower.startswith("remind me to ") or text_lower.startswith("set reminder "):
        content = re.sub(r'^(remind me to|set reminder)\s+', '', text, flags=re.IGNORECASE).strip()
        due_at = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        if "tomorrow" in content.lower():
            due_at = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 09:00:00")
            content = re.sub(r'\s+tomorrow', '', content, flags=re.IGNORECASE).strip()
        return registry.dispatch(user_id, "create_reminder", title=content, due_at=due_at)

    # 3. Note Creation Intent: "note: <content>" or "save note <content>"
    if text_lower.startswith("note:") or text_lower.startswith("add note ") or text_lower.startswith("save note "):
        content = text.split(":", 1)[-1].strip() if ":" in text else re.sub(r'^(add|save)\s+note\s+', '', text, flags=re.IGNORECASE).strip()
        if content:
            title = content[:30] + ("..." if len(content) > 30 else "")
            return registry.dispatch(user_id, "create_note", title=title, content=content)

    # 4. List Tasks Intent
    if "list tasks" in text_lower or "show tasks" in text_lower or "my tasks" in text_lower:
        return registry.dispatch(user_id, "list_tasks")

    # 5. List Notes Intent
    if "list notes" in text_lower or "show notes" in text_lower or "my notes" in text_lower:
        return registry.dispatch(user_id, "list_notes")

    # 6. Memory Storage Intent: "remember that <key> is <value>"
    if "remember that " in text_lower and " is " in text_lower:
        match = re.search(r'remember that (.+?) is (.+)', text, re.IGNORECASE)
        if match:
            key, val = match.group(1).strip(), match.group(2).strip()
            return registry.dispatch(user_id, "save_memory", key=key, value=val)

    # 7. System Status Intent
    if "system status" in text_lower or "telemetry" in text_lower:
        return registry.dispatch(user_id, "get_system_status")

    # Default fallback: Unhandled command (passes to standard conversational AI engine)
    return False, ""
