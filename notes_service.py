from database import db_session

class NotesService:
    @staticmethod
    def create_note(user_id: int, title: str, content: str = "", tags: str = "") -> dict:
        title = title.strip()
        if not title:
            return {}
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (user_id, title, content, tags) VALUES (?, ?, ?, ?)",
                (user_id, title, content, tags)
            )
            note_id = cursor.lastrowid
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            return dict(cursor.fetchone())

    @staticmethod
    def get_notes(user_id: int) -> list[dict]:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM notes WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def update_note(user_id: int, note_id: int, title: str, content: str, tags: str = "") -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notes SET title = ?, content = ?, tags = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = ? AND user_id = ?",
                (title, content, tags, note_id, user_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def delete_note(user_id: int, note_id: int) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM notes WHERE id = ? AND user_id = ?",
                (note_id, user_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def search_notes(user_id: int, query: str) -> list[dict]:
        query = query.strip()
        if not query:
            return []
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM notes WHERE user_id = ? AND (title LIKE ? OR content LIKE ? OR tags LIKE ?) "
                "ORDER BY updated_at DESC",
                (user_id, f"%{query}%", f"%{query}%", f"%{query}%")
            )
            return [dict(row) for row in cursor.fetchall()]
