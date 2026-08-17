import os
import shutil
from database import db_session

BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis-data")

class FileService:
    @staticmethod
    def _get_user_dir(user_id: int) -> str:
        user_dir = os.path.join(BASE_DATA_DIR, "users", str(user_id), "files")
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return user_dir

    @classmethod
    def save_file(cls, user_id: int, filename: str, content_bytes: bytes) -> dict:
        filename = os.path.basename(filename).strip()
        if not filename:
            return {}

        user_dir = cls._get_user_dir(user_id)
        file_path = os.path.join(user_dir, filename)

        # Write file
        with open(file_path, "wb") as f:
            f.write(content_bytes)

        file_size = len(content_bytes)
        ext = os.path.splitext(filename)[1].lower()

        # Extract text content if plain text file
        indexed_text = ""
        if ext in [".txt", ".md", ".json", ".csv", ".py", ".html", ".css", ".js", ".log"]:
            try:
                indexed_text = content_bytes.decode("utf-8", errors="ignore")[:10000] # First 10k chars
            except Exception:
                pass

        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO file_records (user_id, filename, file_path, file_type, file_size, indexed_text) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, filename, file_path, ext, file_size, indexed_text)
            )
            rec_id = cursor.lastrowid
            cursor.execute("SELECT * FROM file_records WHERE id = ?", (rec_id,))
            return dict(cursor.fetchone())

    @classmethod
    def import_local_file(cls, user_id: int, source_path: str) -> dict:
        if not os.path.exists(source_path):
            return {}
        filename = os.path.basename(source_path)
        with open(source_path, "rb") as f:
            content = f.read()
        return cls.save_file(user_id, filename, content)

    @classmethod
    def get_files(cls, user_id: int) -> list[dict]:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM file_records WHERE user_id = ? ORDER BY uploaded_at DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def delete_file(cls, user_id: int, file_id: int) -> bool:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM file_records WHERE id = ? AND user_id = ?", (file_id, user_id))
            row = cursor.fetchone()
            if not row:
                return False

            path = row["file_path"]
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

            cursor.execute("DELETE FROM file_records WHERE id = ? AND user_id = ?", (file_id, user_id))
            return cursor.rowcount > 0

    @classmethod
    def search_documents(cls, user_id: int, query: str) -> list[dict]:
        query = query.strip()
        if not query:
            return []
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM file_records WHERE user_id = ? AND (filename LIKE ? OR indexed_text LIKE ?) "
                "ORDER BY uploaded_at DESC",
                (user_id, f"%{query}%", f"%{query}%")
            )
            return [dict(row) for row in cursor.fetchall()]
