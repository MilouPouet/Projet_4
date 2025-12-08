import hashlib
import os
import binascii

def hash_password(password: str) -> dict:
    """
    Hache un mot de passe avec un Salt unique (SHA-256).
    Retourne le hash et le salt pour stockage.
    """
    # 1. Générer un salt aléatoire de 32 bytes (très robuste)
    salt = os.urandom(32)
    
    # 2. Combiner Salt + Password
    pwd_bytes = password.encode('utf-8')
    combined = salt + pwd_bytes
    
    # 3. Hacher
    hashed = hashlib.sha256(combined).hexdigest()
    
    # 4. Convertir le salt en hexadécimal pour stockage CSV
    salt_hex = binascii.hexlify(salt).decode('utf-8')
    
    return {"hash": hashed, "salt": salt_hex}

def verify_password(stored_password: str, stored_salt: str, provided_password: str) -> bool:
    """
    Vérifie si le mot de passe fourni correspond au hash stocké.
    """
    try:
        # Reconvertir le salt hex en bytes
        salt = binascii.unhexlify(stored_salt)
        
        # Refaire exactement le même processus
        pwd_bytes = provided_password.encode('utf-8')
        combined = salt + pwd_bytes
        new_hash = hashlib.sha256(combined).hexdigest()
        
        # Comparaison (En prod, on utiliserait hmac.compare_digest pour éviter les timing attacks)
        return new_hash == stored_password
    except Exception as e:
        print(f"Erreur crypto: {e}")
        return False