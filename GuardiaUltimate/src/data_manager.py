import csv
import os
import json
import shutil
import webbrowser
<<<<<<< HEAD
=======
import uuid  # <--- IMPORT IMPORTANT
>>>>>>> main
from datetime import datetime
from typing import List, Dict
from src.security import SecurityService

<<<<<<< HEAD
# CHEMINS ABSOLUS (INCASSABLES)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

=======
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
>>>>>>> main
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
DATA_FILE = os.path.join(DATA_DIR, "produits.csv")
USER_FILE = os.path.join(DATA_DIR, "users.json")
<<<<<<< HEAD

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
=======
ORDER_FILE = os.path.join(DATA_DIR, "orders.json")

class DataManager:
    def __init__(self):
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR, exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(["id", "nom", "prix", "quantite", "categorie", "secret_info"])
        if not os.path.exists(ORDER_FILE):
            with open(ORDER_FILE, 'w') as f:
                json.dump([], f)

    def create_backup(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if os.path.exists(DATA_FILE):
            shutil.copy2(DATA_FILE, os.path.join(BACKUP_DIR, f"back_{ts}.csv"))
>>>>>>> main

    def get_all_products(self) -> List[Dict]:
        data = []
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
<<<<<<< HEAD
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
=======
                    if row.get('secret_info'):
                        row['secret_info'] = SecurityService.decrypt_data(row['secret_info'])
                    data.append(row)
        except:
            pass
        return data

    def get_stock_status(self, pid):
        prods = self.get_all_products()
        # Recherche par ID unique
        p = next((x for x in prods if x['id'] == pid), None)
        if not p:
            return (0, 0, 0)
        try:
            real = int(float(p['quantite']))
        except:
            real = 0
        
        orders = self.get_all_orders()
        res = 0
        for o in orders:
            if o.get('status') == 'PENDING':
                for item in o.get('items', []):
                    if item['id'] == pid:
                        res += int(item['qty'])
        return (real, res, real - res)

    def get_user_data(self, u):
        if os.path.exists(USER_FILE):
            try:
                with open(USER_FILE, 'r') as f:
                    users = json.load(f)
                    d = users.get(u)
                    if isinstance(d, str): 
                        new_data = {"hash":d, "role":"admin", "2fa_secret":None}
                        self.register_user(u, new_data)
                        return new_data
                    return d
            except:
                pass
        return None

    def get_all_users_list(self):
        if os.path.exists(USER_FILE):
            try:
                with open(USER_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def delete_user(self, username):
        if os.path.exists(USER_FILE):
            try:
                with open(USER_FILE, 'r') as f:
                    users = json.load(f)
                if username in users:
                    del users[username]
                    with open(USER_FILE, 'w') as f:
                        json.dump(users, f, indent=4)
                    return True
            except:
                pass
        return False

    def register_user(self, u, data):
        users = {}
        if os.path.exists(USER_FILE):
            try:
                with open(USER_FILE, 'r') as f:
                    users = json.load(f)
            except:
                pass
        users[u] = data
        with open(USER_FILE, 'w') as f:
            json.dump(users, f, indent=4)

    def update_user_2fa(self, u, sec):
        d = self.get_user_data(u)
        if d:
            d['2fa_secret'] = sec
            self.register_user(u, d)

    def change_password(self, u, h):
        d = self.get_user_data(u)
        if d:
            d['hash'] = h
            self.register_user(u, d)
            return True
        return False

    def add_product(self, p):
        self.create_backup()
        # --- FIX UUID : ID UNIQUE GARANTI ---
        p['id'] = str(uuid.uuid4())
        p['secret_info'] = SecurityService.encrypt_data(p.get('secret_info',''))
        exists = os.path.isfile(DATA_FILE)
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=["id","nom","prix","quantite","categorie","secret_info"])
            if not exists: w.writeheader()
            w.writerow(p)

    def delete_product(self, pid):
        self.create_backup()
        rows = self.get_all_products()
        for r in rows:
            r['secret_info'] = SecurityService.encrypt_data(r['secret_info'])
            
        new_rows = [r for r in rows if r['id'] != pid]
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=["id","nom","prix","quantite","categorie","secret_info"])
            w.writeheader()
            w.writerows(new_rows)

    def get_all_orders(self):
        if os.path.exists(ORDER_FILE):
            try:
                with open(ORDER_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def place_order(self, u, cart):
        orders = self.get_all_orders()
        o = {
            "id": f"CMD-{int(datetime.now().timestamp())}", 
            "user": u, 
            "date": datetime.now().strftime("%d/%m/%Y"), 
            "status": "PENDING", 
            "items": cart, 
            "total": sum(x['price']*x['qty'] for x in cart)
        }
        orders.append(o)
        with open(ORDER_FILE, 'w') as f:
            json.dump(orders, f, indent=4)

    def validate_order(self, oid):
        orders = self.get_all_orders()
        t = next((o for o in orders if o['id'] == oid), None)
        if not t or t['status'] != 'PENDING': return False
        
        prods = self.get_all_products()
        for item in t['items']:
            for p in prods:
                if p['id'] == item['id']:
                    try:
                        curr = int(float(p['quantite']))
                        p['quantite'] = max(0, curr - item['qty'])
                    except:
                        pass
        
        self.create_backup()
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=["id","nom","prix","quantite","categorie","secret_info"])
            w.writeheader()
            for p in prods:
                p['secret_info'] = SecurityService.encrypt_data(p['secret_info'])
                w.writerow(p)
                
        t['status'] = "SHIPPED"
        with open(ORDER_FILE, 'w') as f:
            json.dump(orders, f, indent=4)
        return True

    def generate_html_report(self):
        fname = os.path.join(PROJECT_ROOT, "rapport.html")
        with open(fname, 'w', encoding='utf-8') as f:
            f.write("<h1>Rapport de Stock</h1>")
>>>>>>> main
        webbrowser.open('file://' + os.path.realpath(fname))
        return fname
