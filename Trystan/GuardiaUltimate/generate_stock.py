import os
import sys

# Ajout du dossier courant au path pour trouver les modules src
sys.path.append(os.getcwd())

from src.data_manager import DataManager

def generate_data():
    print("🚀 Génération du stock Wanhao France...")
    
    # Initialisation du gestionnaire (crée les fichiers si absents)
    db = DataManager()
    
    # Liste de produits réalistes (Prix et Modèles Wanhao)
    # Les 'secret_info' seront chiffrés automatiquement par votre app
    stock = [
        # --- IMPRIMANTES FDM ---
        {
            "nom": "Wanhao Duplicator 12/230 (D12 Mono)",
            "prix": 229.00,
            "quantite": 15,
            "categorie": "Imprimante FDM",
            "secret_info": "Marge: 18% - Fournisseur: Wanhao China"
        },
        {
            "nom": "Wanhao Duplicator 12/230 (D12 Dual)",
            "prix": 256.80,
            "quantite": 8,
            "categorie": "Imprimante FDM",
            "secret_info": "Marge: 20% - Promo Hiver possible"
        },
        {
            "nom": "Wanhao Duplicator 12/300 Pro Max",
            "prix": 399.00,
            "quantite": 5,
            "categorie": "Imprimante FDM",
            "secret_info": "Seuil critique: 3 unités"
        },
        {
            "nom": "Wanhao Duplicator 12/500 (Géante)",
            "prix": 549.90,
            "quantite": 2,
            "categorie": "Imprimante FDM",
            "secret_info": "Transporteur spécial requis (Palette)"
        },
        {
            "nom": "Wanhao GR2 (Gadoso Revolution 2)",
            "prix": 299.00,
            "quantite": 4,
            "categorie": "Imprimante FDM",
            "secret_info": "Fin de série - Ne pas recommander"
        },
        
        # --- IMPRIMANTES RÉSINE ---
        {
            "nom": "Wanhao Duplicator D8 (Résine UV)",
            "prix": 450.00,
            "quantite": 3,
            "categorie": "Imprimante Résine",
            "secret_info": "Stockage: Endroit ventilé"
        },

        # --- CONSOMMABLES ---
        {
            "nom": "Filament PLA Wanhao 1.75mm Blanc",
            "prix": 24.90,
            "quantite": 120,
            "categorie": "Filament",
            "secret_info": "Lot: 2024-A01 - Achat groupé"
        },
        {
            "nom": "Filament PLA Wanhao 1.75mm Noir",
            "prix": 24.90,
            "quantite": 95,
            "categorie": "Filament",
            "secret_info": "Lot: 2024-A02 - Best Seller"
        },
        {
            "nom": "Résine Wanhao Standard Grise 1L",
            "prix": 35.00,
            "quantite": 30,
            "categorie": "Résine",
            "secret_info": "Date peremption: 12/2025"
        },

        # --- PIÈCES DÉTACHÉES ---
        {
            "nom": "Kit Upgrade Dual Extruder D12",
            "prix": 39.90,
            "quantite": 12,
            "categorie": "Accessoire",
            "secret_info": "Compatible D12/230 uniquement"
        },
        {
            "nom": "Plateau Magnétique PEI 230mm",
            "prix": 29.00,
            "quantite": 25,
            "categorie": "Accessoire",
            "secret_info": "Fournisseur B - Marge élevée"
        }
    ]

    count = 0
    for p in stock:
        # On vérifie si le produit existe déjà pour éviter les doublons (basique)
        existing = [x for x in db.get_all_products() if x['nom'] == p['nom']]
        if not existing:
            db.add_product(p)
            print(f"✅ Ajouté : {p['nom']}")
            count += 1
        else:
            print(f"ℹ️ Déjà présent : {p['nom']}")

    print(f"\n🎉 Terminé ! {count} nouveaux produits ajoutés à 'data/produits.csv'.")
    print("👉 Vous pouvez lancer 'python main.py' pour voir le stock.")

if __name__ == "__main__":
    generate_data()