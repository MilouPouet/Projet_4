RoadMaps 🗓️  :
🏁 SEMAINE 1 : Le Socle "Invisible" (Backend & Sécurité) Tout le monde travaille sur le code Python pur (pas de fenêtres graphiques).

Lundi : Kick-off & Data Model (TOUS) ◦ Définir ensemble le format du fichier CSV et les noms des variables — c'est crucial pour éviter de perdre du temps par la suite.

• Mardi - Mercredi : ◦ Dev 1 : Code le Module 1 (CRUD Produits) + Gestion des erreurs CSV. ◦ Dev 2 : Code le Module 2 (Classe User + Hachage SHA-256). ◦ Dev 3 : Prépare les fonctions de statistiques (Module 5, partie backend) ou aide sur le CRUD.

• Jeudi - Vendredi : Intégration Sécurité ◦ Dev 2 intègre l'API HaveIBeenPwned (Module 3). ◦ Dev 1 & 3 utilisent la classe de Dev 2 pour protéger l'accès à leurs fonctions. ◦ 🎯 Livrable S1 : Un programme en ligne de commande avec login sécurisé et gestion des produits.

🎨 SEMAINE 2 : L'Expérience Utilisateur (Le "Bottleneck") Attention : c'est ici que l'équipe de 3 risque de ralentir. Le Dev Frontend a beaucoup de travail.

Lundi - Mercredi : Focus GUI ◦ Dev 3 : Construit les fenêtres principales (Tkinter/PyQt). ◦ Dev 1 : Connecte ses fonctions Backend aux boutons du Dev 3 (Binding). Il ne commence pas l'API tout de suite — il aide le Frontend. ◦ Dev 2 : Sécurise l'interface (masquage mot de passe, timeout session, logs d'erreurs).

• Jeudi - Vendredi : Stats & Commandes ◦ Dev 1 : Logique de commande (déstockage). ◦ Dev 3 : Intègre les graphiques Matplotlib dans la fenêtre. ◦ 🎯 Livrable S2 : L'application graphique est terminée et fonctionnelle.

🚀 SEMAINE 3 : Ouverture (API) & Audit Sprint final vers la qualité et le web.

Lundi - Mardi : API REST (Module 6) ◦ Dev 1 : Prend le lead sur Flask/FastAPI. Il expose ce qui a été fait en S1 et S2. ◦ Dev 2 : Implémente l'authentification JWT sur l'API (pour ne pas laisser l'API ouverte à tous). ◦ Dev 3 : Nettoie le code de l'interface graphique et écrit la documentation utilisateur.

• Mercredi : Journée "Hackers" (Module 7) ◦ TOUS : On arrête de coder des fonctionnalités. ◦ Lancement de Bandit, Safety et Pylint. ◦ Chacun corrige ses propres bugs de sécurité trouvés par les outils.

• Jeudi : Finalisation ◦ Merge final sur Git et préparation de la démo.

• Vendredi : DÉMO 🎉

💡 Conseil Tactique pour 3 personnes Si vous êtes en retard à la fin de la Semaine 2 : Sacrifiez la partie graphique du Module 5 (Stats Visuelles). Mieux vaut une application sécurisée qui affiche les stats en texte simple (dans la console ou un tableau) qu'une application avec de jolis graphiques qui plante ou n'est pas finie.