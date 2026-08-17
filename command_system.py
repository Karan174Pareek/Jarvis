import re
from datetime import datetime, timedelta
from task_service import TaskService
from reminder_service import ReminderService
from notes_service import NotesService
from notification_service import NotificationService

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

# Instantiate registry
registry = CommandRegistry()

# Handlers
def _handle_create_task(user_id: int, title: str, priority: str = "medium", due_date: str = None, category: str = "general"):
    t = TaskService.create_task(user_id, title=title, priority=priority, due_date=due_date, category=category)
    if t:
        return True, f"Task created successfully: '{t['title']}' (ID: {t['id']})"
    return False, "Failed to create task."

def _handle_list_tasks(user_id: int):
    tasks = TaskService.get_tasks(user_id, status="pending")
    if not tasks:
        return True, "You currently have 0 pending tasks."
    formatted = "\n".join([f"• [{t['id']}] {t['title']} (Priority: {t['priority']})" for t in tasks])
    return True, f"Pending Tasks ({len(tasks)}):\n{formatted}"

def _handle_create_reminder(user_id: int, title: str, due_at: str):
    r = ReminderService.create_reminder(user_id, title=title, due_at=due_at)
    if r:
        return True, f"Reminder set: '{r['title']}' scheduled for {r['due_at']}."
    return False, "Failed to create reminder."

def _handle_create_note(user_id: int, title: str, content: str, tags: str = ""):
    n = NotesService.create_note(user_id, title=title, content=content, tags=tags)
    if n:
        return True, f"Note saved: '{n['title']}'."
    return False, "Failed to create note."

def _handle_list_notes(user_id: int):
    notes = NotesService.get_notes(user_id)
    if not notes:
        return True, "Notes vault is currently empty."
    formatted = "\n".join([f"• [{n['id']}] {n['title']}" for n in notes[:10]])
    return True, f"Notes Vault ({len(notes)} items):\n{formatted}"

def _handle_system_status(user_id: int):
    tasks = TaskService.get_tasks(user_id, status="pending")
    notes = NotesService.get_notes(user_id)
    notifs = NotificationService.get_notifications(user_id, unread_only=True)
    return True, f"System Status: OPTIMAL. Active Tasks: {len(tasks)} | Saved Notes: {len(notes)} | Unread Alerts: {len(notifs)}."

# Register default actions
registry.register("create_task", _handle_create_task)
registry.register("list_tasks", _handle_list_tasks)
registry.register("create_reminder", _handle_create_reminder)
registry.register("create_note", _handle_create_note)
registry.register("list_notes", _handle_list_notes)
registry.register("get_system_status", _handle_system_status)


def parse_intent_and_execute(user_id: int, text: str) -> tuple[bool, str]:
    text_lower = text.strip().lower()

    # 1. Task Creation Intent
    if "task:" in text_lower or text_lower.startswith("add task ") or text_lower.startswith("create task "):
        title = text.split(":", 1)[-1].strip() if ":" in text else re.sub(r'^(add|create)\s+task\s+', '', text, flags=re.IGNORECASE).strip()
        if title:
            return registry.dispatch(user_id, "create_task", title=title)

    # 2. Reminder Intent
    if text_lower.startswith("remind me to ") or text_lower.startswith("set reminder "):
        content = re.sub(r'^(remind me to|set reminder)\s+', '', text, flags=re.IGNORECASE).strip()
        due_at = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        if "tomorrow" in content.lower():
            due_at = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 09:00:00")
            content = re.sub(r'\s+tomorrow', '', content, flags=re.IGNORECASE).strip()
        return registry.dispatch(user_id, "create_reminder", title=content, due_at=due_at)

    # 3. Note Creation Intent
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

    # 6. System Status Intent
    if "system status" in text_lower or "telemetry" in text_lower:
        return registry.dispatch(user_id, "get_system_status")

    return False, ""
