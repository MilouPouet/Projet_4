import hashlib
import requests

def check_password_leak(password):
    """
    Vérifie si le mot de passe est dans la base de données des fuites.
    Retourne: (True, count) si compromis, (False, 0) si sûr.
    """
    # 1. Hachage SHA-1 (Requis par l'API Pwned Passwords)
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    
    # 2. K-Anonymity : On sépare les 5 premiers chars (prefix) du reste (suffix)
    prefix = sha1_password[:5]
    suffix = sha1_password[5:]
    
    # 3. Appel API (On envoie seulement les 5 chars)
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        # 4. Vérifier si notre suffixe est dans la liste retournée
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                return True, int(count) # Aie, trouvé !
                
        return False, 0 # Ouf, pas trouvé.
        
    except requests.exceptions.RequestException as e:
        print(f"[WARN] API inaccessible, vérification ignorée: {e}")
        return False, 0 # En cas de panne internet, on laisse passer (Fail open)