import hashlib
import secrets
import time


class SessionManager:
    def __init__(self, expiry=600):
        self.sessions = {}
        self.expiry = expiry

    def create(self, user_id):
        session_id = secrets.token_hex(32)
        self.sessions[session_id] = {"user_id": user_id, "created_at": time.time()}
        return session_id

    def validate(self, session_id):
        session = self.sessions.get(session_id)

        if not session:
            return None

        if (time.time() - session["created_at"]) > self.expiry:
            self.terminate(session_id)
            return None

        return session["user_id"]

    def terminate(self, session_id):
        self.sessions.pop(session_id, None)


def hash_password(password):
    # Get random salt
    salt = secrets.token_bytes(16)

    # Hash password+salt. (params taken from IETF RFC7914)
    hashed = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)

    # Return both hash, and salt so password can be verified later
    return f"{salt.hex()}:{hashed.hex()}"


def verify_password(password, stored):
    salt_hex, hashed_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)

    hashed = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)

    return hashed.hex() == hashed_hex
