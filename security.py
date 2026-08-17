import re
import os
from database import db_session

class SecurityService:
    @staticmethod
    def sanitize_input(text: str) -> str:
        if not text:
            return ""
        # Strip script tags and dangerous HTML injections
        cleaned = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r'<[^>]*>', '', cleaned)
        return cleaned.strip()

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        if not filename:
            return "unnamed_file"
        # Prevent directory traversal attacks
        base = os.path.basename(filename)
        cleaned = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
        return cleaned

    @staticmethod
    def log_activity(user_id: int, action: str, details: str = "") -> dict:
        action_clean = SecurityService.sanitize_input(action)
        details_clean = SecurityService.sanitize_input(details)
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO activity_logs (user_id, action, details) VALUES (?, ?, ?)",
                (user_id, action_clean, details_clean)
            )
            log_id = cursor.lastrowid
            cursor.execute("SELECT * FROM activity_logs WHERE id = ?", (log_id,))
            return dict(cursor.fetchone())

    @staticmethod
    def get_user_activity(user_id: int, limit: int = 50) -> list[dict]:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM activity_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
