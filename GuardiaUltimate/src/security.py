import hashlib
import os
import requests
import logging
import re
import pyotp
import qrcode
from cryptography.fernet import Fernet
from datetime import datetime

<<<<<<< HEAD
# --- FIX : CHEMINS ABSOLUS ---
# On récupère le dossier parent de ce fichier (src/..) -> GuardiaUltimate/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "audit.log")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', force=True)

KEY_FILE = os.path.join(PROJECT_ROOT, "secret.key")
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as kf: kf.write(key)
else:
    with open(KEY_FILE, "rb") as kf: key = kf.read()

cipher_suite = Fernet(key)
=======
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "audit.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s', force=True)

KEY_FILE = os.path.join(PROJECT_ROOT, "secret.key")

def get_cipher():
    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as kf:
                key = kf.read()
                if len(key) > 0:
                    return Fernet(key)
        
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as kf:
            kf.write(key)
        return Fernet(key)
    except:
        return Fernet(Fernet.generate_key())

cipher_suite = get_cipher()
>>>>>>> main

class SecurityService:
    @staticmethod
    def log_action(user, action):
<<<<<<< HEAD
        msg = f"USER: {user} | ACTION: {action}"
        print(f"📝 AUDIT: {msg}")
        try: logging.info(msg)
        except: pass

    @staticmethod
    def encrypt_data(data: str) -> str:
        return cipher_suite.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_data(token: str) -> str:
        try: return cipher_suite.decrypt(token.encode()).decode()
        except: return "[DONNÉE ILLISIBLE]"

    @staticmethod
    def generate_2fa_secret(): return pyotp.random_base32()

    @staticmethod
    def get_totp_uri(username, secret):
        return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="Guardia-App")

    @staticmethod
    def verify_2fa_code(secret, code):
        totp = pyotp.totp.TOTP(secret)
        return totp.verify(code)

    @staticmethod
    def check_password_strength(password: str) -> dict:
        score = 0; feedback = []
        if len(password) >= 8: score += 1
        else: feedback.append("Trop court")
        if re.search(r"[A-Z]", password): score += 1
        else: feedback.append("Manque Majuscule")
        if re.search(r"[0-9]", password): score += 1
        else: feedback.append("Manque Chiffre")
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 1
        else: feedback.append("Manque Special Char")
        return {"score": score, "feedback": feedback}

    @staticmethod
    def is_password_pwned(password: str) -> bool:
        sha1_pwd = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_pwd[:5], sha1_pwd[5:]
        try:
            res = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=3)
            return suffix in res.text
        except: return False

    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
        return f"{salt.hex()}:{key.hex()}"

    @staticmethod
    def verify_password(stored_data: str, input_password: str) -> bool:
        try:
            salt_hex, key_hex = stored_data.split(":")
            salt = bytes.fromhex(salt_hex)
            new_key = hashlib.pbkdf2_hmac('sha256', input_password.encode('utf-8'), salt, 100_000)
            return new_key.hex() == key_hex
        except: return False
=======
        try:
            logging.info(f"UTILISATEUR: {user} | ACTION: {action}")
        except:
            pass

    @staticmethod
    def encrypt_data(data: str) -> str:
        try:
            return cipher_suite.encrypt(str(data).encode()).decode()
        except:
            return ""

    @staticmethod
    def decrypt_data(token: str) -> str:
        try:
            return cipher_suite.decrypt(token.encode()).decode()
        except:
            return "[DONNÉE SÉCURISÉE]"

    @staticmethod
    def generate_2fa_secret():
        return pyotp.random_base32()

    @staticmethod
    def get_totp_uri(u, s):
        return pyotp.totp.TOTP(s).provisioning_uri(name=u, issuer_name="Guardia-App")

    @staticmethod
    def verify_2fa_code(s, c):
        if not s or not c:
            return False
        return pyotp.totp.TOTP(s).verify(c, valid_window=1)

    @staticmethod
    def check_password_strength(p):
        s = 0
        f = []
        if len(p) >= 8:
            s += 1
        else:
            f.append("Trop court")
        if re.search(r"[A-Z]", p):
            s += 1
        if re.search(r"[0-9]", p):
            s += 1
        if re.search(r"[!@#$%^&*]", p):
            s += 1
        return {"score": s, "feedback": f}

    @staticmethod
    def is_password_pwned(p):
        try:
            h = hashlib.sha1(p.encode()).hexdigest().upper()
            return h[5:] in requests.get(f"https://api.pwnedpasswords.com/range/{h[:5]}", timeout=2).text
        except:
            return False

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
        except:
            return False
>>>>>>> main
