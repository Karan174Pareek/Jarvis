from database import db_session

class ChatService:
    @staticmethod
    def get_or_create_active_conversation(user_id: int) -> dict:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations "
                "WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1",
                (user_id,)
            )
            conv = cursor.fetchone()
            if conv:
                return dict(conv)

            # Create default primary conversation
            cursor.execute(
                "INSERT INTO conversations (user_id, title) VALUES (?, ?)",
                (user_id, "Primary Command Channel")
            )
            conv_id = cursor.lastrowid
            cursor.execute("SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?", (conv_id,))
            return dict(cursor.fetchone())

    @staticmethod
    def get_user_conversations(user_id: int) -> list[dict]:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations "
                "WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def create_conversation(user_id: int, title: str = "New Conversation") -> dict:
        title = title.strip() or "New Conversation"
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (user_id, title) VALUES (?, ?)",
                (user_id, title)
            )
            conv_id = cursor.lastrowid
            cursor.execute("SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?", (conv_id,))
            return dict(cursor.fetchone())

    @staticmethod
    def rename_conversation(user_id: int, conversation_id: int, new_title: str) -> bool:
        new_title = new_title.strip()
        if not new_title:
            return False
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = ? AND user_id = ?",
                (new_title, conversation_id, user_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def delete_conversation(user_id: int, conversation_id: int) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM conversations WHERE id = ? AND user_id = ?",
                (conversation_id, user_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def get_messages(user_id: int, conversation_id: int) -> list[dict]:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, conversation_id, sender, text, timestamp FROM messages "
                "WHERE user_id = ? AND conversation_id = ? ORDER BY id ASC",
                (user_id, conversation_id)
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def add_message(user_id: int, conversation_id: int, sender: str, text: str) -> dict:
        text = text.strip()
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (user_id, conversation_id, sender, text) VALUES (?, ?, ?, ?)",
                (user_id, conversation_id, sender, text)
            )
            msg_id = cursor.lastrowid
            
            # Touch conversation updated_at timestamp
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,)
            )

            cursor.execute("SELECT id, conversation_id, sender, text, timestamp FROM messages WHERE id = ?", (msg_id,))
            return dict(cursor.fetchone())

    @staticmethod
    def search_messages(user_id: int, query: str) -> list[dict]:
        query = query.strip()
        if not query:
            return []
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT m.id, m.conversation_id, m.sender, m.text, m.timestamp, c.title as conversation_title "
                "FROM messages m JOIN conversations c ON m.conversation_id = c.id "
                "WHERE m.user_id = ? AND m.text LIKE ? ORDER BY m.id DESC LIMIT 50",
                (user_id, f"%{query}%")
            )
            return [dict(row) for row in cursor.fetchall()]
