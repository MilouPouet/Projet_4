from src.database import initialize_files
from src.auth import register_user, login_user
from src.pwned_check import check_password_leak  # <-- NOUVEAU
from src.product_manager import list_products, create_product, delete_product # <-- NOUVEAU

def main():
    print("--- NOVICORE SECURE SHOP ---")
    initialize_files()
    
    current_user = None

    while True:
        if not current_user:
            # --- MENU NON CONNECTÉ ---
            print("\n1. Se connecter")
            print("2. Créer un compte")
            print("3. Quitter")
            choix = input("Choix > ")
            
            if choix == "1":
                user = input("Utilisateur: ")
                pwd = input("Mot de passe: ")
                success, msg = login_user(user, pwd)
                if success:
                    print(f"\n✅ Bienvenue {msg['username']} ! (Role: {msg['role']})")
                    current_user = msg
                else:
                    print(f"\n❌ {msg}")

            elif choix == "2":
                user = input("Nouvel utilisateur: ")
                pwd = input("Nouveau mot de passe: ")
                
                # --- ÉTAPE DE SÉCURITÉ ---
                print("🔍 Vérification fuites de données...")
                is_leaked, count = check_password_leak(pwd)
                
                if is_leaked:
                    print(f"⚠️ DANGER : Ce mot de passe est apparu {count} fois dans des fuites !")
                    print("❌ Création de compte refusée par sécurité.")
                else:
                    success, msg = register_user(user, pwd)
                    print(f"\n{msg}")
            
            elif choix == "3":
                print("Au revoir !")
                break
        
        else:
            # --- MENU CONNECTÉ ---
            print(f"\n--- Menu {current_user['username']} ---")
            print("1. Voir les produits")
            print("2. Ajouter un produit")
            print("3. Supprimer un produit")
            print("4. Déconnexion")
            
            choix = input("Choix > ")
            
            if choix == "1":
                list_products()
            elif choix == "2":
                create_product()
            elif choix == "3":
                delete_product()
            elif choix == "4":
                current_user = None
                print("Déconnexion...")

if __name__ == "__main__":
    main()