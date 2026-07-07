import time
from bas_server.auth import hash_password, verify_password, SessionManager


## Hash
# Correct passwords
def test_correct_password_verifies():
    stored = hash_password("password1")
    assert verify_password("password1", stored)

    stored = hash_password("topsecret")
    assert verify_password("topsecret", stored)


# Incorrect passwords
def test_wrong_password_fails():
    stored = hash_password("password1")
    assert not verify_password("PASSWORD1", stored)

    stored = hash_password("topsecret")
    assert not verify_password("password1", stored)


# Salts
def test_different_hashes_per_call():
    p1 = hash_password("password1")
    p2 = hash_password("password1")
    assert p1 != p2

    p3 = hash_password("topsecret")
    p4 = hash_password("topsecret")
    assert p3 != p4


## Sessions
def test_expired_session():
    sessions = SessionManager(expiry=1) 
    session_id = sessions.create("user1")
    time.sleep(1.1)
    assert sessions.validate(session_id) is None

def test_create_is_string():
    sessions = SessionManager()
    session_id = sessions.create("user1")
    assert isinstance(session_id, str)

def test_validate_user_id():
    sessions = SessionManager()
    session_id = sessions.create("user1")
    assert sessions.validate(session_id) == "user1"

def test_validate_invalid():
    sessions = SessionManager()
    assert sessions.validate("thisisdefinitelyarealsessionidtrustme") is None

def test_terminate():
    sessions = SessionManager()
    session_id = sessions.create("user1")
    assert sessions.validate(session_id) == "user1"
    sessions.terminate(session_id)
    assert sessions.validate(session_id) is None