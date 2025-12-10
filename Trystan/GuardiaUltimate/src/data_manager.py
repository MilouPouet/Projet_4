import csv
import os
import json
import shutil
import webbrowser
from datetime import datetime
from typing import List, Dict
from src.security import SecurityService

# CHEMINS ABSOLUS (INCASSABLES)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
DATA_FILE = os.path.join(DATA_DIR, "produits.csv")
USER_FILE = os.path.join(DATA_DIR, "users.json")

class DataManager:
    def __init__(self):
        if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR, exist_ok=True)
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["id", "nom", "prix", "quantite", "categorie", "secret_info"])

    def create_backup(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if os.path.exists(DATA_FILE): shutil.copy2(DATA_FILE, os.path.join(BACKUP_DIR, f"backup_{ts}.csv"))

    def get_all_products(self) -> List[Dict]:
        data = []
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'secret_info' in row and row['secret_info']:
                        row['secret_info'] = SecurityService.decrypt_data(row['secret_info'])
                    data.append(row)
        except FileNotFoundError: pass
        return data

    def get_user_data(self, username) -> Dict:
        if os.path.exists(USER_FILE):
            try:
                with open(USER_FILE, 'r') as f: 
                    users = json.load(f)
                    return users.get(username, None)
            except json.JSONDecodeError: return None
        return None

    # --- NOUVEAU : GESTION CENTRALISÉE DES UTILISATEURS ---
    def register_user(self, username, data):
        """Enregistre un utilisateur de manière sécurisée sans planter."""
        users = {}
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r') as f:
                try: users = json.load(f)
                except: users = {} # Si fichier corrompu, on repart à zéro
        
        users[username] = data
        
        with open(USER_FILE, 'w') as f:
            json.dump(users, f, indent=4)

    def update_user_2fa(self, username, secret):
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r') as f: users = json.load(f)
            if username in users:
                users[username]['2fa_secret'] = secret
                with open(USER_FILE, 'w') as f: json.dump(users, f, indent=4)

    def add_product(self, product: Dict):
        self.create_backup()
        product['id'] = str(int(datetime.now().timestamp()))
        raw_secret = product.get('secret_info', 'Confidentiel')
        product['secret_info'] = SecurityService.encrypt_data(raw_secret)
        
        file_exists = os.path.isfile(DATA_FILE)
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ["id", "nom", "prix", "quantite", "categorie", "secret_info"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists: writer.writeheader()
            writer.writerow(product)

    def delete_product(self, product_id: str):
        self.create_backup()
        rows = []
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        new_rows = [r for r in rows if r['id'] != product_id]
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["id", "nom", "prix", "quantite", "categorie", "secret_info"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_rows)

    def generate_html_report(self):
        products = self.get_all_products()
        total = sum(float(p['prix']) * int(p['quantite']) for p in products)
        html = f"""<html><body style='font-family:sans-serif; padding:20px;'>
        <h1 style='color:#2c3e50;'>Rapport Stock Sécurisé</h1>
        <p>Généré le {datetime.now()}</p>
        <table border='1' cellspacing='0' cellpadding='10' style='border-collapse:collapse; width:100%;'>
        <tr style='background:#34495e; color:white;'><th>Produit</th><th>Prix</th><th>Qté</th><th>Info (Décryptée)</th></tr>"""
        for p in products:
            html += f"<tr><td>{p['nom']}</td><td>{p['prix']}</td><td>{p['quantite']}</td><td>{p.get('secret_info','')}</td></tr>"
        html += f"</table><h3>Total Valorisation: {total:.2f} €</h3></body></html>"
        
        # Correction chemin rapport
        fname = os.path.join(PROJECT_ROOT, "rapport_secure.html")
        with open(fname, "w", encoding='utf-8') as f: f.write(html)
        webbrowser.open('file://' + os.path.realpath(fname))
        return fname
