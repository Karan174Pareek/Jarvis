from database import db_session

class MemoryService:
    @staticmethod
    def save_memory(user_id: int, key: str, value: str, category: str = "general") -> dict:
        key = key.strip()
        value = value.strip()
        if not key or not value:
            return {}

        with db_session() as conn:
            cursor = conn.cursor()
            # Upsert memory key for user
            cursor.execute(
                "SELECT id FROM memories WHERE user_id = ? AND LOWER(key) = LOWER(?)",
                (user_id, key)
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "UPDATE memories SET value = ?, category = ?, created_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (value, category, existing["id"])
                )
                mem_id = existing["id"]
            else:
                cursor.execute(
                    "INSERT INTO memories (user_id, key, value, category) VALUES (?, ?, ?, ?)",
                    (user_id, key, value, category)
                )
                mem_id = cursor.lastrowid

            cursor.execute("SELECT * FROM memories WHERE id = ?", (mem_id,))
            return dict(cursor.fetchone())

    @staticmethod
    def get_memories(user_id: int) -> list[dict]:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM memories WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def delete_memory(user_id: int, memory_id: int) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE id = ? AND user_id = ?", (memory_id, user_id))
            return cursor.rowcount > 0

    @staticmethod
    def clear_all(user_id: int) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
            return cursor.rowcount > 0
