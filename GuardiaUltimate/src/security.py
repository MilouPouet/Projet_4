import hashlib
import os
import requests
import logging
import re
import pyotp
import qrcode
from cryptography.fernet import Fernet
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(filename=os.path.join(LOG_DIR, "audit.log"), level=logging.INFO, format='%(asctime)s - %(message)s', force=True)

KEY_FILE = os.path.join(PROJECT_ROOT, "secret.key")

def get_cipher():
    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as kf: return Fernet(kf.read())
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as kf: kf.write(key)
        return Fernet(key)
    except: return Fernet(Fernet.generate_key())

cipher_suite = get_cipher()

class SecurityService:
    @staticmethod
    def log_action(user, action): logging.info(f"USER: {user} | ACTION: {action}")
    @staticmethod
    def encrypt_data(data: str) -> str: return cipher_suite.encrypt(str(data).encode()).decode()
    @staticmethod
    def decrypt_data(token: str) -> str: 
        try: return cipher_suite.decrypt(token.encode()).decode()
        except: return ""
    @staticmethod
    def generate_2fa_secret(): return pyotp.random_base32()
    @staticmethod
    def get_totp_uri(u, s): return pyotp.totp.TOTP(s).provisioning_uri(name=u, issuer_name="Guardia")
    @staticmethod
    def verify_2fa_code(s, c): return pyotp.totp.TOTP(s).verify(c, valid_window=1) if s and c else False
    @staticmethod
    def is_password_pwned(p):
        try:
            h = hashlib.sha1(p.encode()).hexdigest().upper()
            return h[5:] in requests.get(f"https://api.pwnedpasswords.com/range/{h[:5]}", timeout=2).text
        except: return False
    @staticmethod
    def hash_password(p):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', p.encode(), salt, 100000)
        return f"{salt.hex()}:{key.hex()}"
    @staticmethod
    def verify_password(stored, input_p):
        try:
            salt, key = stored.split(":")
            return hashlib.pbkdf2_hmac('sha256', input_p.encode(), bytes.fromhex(salt), 100000).hex() == key
        except: return False
