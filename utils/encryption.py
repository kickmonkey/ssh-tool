from cryptography.fernet import Fernet

def get_or_create_key(filepath='.ssh_key'):
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(filepath, 'wb') as f:
            f.write(key)
        return key

def encrypt(text: str, key: bytes) -> str:
    cipher = Fernet(key)
    return cipher.encrypt(text.encode()).decode()

def decrypt(token: str, key: bytes) -> str:
    cipher = Fernet(key)
    return cipher.decrypt(token.encode()).decode()
