

from db.mongo import users_collection
import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _check_db() -> tuple[bool, str]:
    """Return (ok, error_message) — centralises the None guard."""
    if users_collection is None:
        return False, "Database unavailable. Please check MongoDB connection."
    return True, ""


def login_user(username: str, password: str) -> tuple[bool, str]:
    ok, err = _check_db()
    if not ok:
        return False, err

    try:
        if not username or not password:
            return False, "Username and password are required."

        user = users_collection.find_one({"username": username})
        if not user:
            return False, "User not found."

        if user["password"] == hash_password(password):
            return True, "Login successful"

        return False, "Incorrect password."

    except Exception as exc:
        return False, f"Login error: {str(exc)[:120]}"


def create_user(username: str, email: str, password: str) -> tuple[bool, str]:
    ok, err = _check_db()
    if not ok:
        return False, err

    try:
        if not username or not email or not password:
            return False, "All fields are required."

        if users_collection.find_one({"username": username}):
            return False, "Username already exists."

        if users_collection.find_one({"email": email}):
            return False, "Email already registered."

        users_collection.insert_one(
            {
                "username": username,
                "email": email,
                "password": hash_password(password),
            }
        )
        return True, "Account created successfully! You can now log in."

    except Exception as exc:
        return False, f"Signup error: {str(exc)[:120]}"