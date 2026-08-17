import time
import threading
from datetime import datetime
from database import db_session
from notification_service import NotificationService

class ReminderService:
    @staticmethod
    def create_reminder(user_id: int, title: str, due_at: str, is_recurring: bool = False, pattern: str = "") -> dict:
        title = title.strip()
        if not title:
            return {}
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reminders (user_id, title, due_at, is_recurring, recurrence_pattern, status) "
                "VALUES (?, ?, ?, ?, ?, 'pending')",
                (user_id, title, due_at, 1 if is_recurring else 0, pattern)
            )
            rem_id = cursor.lastrowid
            cursor.execute("SELECT * FROM reminders WHERE id = ?", (rem_id,))
            return dict(cursor.fetchone())

    @staticmethod
    def get_reminders(user_id: int, status: str = None) -> list[dict]:
        with db_session() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    "SELECT * FROM reminders WHERE user_id = ? AND status = ? ORDER BY due_at ASC",
                    (user_id, status)
                )
            else:
                cursor.execute(
                    "SELECT * FROM reminders WHERE user_id = ? ORDER BY due_at ASC",
                    (user_id,)
                )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def mark_completed(user_id: int, reminder_id: int) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE reminders SET status = 'completed' WHERE id = ? AND user_id = ?",
                (reminder_id, user_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def delete_reminder(user_id: int, reminder_id: int) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM reminders WHERE id = ? AND user_id = ?",
                (reminder_id, user_id)
            )
            return cursor.rowcount > 0

    @classmethod
    def check_due_reminders(cls):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, title, due_at FROM reminders WHERE status = 'pending' AND due_at <= ?",
                (now_str,)
            )
            due_list = cursor.fetchall()
            for rem in due_list:
                r_id, u_id, r_title = rem["id"], rem["user_id"], rem["title"]
                # Trigger notification
                NotificationService.create_notification(
                    u_id,
                    title="Reminder Alert",
                    message=f"Reminder due: {r_title}",
                    notification_type="reminder"
                )
                cursor.execute("UPDATE reminders SET status = 'triggered' WHERE id = ?", (r_id,))
                print(f"[REMINDER ENGINE] Triggered reminder '{r_title}' for User {u_id}")

_scheduler_running = False

def start_reminder_scheduler(interval_sec=10):
    global _scheduler_running
    if _scheduler_running:
        return
    _scheduler_running = True

    def loop():
        while _scheduler_running:
            try:
                ReminderService.check_due_reminders()
            except Exception as e:
                print("[REMINDER SCHEDULER ERROR]:", e)
            time.sleep(interval_sec)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    print("[REMINDER SCHEDULER] Background daemon thread active.")
