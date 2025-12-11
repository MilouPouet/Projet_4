import os
import json
import random
import sys
from datetime import datetime, timedelta

# Import pour hasher les mots de passe
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.security import SecurityService
from src.data_manager import DataManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")

# Catalogue Wanhao
CATALOGUE = [
    {"nom": "Wanhao Duplicator 12/230 (Mono)", "prix": 229.0},
    {"nom": "Wanhao Duplicator 12/230 (Dual)", "prix": 269.0},
    {"nom": "Wanhao D12/300 Pro Max", "prix": 399.0},
    {"nom": "Filament PLA+ Blanc 1kg", "prix": 22.90},
    {"nom": "Filament PETG Noir", "prix": 24.90}
]

# CLIENTS A CRÉER (Nom d'utilisateur, Mot de passe)
CLIENTS_DATA = {
    "LaraClette": "12345678",
    "AlainTerieur": "12345678",
    "SarahCroche": "12345678",
    "DaisyDrate": "12345678",
    "GerardMensoif": "12345678",
    "EllaDanlos": "12345678",
    "JerryGolay": "12345678",
    "NordineAteur": "12345678",
    "SandraNicouette": "12345678",
    "TheoPhile": "12345678",
    "VincentTime": "12345678",
    "AudeJavel": "12345678",
    "JeanBonneau": "12345678",
    "PhilDefer": "12345678"
}

def generate():
    print("⏳ Création des comptes utilisateurs & Historique...")
    db = DataManager()
    
    # 1. CRÉATION DES COMPTES
    for username, password in CLIENTS_DATA.items():
        if not db.get_user_data(username):
            hashed = SecurityService.hash_password(password)
            db.register_user(username, {"hash": hashed, "role": "client", "2fa_secret": None})
            print(f"👤 Compte créé : {username} (MDP: {password})")

    # 2. GÉNÉRATION COMMANDES
    orders = []
    stats = {}
    current_stock_total = 500
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    for i in range(31):
        current_day = start_date + timedelta(days=i)
        date_str_orders = current_day.strftime("%d/%m/%Y")
        date_str_stats = current_day.strftime("%Y-%m-%d")

        nb_orders = random.randint(0, 4)
        if current_day.weekday() >= 5: nb_orders += random.randint(1, 3)

        daily_sold_qty = 0

        for _ in range(nb_orders):
            cart = []
            nb_items = random.randint(1, 3)
            for _ in range(nb_items):
                prod = random.choice(CATALOGUE)
                qty = random.randint(1, 2)
                item = {
                    "id": "fictif_hist",
                    "nom": prod["nom"],
                    "qty": qty,
                    "price": prod["prix"]
                }
                cart.append(item)
                daily_sold_qty += qty

            # On prend un vrai client de la liste
            client_name = random.choice(list(CLIENTS_DATA.keys()))
            
            order = {
                "id": f"CMD-{int(current_day.timestamp())}-{random.randint(10,99)}",
                "user": client_name,
                "date": date_str_orders,
                "status": "SHIPPED",
                "items": cart,
                "total": sum(x['price']*x['qty'] for x in cart)
            }
            orders.append(order)

        if random.random() > 0.8: 
            restock = random.randint(15, 40)
            current_stock_total += restock
        
        current_stock_total -= daily_sold_qty
        if current_stock_total < 0: current_stock_total = 0
        stats[date_str_stats] = current_stock_total

    with open(ORDERS_FILE, 'w', encoding='utf-8') as f: json.dump(orders, f, indent=4)
    with open(STATS_FILE, 'w', encoding='utf-8') as f: json.dump(stats, f, indent=4)

    print(f"✅ Terminé ! {len(orders)} commandes générées.")
    print("👉 Vous pouvez maintenant vous connecter avec 'LaraClette' / '12345678'")

if __name__ == "__main__":
    generate()