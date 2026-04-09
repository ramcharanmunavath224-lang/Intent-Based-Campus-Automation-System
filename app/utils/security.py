import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password, hashed_password):
    return hash_password(plain_password) == hashed_password