import csv
import os
import json
import shutil
import webbrowser
import uuid
from datetime import datetime, timedelta
from typing import List, Dict
from src.security import SecurityService

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
DATA_FILE = os.path.join(DATA_DIR, "produits.csv")
USER_FILE = os.path.join(DATA_DIR, "users.json")
ORDER_FILE = os.path.join(DATA_DIR, "orders.json")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")

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
        if not os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'w') as f:
                json.dump({}, f)

    def create_backup(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if os.path.exists(DATA_FILE):
            shutil.copy2(DATA_FILE, os.path.join(BACKUP_DIR, f"back_{ts}.csv"))

    def record_daily_stock(self):
        today = datetime.now().strftime("%Y-%m-%d")
        total_qty = sum(int(float(p['quantite'])) for p in self.get_all_products())
        stats = {}
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, 'r') as f:
                    stats = json.load(f)
            except:
                pass
        stats[today] = total_qty
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=4)

    def get_stock_history(self):
        self.record_daily_stock()
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def get_sales_per_day(self):
        orders = self.get_all_orders()
        sales_raw = {}
        for o in orders:
            raw_date = o['date']
            try:
                date_obj = datetime.strptime(raw_date, "%d/%m/%Y")
                fmt_date = date_obj.strftime("%Y-%m-%d")
                qty = sum(int(item['qty']) for item in o['items'])
                sales_raw[fmt_date] = sales_raw.get(fmt_date, 0) + qty
            except:
                continue
        
        if not sales_raw: return {}
        sorted_dates = sorted(sales_raw.keys())
        start = datetime.strptime(sorted_dates[0], "%Y-%m-%d")
        end = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")
        sales_full = {}
        delta = end - start
        for i in range(delta.days + 1):
            day = (start + timedelta(days=i)).strftime("%Y-%m-%d")
            sales_full[day] = sales_raw.get(day, 0)
        return sales_full

    def get_top_products(self):
        orders = self.get_all_orders()
        counts = {}
        for o in orders:
            for item in o['items']:
                name = item['nom']
                qty = int(item['qty'])
                counts[name] = counts.get(name, 0) + qty
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]

    def get_all_products(self) -> List[Dict]:
        data = []
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('secret_info'):
                        row['secret_info'] = SecurityService.decrypt_data(row['secret_info'])
                    data.append(row)
        except:
            pass
        return data

    def get_stock_status(self, pid):
        prods = self.get_all_products()
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
        p['id'] = str(uuid.uuid4())
        p['secret_info'] = SecurityService.encrypt_data(p.get('secret_info',''))
        exists = os.path.isfile(DATA_FILE)
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=["id","nom","prix","quantite","categorie","secret_info"])
            if not exists: w.writeheader()
            w.writerow(p)
        self.record_daily_stock()

    def update_product_data(self, product_id, new_data):
        self.create_backup()
        rows = self.get_all_products()
        updated = False
        for r in rows:
            if r['id'] == product_id:
                r.update(new_data)
                updated = True
                break
        if updated:
            with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=["id","nom","prix","quantite","categorie","secret_info"])
                w.writeheader()
                for r in rows:
                    r_save = r.copy()
                    r_save['secret_info'] = SecurityService.encrypt_data(r['secret_info'])
                    w.writerow(r_save)
            self.record_daily_stock()
            return True
        return False

    def adjust_stock(self, product_id, delta):
        self.create_backup()
        rows = self.get_all_products()
        updated = False
        for r in rows:
            if r['id'] == product_id:
                try:
                    current = int(float(r['quantite']))
                    new_qty = max(0, current + delta)
                    r['quantite'] = new_qty
                    updated = True
                except: pass
                break
        if updated:
            with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=["id","nom","prix","quantite","categorie","secret_info"])
                w.writeheader()
                for r in rows:
                    r_save = r.copy()
                    r_save['secret_info'] = SecurityService.encrypt_data(r['secret_info'])
                    w.writerow(r_save)
            self.record_daily_stock()
            return True
        return False

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
        self.record_daily_stock()

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
        
        self.record_daily_stock()
        return True

    def generate_html_report(self):
        fname = os.path.join(PROJECT_ROOT, "rapport.html")
        with open(fname, 'w', encoding='utf-8') as f:
            f.write("<h1>Rapport de Stock</h1>")
        webbrowser.open('file://' + os.path.realpath(fname))
        return fname
