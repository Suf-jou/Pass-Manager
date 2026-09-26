# Pass Manager

A small desktop password manager built with Python and Tkinter.

## Features

- Encrypted login storage using Fernet.
- Master-password-based key derivation using Scrypt.
- Add, view, copy, and delete saved logins.
- Generate passwords with configurable length and character types.
- Change the master password and re-encrypt the vault.
- Create a new vault or permanently delete the local database.

## Requirements

- Python 3.11 or newer
- `cryptography`

Install the dependency:

```powershell
pip install cryptography
```

## Run

Start the graphical interface:

```powershell
python GUI.py
```
At first launch type in the master password you want to be set as the master password
Enter the master password when the application starts. Use the vault screen to add and manage login details.

If you forget the master password, use **Delete database** on the unlock screen to permanently remove the encrypted vault and start over. This cannot recover the old logins.

## Storage and security

Login data is stored in `logins.json`. The file is excluded from Git by `.gitignore` and contains encrypted vault data rather than readable passwords.

The master password is never stored. It is used to derive the encryption key when the vault is opened. If the master password is forgotten, the encrypted data cannot be recovered.

This project is intended for learning and personal testing. Review the implementation and threat model before using it for important credentials.
