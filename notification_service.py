from database import db_session

class NotificationService:
    @staticmethod
    def create_notification(user_id: int, title: str, message: str, notification_type: str = "info") -> dict:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notifications (user_id, title, message, type, is_read) VALUES (?, ?, ?, ?, 0)",
                (user_id, title, message, notification_type)
            )
            notif_id = cursor.lastrowid
            cursor.execute("SELECT * FROM notifications WHERE id = ?", (notif_id,))
            return dict(cursor.fetchone())

    @staticmethod
    def get_notifications(user_id: int, unread_only: bool = False) -> list[dict]:
        with db_session() as conn:
            cursor = conn.cursor()
            if unread_only:
                cursor.execute(
                    "SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY id DESC",
                    (user_id,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 50",
                    (user_id,)
                )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def mark_read(user_id: int, notification_id: int) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
                (notification_id, user_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def clear_all(user_id: int) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
            return cursor.rowcount > 0
