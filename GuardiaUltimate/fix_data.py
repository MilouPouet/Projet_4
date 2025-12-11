import os
import sys
import csv
import json
import uuid

# On s'assure d'importer les modules du projet correctement
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.security import SecurityService

def reset_database():
    print("🧹 NETTOYAGE COMPLET DES DONNÉES...")

    # Chemins des fichiers
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    csv_file = os.path.join(base_dir, "produits.csv")
    orders_file = os.path.join(base_dir, "orders.json")

    # 1. Suppression des anciens fichiers (corrompus avec les IDs en double)
    if os.path.exists(csv_file):
        os.remove(csv_file)
        print("✅ Fichier produits.csv supprimé.")
    
    if os.path.exists(orders_file):
        os.remove(orders_file)
        print("✅ Fichier orders.json supprimé (Reset des commandes).")

    # 2. Création du nouveau fichier produits avec des UUID uniques
    print("🚀 GÉNÉRATION DU NOUVEAU CATALOGUE (IDs UNIQUES)...")
    
    # Liste des produits avec leurs stocks réels
    stock = [
        {"nom": "Wanhao Duplicator 12/230 (Mono)", "prix": 229.00, "quantite": 12, "categorie": "Imprimante FDM", "secret": "Marge: 20%"},
        {"nom": "Wanhao Duplicator 12/230 (Dual)", "prix": 269.00, "quantite": 8, "categorie": "Imprimante FDM", "secret": "Promo Noel"},
        {"nom": "Wanhao D12/300 Pro Max", "prix": 399.00, "quantite": 5, "categorie": "Imprimante FDM", "secret": "Stock critique"},
        {"nom": "Wanhao D12/500 (Grand Format)", "prix": 549.00, "quantite": 2, "categorie": "Imprimante FDM", "secret": "Palette requise"},
        {"nom": "Wanhao GR2 (Gadoso)", "prix": 299.00, "quantite": 15, "categorie": "Imprimante FDM", "secret": "Fin de série"},
        {"nom": "Wanhao D8 (Résine UV)", "prix": 450.00, "quantite": 3, "categorie": "Imprimante Résine", "secret": "Stockage ventilé"},
        {"nom": "Filament PLA+ Blanc 1kg", "prix": 22.90, "quantite": 50, "categorie": "Consommable", "secret": "Lot A882"},
        {"nom": "Filament PLA Soie Or", "prix": 26.90, "quantite": 30, "categorie": "Consommable", "secret": "Best seller"},
        {"nom": "Filament PETG Noir", "prix": 24.90, "quantite": 40, "categorie": "Consommable", "secret": "Résistant"},
        {"nom": "Plateau Magnétique PEI 235", "prix": 29.90, "quantite": 20, "categorie": "Accessoire", "secret": "Fournisseur B"},
        {"nom": "Kit Buse Laiton 0.4mm (x5)", "prix": 9.90, "quantite": 100, "categorie": "Pièce Détachée", "secret": "Vrac"}
    ]

    # Écriture directe dans le CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "nom", "prix", "quantite", "categorie", "secret_info"])
        writer.writeheader()
        
        for p in stock:
            # GÉNÉRATION D'UN ID UNIQUE POUR CHAQUE LIGNE
            p_data = {
                "id": str(uuid.uuid4()),  # <--- C'est ici que la magie opère
                "nom": p["nom"],
                "prix": p["prix"],
                "quantite": p["quantite"],
                "categorie": p["categorie"],
                "secret_info": SecurityService.encrypt_data(p["secret"])
            }
            writer.writerow(p_data)
            print(f"   -> Ajouté : {p['nom']} (Qté: {p['quantite']})")

    # Récréation du fichier de commandes vide
    with open(orders_file, 'w') as f:
        json.dump([], f)

    print("\n🎉 TERMINÉ ! Les données sont propres.")
    print("👉 Relancez 'python main.py', les stocks seront corrects (12, 8, 5, 2...).")

if __name__ == "__main__":
    reset_database()