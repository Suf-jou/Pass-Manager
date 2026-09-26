import cryptography
import secrets
import string

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
