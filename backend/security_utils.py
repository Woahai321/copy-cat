from cryptography.fernet import Fernet
import os
import base64
from typing import Optional

# Generate a key based on an environment variable or a fixed secret for this installation
# In production, this should be a properly managed secret.
# For this app, we'll try to use a persistent key file or fallback to a deterministic key based on a secret.

KEY_FILE = "secret.key"

def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

try:
    _key = load_or_create_key()
    _cipher_suite = Fernet(_key)
except Exception as e:
    print(f"CRITICAL: Failed to initialize encryption key: {e}")
    _cipher_suite = None

def encrypt_value(value: str) -> str:
    """Encrypts a string value."""
    if not value:
        return value
    if _cipher_suite is None:
        raise RuntimeError("Encryption system not initialized")
    
    encrypted_bytes = _cipher_suite.encrypt(value.encode('utf-8'))
    return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')

def decrypt_value(encrypted_value: str) -> str:
    """Decrypts a string value."""
    if not encrypted_value:
        return encrypted_value
    if _cipher_suite is None:
        raise RuntimeError("Encryption system not initialized")
        
    try:
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode('utf-8'))
        decrypted_bytes = _cipher_suite.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return ""
