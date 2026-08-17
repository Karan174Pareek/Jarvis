from database import db_session

class TaskService:
    @staticmethod
    def create_task(user_id: int, title: str, description: str = "", priority: str = "medium", due_date: str = None, category: str = "general") -> dict:
        title = title.strip()
        if not title:
            return {}
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (user_id, title, description, priority, status, due_date, category) "
                "VALUES (?, ?, ?, ?, 'pending', ?, ?)",
                (user_id, title, description, priority, due_date, category)
            )
            task_id = cursor.lastrowid
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            return dict(cursor.fetchone())

    @staticmethod
    def get_tasks(user_id: int, status: str = None) -> list[dict]:
        with db_session() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    "SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY id DESC",
                    (user_id, status)
                )
            else:
                cursor.execute(
                    "SELECT * FROM tasks WHERE user_id = ? ORDER BY id DESC",
                    (user_id,)
                )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def update_task_status(user_id: int, task_id: int, status: str) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?",
                (status, task_id, user_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def delete_task(user_id: int, task_id: int) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def search_tasks(user_id: int, query: str) -> list[dict]:
        query = query.strip()
        if not query:
            return []
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE user_id = ? AND (title LIKE ? OR description LIKE ?) ORDER BY id DESC",
                (user_id, f"%{query}%", f"%{query}%")
            )
            return [dict(row) for row in cursor.fetchall()]
