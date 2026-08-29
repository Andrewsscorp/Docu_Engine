import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# We need a 32-url-safe-base64-encoded key
# If not present in ENV, use a static fallback for local dev.
ENCRYPTION_KEY = os.getenv("MESSAGES_ENCRYPTION_KEY", "uO_v0jW9R0yE6q2WJ_r1U0Z8D-Y_c4G8Q-s8mXvX7Yw=")

try:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode('utf-8'))
except ValueError:
    # If key is invalid, generate one on the fly (will break persistence across restarts if not saved)
    cipher_suite = Fernet(Fernet.generate_key())

def encrypt_message(text: str) -> str:
    if not text:
        return text
    encrypted_text = cipher_suite.encrypt(text.encode('utf-8'))
    return encrypted_text.decode('utf-8')

def decrypt_message(cipher_text: str) -> str:
    if not cipher_text:
        return cipher_text
    try:
        decrypted_text = cipher_suite.decrypt(cipher_text.encode('utf-8'))
        return decrypted_text.decode('utf-8')
    except Exception:
        # If decryption fails, it might be an old unencrypted message (plaintext)
        return cipher_text
