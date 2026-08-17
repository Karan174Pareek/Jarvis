import hashlib
import os
import secrets
from datetime import datetime, timedelta
from database import db_session, init_db

class AuthService:
    @staticmethod
    def _hash_password(password: str, salt_bytes: bytes = None) -> tuple[str, str]:
        if salt_bytes is None:
            salt_bytes = os.urandom(16)
        salt_hex = salt_bytes.hex()
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_bytes,
            100000
        )
        return key.hex(), salt_hex

    @classmethod
    def register_user(cls, username: str, email: str, password: str, pin: str = "1234") -> tuple[bool, str, dict]:
        username = username.strip()
        email = email.strip().lower()

        if not username or not email or not password:
            return False, "Username, email, and password are required.", {}

        if len(password) < 4:
            return False, "Password must be at least 4 characters.", {}

        with db_session() as conn:
            cursor = conn.cursor()
            # Check existing username or email
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return False, "Username or Email already registered.", {}

            pwd_hash, salt_hex = cls._hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, salt, security_pin) VALUES (?, ?, ?, ?, ?)",
                (username, email, pwd_hash, salt_hex, pin)
            )
            user_id = cursor.lastrowid

            # Initialize default user settings
            cursor.execute(
                "INSERT INTO user_settings (user_id, assistant_name) VALUES (?, ?)",
                (user_id, "Jarvis")
            )

            user_data = {"id": user_id, "username": username, "email": email}
            return True, "User registered successfully.", user_data

    @classmethod
    def authenticate_user(cls, username_or_email: str, password: str) -> tuple[bool, str, dict]:
        query_val = username_or_email.strip().lower()
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, email, password_hash, salt, security_pin FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
                (query_val, query_val)
            )
            user = cursor.fetchone()
            if not user:
                return False, "Invalid credentials.", {}

            user_id, username, email, stored_hash, salt_hex, pin = user["id"], user["username"], user["email"], user["password_hash"], user["salt"], user["security_pin"]
            salt_bytes = bytes.fromhex(salt_hex)
            computed_hash, _ = cls._hash_password(password, salt_bytes)

            if computed_hash == stored_hash:
                token = secrets.token_hex(24)
                expires_at = (datetime.now() + timedelta(days=7)).isoformat()
                cursor.execute(
                    "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
                    (user_id, token, expires_at)
                )
                user_data = {
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "token": token,
                    "security_pin": pin
                }
                return True, "Authentication successful.", user_data
            else:
                return False, "Invalid credentials.", {}

    @classmethod
    def validate_session(cls, token: str) -> tuple[bool, dict]:
        if not token:
            return False, {}
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT u.id, u.username, u.email, u.security_pin, s.expires_at "
                "FROM sessions s JOIN users u ON s.user_id = u.id "
                "WHERE s.token = ?",
                (token,)
            )
            session = cursor.fetchone()
            if not session:
                return False, {}

            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.now() > expires_at:
                cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
                return False, {}

            return True, {
                "id": session["id"],
                "username": session["username"],
                "email": session["email"],
                "security_pin": session["security_pin"]
            }

    @classmethod
    def get_or_create_default_user(cls) -> dict:
        """Ensure a default primary user exists for desktop single-user mode."""
        init_db()
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, security_pin FROM users ORDER BY id ASC LIMIT 1")
            user = cursor.fetchone()
            if user:
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "security_pin": user["security_pin"]
                }
        
        # Create default primary user "Sir"
        success, msg, user_data = cls.register_user("Sir", "sir@jarvis.local", "1234", "1234")
        if success:
            return user_data
        
        # Fallback check
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, security_pin FROM users LIMIT 1")
            u = cursor.fetchone()
            return {"id": u["id"], "username": u["username"], "email": u["email"], "security_pin": u["security_pin"]}
