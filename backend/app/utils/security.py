from cryptography.fernet import Fernet
import base64
import hashlib

# derive key from password
def generate_key(password: str) -> bytes:
    hashed = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

def encrypt_data(data: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(token: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()