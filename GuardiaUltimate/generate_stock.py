import os
import sys

# On s'assure de pouvoir importer les modules du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_manager import DataManager

def run():
    print("🚀 Génération du catalogue Wanhao France...")
    
    # Initialisation de la base de données
    db = DataManager()
    
    # Liste réaliste (Modèles et Prix moyens constatés)
    # Note : 'secret_info' sera chiffré automatiquement par l'application
    nouveaux_produits = [
        # --- IMPRIMANTES FDM ---
        {
            "nom": "Wanhao Duplicator 12/230 (Mono)", 
            "prix": 229.00, 
            "quantite": 12, 
            "categorie": "Imprimante FDM", 
            "secret_info": "Fournisseur: Wanhao CN - Marge: 20%"
        },
        {
            "nom": "Wanhao Duplicator 12/230 (Dual Extruder)", 
            "prix": 269.00, 
            "quantite": 8, 
            "categorie": "Imprimante FDM", 
            "secret_info": "Promo possible pour Noël"
        },
        {
            "nom": "Wanhao D12/300 Pro Max", 
            "prix": 399.00, 
            "quantite": 5, 
            "categorie": "Imprimante FDM", 
            "secret_info": "Stock critique (< 5 unités)"
        },
        {
            "nom": "Wanhao D12/500 (Grand Format)", 
            "prix": 549.00, 
            "quantite": 2, 
            "categorie": "Imprimante FDM", 
            "secret_info": "Livraison sur palette uniquement"
        },
        {
            "nom": "Wanhao GR2 (Gadoso Revolution)", 
            "prix": 299.00, 
            "quantite": 15, 
            "categorie": "Imprimante FDM", 
            "secret_info": "Modèle éducatif - Robuste"
        },

        # --- IMPRIMANTES RÉSINE ---
        {
            "nom": "Wanhao D8 (Résine UV)", 
            "prix": 450.00, 
            "quantite": 3, 
            "categorie": "Imprimante Résine", 
            "secret_info": "Liquidation stock ancien"
        },

        # --- FILAMENTS ---
        {
            "nom": "Filament PLA+ Wanhao Blanc 1kg", 
            "prix": 22.90, 
            "quantite": 50, 
            "categorie": "Consommable", 
            "secret_info": "Lot #A882 - Exp: 2026"
        },
        {
            "nom": "Filament PLA Soie Or (Silk Gold)", 
            "prix": 26.90, 
            "quantite": 30, 
            "categorie": "Consommable", 
            "secret_info": "Best-seller Déco"
        },
        {
            "nom": "Filament PETG Noir Wanhao", 
            "prix": 24.90, 
            "quantite": 40, 
            "categorie": "Consommable", 
            "secret_info": "Résistant chaleur"
        },

        # --- PIÈCES ---
        {
            "nom": "Plateau Magnétique PEI 235x235", 
            "prix": 29.90, 
            "quantite": 20, 
            "categorie": "Accessoire", 
            "secret_info": "Compatible Ender 3 aussi"
        },
        {
            "nom": "Kit Buse Laiton 0.4mm (x5)", 
            "prix": 9.90, 
            "quantite": 100, 
            "categorie": "Pièce Détachée", 
            "secret_info": "Vrac fournisseur"
        }
    ]

    count = 0
    # On récupère les produits existants pour éviter les doublons
    produits_existants = [p['nom'] for p in db.get_all_products()]

    for p in nouveaux_produits:
        if p['nom'] not in produits_existants:
            db.add_product(p)
            print(f"✅ Ajouté : {p['nom']}")
            count += 1
        else:
            print(f"ℹ️ Déjà en stock : {p['nom']}")

    print(f"\n🎉 Terminé ! {count} produits ajoutés à la base de données.")
    print("👉 Lancez 'python main.py' pour voir le nouveau catalogue.")

if __name__ == "__main__":
    run()