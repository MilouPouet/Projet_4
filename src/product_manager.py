import uuid
from src.database import read_csv, append_csv, overwrite_csv

PRODUCT_FILE = "products.csv"
PRODUCT_HEADERS = ["product_id", "name", "description", "price", "quantity", "category"]

def list_products():
    """Affiche tous les produits formatés proprement"""
    products = read_csv(PRODUCT_FILE)
    if not products:
        print("\n📭 Aucun produit en stock.")
        return

    print(f"\n{'ID':<36} | {'NOM':<20} | {'PRIX (€)':<10} | {'STOCK':<5}")
    print("-" * 80)
    for p in products:
        print(f"{p['product_id']:<36} | {p['name']:<20} | {p['price']:<10} | {p['quantity']:<5}")

def create_product():
    """Demande les infos à l'utilisateur et crée le produit"""
    print("\n--- Ajout d'un nouveau produit ---")
    name = input("Nom du produit : ")
    desc = input("Description : ")
    cat = input("Catégorie : ")
    
    # Validation des entrées (DevSecOps : Input Validation)
    try:
        price = float(input("Prix : "))
        qty = int(input("Quantité : "))
        if price < 0 or qty < 0:
            raise ValueError("Les valeurs doivent être positives.")
    except ValueError:
        print("❌ Erreur : Le prix et la quantité doivent être des nombres valides.")
        return

    new_prod = {
        "product_id": str(uuid.uuid4()),
        "name": name,
        "description": desc,
        "price": price,
        "quantity": qty,
        "category": cat
    }
    
    append_csv(PRODUCT_FILE, new_prod)
    print("✅ Produit ajouté avec succès !")

def delete_product():
    """Supprime un produit par son ID"""
    target_id = input("\n🗑️ Entrez l'ID du produit à supprimer : ")
    products = read_csv(PRODUCT_FILE)
    
    # On garde tous les produits SAUF celui qu'on veut supprimer
    new_list = [p for p in products if p['product_id'] != target_id]
    
    if len(new_list) == len(products):
        print("❌ ID introuvable.")
    else:
        overwrite_csv(PRODUCT_FILE, new_list, PRODUCT_HEADERS)
        print("✅ Produit supprimé.")