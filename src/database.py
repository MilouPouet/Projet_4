import csv
import os

DATA_DIR = "data"

def initialize_files():
    """Crée les fichiers CSV s'ils n'existent pas avec les bons headers"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    files = {
        "users.csv": ["user_id", "username", "password_hash", "salt", "role"],
        "products.csv": ["product_id", "name", "description", "price", "quantity", "category"]
    }

    for filename, headers in files.items():
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            with open(path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"[INFO] Fichier créé : {filename}")

def read_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    data = []
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"[ERREUR] Fichier introuvable : {filename}")
    return data

def append_csv(filename, row_dict):
    path = os.path.join(DATA_DIR, filename)
    # Récupérer les headers du fichier existant
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
    
    with open(path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writerow(row_dict)

def overwrite_csv(filename, data_list, headers):
    """
    Écrase le fichier CSV avec la nouvelle liste de données.
    Utilisé pour la suppression ou la modification.
    """
    path = os.path.join(DATA_DIR, filename)
    with open(path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_list)