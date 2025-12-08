import uuid
from src.database import read_csv, append_csv
from src.security import hash_password, verify_password

def register_user(username, password, role="user"):
    # 1. Vérifier si user existe déjà
    users = read_csv("users.csv")
    for user in users:
        if user['username'] == username:
            return False, "Utilisateur déjà existant."

    # 2. Sécuriser le mot de passe
    security_data = hash_password(password)
    
    # 3. Préparer la ligne CSV
    new_user = {
        "user_id": str(uuid.uuid4()),
        "username": username,
        "password_hash": security_data["hash"],
        "salt": security_data["salt"],
        "role": role
    }
    
    # 4. Sauvegarder
    append_csv("users.csv", new_user)
    return True, "Compte créé avec succès (Sécurisé SHA-256)."

def login_user(username, password):
    users = read_csv("users.csv")
    
    for user in users:
        if user['username'] == username:
            # L'utilisateur existe, on vérifie le hash
            if verify_password(user['password_hash'], user['salt'], password):
                return True, user # Succès
            else:
                return False, "Identifiants incorrects" # Même message pour éviter énumération
                
    return False, "Identifiants incorrects"