import hashlib


def anonymize_email(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()
