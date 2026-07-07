import hashlib
import secrets

"""
This is only here for the db seeding. It's not used for anythin else
"""


def hash_password(password):
    # Get random salt
    salt = secrets.token_bytes(16)

    # Hash password+salt. (params taken from IETF RFC7914)
    hashed = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)

    # Return both hash, and salt so password can be verified later
    return f"{salt.hex()}:{hashed.hex()}"
