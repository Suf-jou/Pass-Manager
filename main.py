from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import base64
import json
import os
from pathlib import Path
import secrets
import string

LOGIN_FILE = Path(__file__).with_name("logins.json")


def generate_password(length=12, include_special_chars=True, include_numbers=True, include_uppercase=True):
    """Generate a secure random password."""
    characters = ""
    if include_uppercase:
        characters += string.ascii_uppercase
    characters += string.ascii_lowercase
    if include_numbers:
        characters += string.digits
    if include_special_chars:
        characters += string.punctuation

    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

def hash_password(password):

    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(password.encode('utf-8'))
    return digest.finalize().hex()

def _derive_key(master_password, salt):
    """Derive an encryption key from the master password and salt."""
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))


def _load_logins(master_password):
    if not LOGIN_FILE.exists():
        return []

    with LOGIN_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if "salt" not in data:
        if data.get("logins") == []:
            return []
        raise ValueError("The existing login file is not encrypted.")

    salt = base64.urlsafe_b64decode(data["salt"])
    key = _derive_key(master_password, salt)

    try:
        decrypted = Fernet(key).decrypt(data["vault"]).decode("utf-8")
    except InvalidToken as error:
        raise ValueError("Incorrect master password.") from error

    return json.loads(decrypted).get("logins", [])


def _save_logins(logins, master_password):
    salt = os.urandom(16)
    key = _derive_key(master_password, salt)
    encrypted_vault = Fernet(key).encrypt(
        json.dumps({"logins": logins}).encode("utf-8")
    )

    with LOGIN_FILE.open("w", encoding="utf-8") as file:
        json.dump({
            "salt": base64.urlsafe_b64encode(salt).decode("ascii"),
            "vault": encrypted_vault.decode("ascii"),
        }, file, indent=2)
        file.write("\n")


def create_vault(master_password):
    """Create an empty encrypted vault with a new master password."""
    if LOGIN_FILE.exists():
        raise FileExistsError("A login vault already exists.")
    _save_logins([], master_password)


def delete_vault():
    """Delete the local encrypted vault."""
    if LOGIN_FILE.exists():
        LOGIN_FILE.unlink()


def encrypt_login_info(username, password, master_password):
    
    logins = _load_logins(master_password)
    logins.append({"username": username, "password": password})
    _save_logins(logins, master_password)


def store_login_info(username, password, master_password):
    
    encrypt_login_info(username, password, master_password)


def get_login_info(username, master_password):
    """Return a decrypted login by username."""
    for login in _load_logins(master_password):
        if login["username"] == username:
            return login


def get_all_logins(master_password):
    
    return _load_logins(master_password)

def delete_login_info(username, master_password):
    logins = _load_logins(master_password)
    logins = [login for login in logins if login["username"] != username]
    _save_logins(logins, master_password)

def change_master_password(old_master_password, new_master_password):



    logins = _load_logins(old_master_password)
    _save_logins(logins, new_master_password)

