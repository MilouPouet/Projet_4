import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QHeaderView, QTabWidget, QComboBox
)
from PyQt5.QtCore import Qt
from src.security import SecurityService
from src.data_manager import DataManager
import json
import os

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guardia Secure Access")
        self.setFixedSize(350, 400)
        layout = QVBoxLayout()
        
        self.title = QLabel("🔐 ADMIN LOGIN")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-weight: bold; font-size: 20px;")
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Utilisateur")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Mot de passe")
        self.pass_input.setEchoMode(QLineEdit.Password)
        
        self.btn_login = QPushButton("Connexion")
        self.btn_register = QPushButton("Inscription (Check Pwned)")
        
        layout.addWidget(self.title)
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_register)
        self.setLayout(layout)
        
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_register.clicked.connect(self.handle_register)

    def handle_register(self):
        user = self.user_input.text()
        pwd = self.pass_input.text()
        if not user or not pwd:
            return QMessageBox.warning(self, "Erreur", "Champs vides.")

        if SecurityService.is_password_pwned(pwd):
            return QMessageBox.critical(self, "🛑 SÉCURITÉ", "Mot de passe COMPROMIS ! Changez-le.")

        hashed = SecurityService.hash_password(pwd)
        user_data = {user: hashed}
        data_path = os.path.join("data", "users.json")
        current_users = {}
        
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r') as f: current_users = json.load(f)
            except: pass
        
        current_users.update(user_data)
        with open(data_path, 'w') as f: json.dump(current_users, f)
        QMessageBox.information(self, "Succès", "Compte créé.")

    def handle_login(self):
        user = self.user_input.text()
        pwd = self.pass_input.text()
        data_path = os.path.join("data", "users.json")
        if not os.path.exists(data_path): return QMessageBox.critical(self, "Erreur", "Aucun utilisateur.")
        
        try:
            with open(data_path, 'r') as f: users = json.load(f)
            if user in users and SecurityService.verify_password(users[user], pwd):
                self.main_window = MainWindow()
                self.main_window.show()
                self.close()
            else: QMessageBox.critical(self, "Erreur", "Identifiants invalides.")
        except: QMessageBox.critical(self, "Erreur", "Erreur lecture base.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guardia ERP")
        self.resize(1000, 700)
        self.data_manager = DataManager()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.tab_manage = QWidget()
        self.setup_management_tab()
        self.tabs.addTab(self.tab_manage, "📦 Gestion")
        
        self.tab_stats = QWidget()
        self.setup_stats_tab()
        self.tabs.addTab(self.tab_stats, "📊 Statistiques")

    def setup_management_tab(self):
        layout = QVBoxLayout()
        tools = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher...")
        self.search_input.textChanged.connect(self.refresh_table)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Défaut", "Prix (Croissant)", "Prix (Décroissant)", "Quantité"])
        self.sort_combo.currentIndexChanged.connect(self.refresh_table)
        tools.addWidget(self.search_input)
        tools.addWidget(self.sort_combo)
        layout.addLayout(tools)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nom", "Prix (€)", "Qté", "Catégorie"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        form = QHBoxLayout()
        self.in_nom = QLineEdit(); self.in_nom.setPlaceholderText("Nom")
        self.in_prix = QLineEdit(); self.in_prix.setPlaceholderText("Prix")
        self.in_qty = QLineEdit(); self.in_qty.setPlaceholderText("Qté")
        self.in_cat = QLineEdit(); self.in_cat.setPlaceholderText("Catégorie")
        btn = QPushButton("Ajouter")
        btn.clicked.connect(self.add_product_action)
        form.addWidget(self.in_nom); form.addWidget(self.in_prix); form.addWidget(self.in_qty); form.addWidget(self.in_cat); form.addWidget(btn)
        layout.addLayout(form)
        self.tab_manage.setLayout(layout)
        self.refresh_table()

    def setup_stats_tab(self):
        layout = QVBoxLayout()
        self.figure = plt.figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        btn = QPushButton("Actualiser")
        btn.clicked.connect(self.refresh_charts)
        layout.addWidget(btn)
        layout.addWidget(self.canvas)
        self.tab_stats.setLayout(layout)

    def refresh_table(self):
        query = self.search_input.text()
        products = self.data_manager.search_products(query) if query else self.data_manager.get_all_products()
        sort_mode = self.sort_combo.currentText()
        
        if "Prix (Croissant)" in sort_mode: products.sort(key=lambda x: float(x['prix']))
        elif "Prix (Décroissant)" in sort_mode: products.sort(key=lambda x: float(x['prix']), reverse=True)
        elif "Quantité" in sort_mode: products.sort(key=lambda x: int(x['quantite']), reverse=True)

        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(p.get('nom', '')))
            self.table.setItem(row, 1, QTableWidgetItem(str(p.get('prix', 0))))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.get('quantite', 0))))
            self.table.setItem(row, 3, QTableWidgetItem(p.get('categorie', '')))

    def add_product_action(self):
        try:
            self.data_manager.add_product({
                "nom": self.in_nom.text(), "prix": float(self.in_prix.text()),
                "quantite": int(self.in_qty.text()), "categorie": self.in_cat.text()
            })
            self.refresh_table(); self.refresh_charts()
            self.in_nom.clear(); self.in_prix.clear(); self.in_qty.clear(); self.in_cat.clear()
        except ValueError: QMessageBox.warning(self, "Erreur", "Prix/Qté invalides")

    def refresh_charts(self):
        products = self.data_manager.get_all_products()
        if not products: return
        self.figure.clear()
        ax1 = self.figure.add_subplot(121)
        names = [p['nom'] for p in products][:5]
        prices = [float(p['prix']) for p in products][:5]
        ax1.bar(names, prices); ax1.set_title("Top Prix")
        
        ax2 = self.figure.add_subplot(122)
        cats = {}
        for p in products: cats[p.get('categorie', 'Autre')] = cats.get(p.get('categorie', 'Autre'), 0) + int(p['quantite'])
        ax2.pie(cats.values(), labels=cats.keys(), autopct='%1.1f%%'); ax2.set_title("Stock")
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
