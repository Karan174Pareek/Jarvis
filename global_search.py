from database import db_session
from chat_service import ChatService
from task_service import TaskService
from notes_service import NotesService
from file_service import FileService

class GlobalSearch:
    @staticmethod
    def search_all(user_id: int, query: str) -> dict:
        query = query.strip()
        if not query:
            return {"messages": [], "tasks": [], "notes": [], "files": [], "memories": []}

        messages = ChatService.search_messages(user_id, query)
        tasks = TaskService.search_tasks(user_id, query)
        notes = NotesService.search_notes(user_id, query)
        files = FileService.search_documents(user_id, query)

        memories = []
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM memories WHERE user_id = ? AND (key LIKE ? OR value LIKE ?) ORDER BY created_at DESC",
                (user_id, f"%{query}%", f"%{query}%")
            )
            memories = [dict(row) for row in cursor.fetchall()]

        return {
            "messages": messages,
            "tasks": tasks,
            "notes": notes,
            "files": files,
            "memories": memories
        }
