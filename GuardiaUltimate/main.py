import sys
import os
import io
import qrcode
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QHeaderView, QStackedWidget, QListWidget, QFrame,
    QProgressBar, QCheckBox, QAbstractItemView, QDialog, QSpinBox, QInputDialog, QScrollArea
)
from PyQt5.QtGui import QPixmap, QColor, QFont, QPalette
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from src.security import SecurityService
from src.data_manager import DataManager

STYLESHEET = """
    * { font-family: 'Segoe UI', sans-serif; font-size: 14px; }
    
    QMainWindow, QDialog, QWidget { background-color: #1e1e2e; color: #ffffff; }
    
    QLabel { color: #ffffff; font-size: 14px; background: transparent; }
    
    QLineEdit { 
        background-color: #252535; color: white; border: 2px solid #45475a; 
        border-radius: 6px; padding: 10px; font-size: 14px;
    }
    QLineEdit:focus { border: 2px solid #3498db; }
    
    QPushButton {
        background-color: #3498db; 
        color: white; 
        border-radius: 6px; 
        padding: 12px; 
        font-weight: bold; 
        font-size: 14px;
        border: none;
    }
    QPushButton:hover { background-color: #5dade2; }
    
    QPushButton#BtnOutline {
        background-color: transparent; border: 2px solid #3498db; color: #3498db;
    }
    QPushButton#BtnOutline:hover { background-color: rgba(52, 152, 219, 0.1); }
    
    QCheckBox { color: #ffffff; spacing: 10px; font-size: 15px; font-weight: bold; background: transparent; }
    
    QListWidget { background-color: #181825; border: none; font-size: 15px; color: #a6adc8; }
    QListWidget::item { padding: 15px; border-bottom: 1px solid #313244; }
    QListWidget::item:selected { background-color: #313244; color: #3498db; border-left: 4px solid #3498db; }
    
    QTableWidget { background-color: #1e1e2e; gridline-color: #45475a; color: white; border: 1px solid #45475a; }
    QHeaderView::section { background-color: #313244; color: white; padding: 8px; border: none; font-weight: bold; }
    
    QTableCornerButton::section { background-color: #313244; border: 1px solid #45475a; }
    QScrollBar:vertical { border: none; background: #1e1e2e; width: 10px; }
    QScrollBar::handle:vertical { background: #45475a; border-radius: 5px; }
"""

class OrderDialog(QDialog):
    def __init__(self, product, max_qty, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Commander")
        self.setFixedSize(350, 250)
        l = QVBoxLayout(self)
        self.qty = QSpinBox(); self.qty.setRange(1, max_qty)
        self.qty.setStyleSheet("background: #313244; color: white; padding: 10px; font-size: 18px;")
        btn = QPushButton("VALIDER LA COMMANDE"); btn.clicked.connect(self.accept)
        l.addWidget(QLabel(f"Produit : {product['nom']}")); l.addWidget(QLabel(f"Prix : {product['prix']} €"))
        l.addWidget(QLabel("Quantité :")); l.addWidget(self.qty); l.addWidget(btn)

class LoginWidget(QWidget):
    def __init__(self, parent_controller):
        super().__init__()
        self.parent_controller = parent_controller
        self.db = DataManager()
        
        l = QVBoxLayout(self); l.setAlignment(Qt.AlignCenter)
        frame = QFrame(); frame.setFixedSize(380, 580)
        frame.setStyleSheet("background-color: #181825; border-radius: 20px; border: 2px solid #313244;")
        fl = QVBoxLayout(frame); fl.setSpacing(20); fl.setContentsMargins(40,40,40,40)
        
        title = QLabel("GUARDIA ACCESS"); title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #3498db; background: transparent;")
        
        self.u = QLineEdit(); self.u.setPlaceholderText("Nom d'utilisateur")
        self.p = QLineEdit(); self.p.setPlaceholderText("Mot de passe"); self.p.setEchoMode(QLineEdit.Password)
        self.chk = QCheckBox(" Compte Administrateur")
        
        btn_log = QPushButton("SE CONNECTER"); btn_log.clicked.connect(self.login)
        btn_reg = QPushButton("CRÉER UN COMPTE"); btn_reg.setObjectName("BtnOutline"); btn_reg.clicked.connect(self.register)
        
        fl.addWidget(title); fl.addSpacing(10); fl.addWidget(self.u); fl.addWidget(self.p); fl.addWidget(self.chk)
        fl.addSpacing(20); fl.addWidget(btn_log); fl.addWidget(btn_reg)
        l.addWidget(frame)

    def register(self):
        u, p = self.u.text(), self.p.text()
        if not u or not p: return
        if SecurityService.is_password_pwned(p): QMessageBox.warning(self, "Danger", "Mot de passe compromis !"); return
        role = "admin" if self.chk.isChecked() else "client"
        self.db.register_user(u, {"hash": SecurityService.hash_password(p), "role": role, "2fa_secret": None})
        QMessageBox.information(self, "Succès", f"Compte {role} créé avec succès.")

    def login(self):
        u, p = self.u.text(), self.p.text()
        d = self.db.get_user_data(u)
        if d and SecurityService.verify_password(d.get('hash'), p):
            role = d.get('role', 'client')
            if not d.get('2fa_secret'):
                s = SecurityService.generate_2fa_secret()
                self.parent_controller.show_2fa_setup(u, role, s)
            else:
                self.parent_controller.show_2fa_verify(u, role, d['2fa_secret'])
        else: QMessageBox.warning(self, "Erreur", "Identifiants incorrects")

class Setup2FAWidget(QWidget):
    def __init__(self, parent_controller, username, role, secret):
        super().__init__()
        self.parent_controller = parent_controller
        self.username = username; self.role = role; self.secret = secret
        self.db = DataManager()
        
        l = QVBoxLayout(self); l.setAlignment(Qt.AlignCenter)
        frame = QFrame(); frame.setFixedSize(400, 650)
        frame.setStyleSheet("background-color: #181825; border-radius: 20px; border: 2px solid #313244;")
        fl = QVBoxLayout(frame); fl.setSpacing(15); fl.setContentsMargins(30,30,30,30)
        
        lbl = QLabel("🔐 CONFIGURATION 2FA"); lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498db; background: transparent;")
        lbl.setAlignment(Qt.AlignCenter)
        
        uri = SecurityService.get_totp_uri(username, secret)
        qr = qrcode.QRCode(box_size=10, border=2); qr.add_data(uri); qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        temp_file = "temp_qr.png"; img.save(temp_file); qimg = QPixmap(temp_file)
        lbl_img = QLabel(); lbl_img.setPixmap(qimg.scaled(200, 200, Qt.KeepAspectRatio)); lbl_img.setAlignment(Qt.AlignCenter)
        if os.path.exists(temp_file): os.remove(temp_file)
        
        key_input = QLineEdit(secret); key_input.setReadOnly(True); key_input.setAlignment(Qt.AlignCenter)
        self.code = QLineEdit(); self.code.setPlaceholderText("Code à 6 chiffres"); self.code.setAlignment(Qt.AlignCenter)
        self.code.setStyleSheet("font-size: 18px; padding: 10px;")
        
        btn = QPushButton("VALIDER"); btn.clicked.connect(self.check)
        
        fl.addWidget(lbl); fl.addWidget(lbl_img); fl.addWidget(QLabel("Clé manuelle :")); fl.addWidget(key_input)
        fl.addWidget(self.code); fl.addWidget(btn)
        l.addWidget(frame)

    def check(self):
        if SecurityService.verify_2fa_code(self.secret, self.code.text()):
            self.db.update_user_2fa(self.username, self.secret)
            self.parent_controller.show_app(self.username, self.role)
        else: QMessageBox.warning(self, "Erreur", "Code incorrect.")

class Verify2FAWidget(QWidget):
    def __init__(self, parent_controller, username, role, secret):
        super().__init__()
        self.parent_controller = parent_controller
        self.username = username; self.role = role; self.secret = secret
        
        l = QVBoxLayout(self); l.setAlignment(Qt.AlignCenter)
        frame = QFrame(); frame.setFixedSize(350, 350)
        frame.setStyleSheet("background-color: #181825; border-radius: 20px; border: 2px solid #313244;")
        fl = QVBoxLayout(frame); fl.setSpacing(20); fl.setContentsMargins(40,40,40,40)
        
        lbl = QLabel("VÉRIFICATION 2FA"); lbl.setAlignment(Qt.AlignCenter); lbl.setStyleSheet("font-size: 20px; font-weight: bold; background: transparent;")
        self.code = QLineEdit(); self.code.setPlaceholderText("Code Authenticator"); self.code.setAlignment(Qt.AlignCenter)
        self.code.setStyleSheet("font-size: 20px; padding: 10px;")
        btn = QPushButton("ENTRER"); btn.clicked.connect(self.check)
        
        fl.addWidget(lbl); fl.addWidget(self.code); fl.addWidget(btn)
        l.addWidget(frame)

    def check(self):
        if SecurityService.verify_2fa_code(self.secret, self.code.text()): self.parent_controller.show_app(self.username, self.role)
        else: QMessageBox.warning(self, "Erreur", "Code incorrect.")

class AppWidget(QWidget):
    def __init__(self, username, role, logout_callback):
        super().__init__()
        self.username = username; self.role = role; self.logout = logout_callback
        self.db = DataManager()
        
        layout = QHBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        self.sidebar = QListWidget(); self.sidebar.setFixedWidth(240)
        if role == "admin": self.sidebar.addItems(["📊 Tableau de Bord", "📦 Gestion Stock", "🚚 Commandes", "👥 Utilisateurs", "🚪 Déconnexion"])
        else: self.sidebar.addItems(["🛍️ Catalogue", "🛒 Mes Commandes", "⚙️ Mon Compte", "🚪 Déconnexion"])
        self.sidebar.currentRowChanged.connect(self.nav)
        
        self.stack = QStackedWidget()
        self.refresh_pages()
        layout.addWidget(self.sidebar); layout.addWidget(self.stack)

    def nav(self, i):
        max_idx = 4 if self.role == "admin" else 3
        if i == max_idx: self.logout(); return
        self.stack.setCurrentIndex(i); self.refresh_pages() 

    def refresh_pages(self):
        current = self.stack.currentIndex()
        for _ in range(self.stack.count()): self.stack.removeWidget(self.stack.widget(0))
        if self.role == "admin":
            self.stack.addWidget(self.view_dashboard())
            self.stack.addWidget(self.view_stock())
            self.stack.addWidget(self.view_orders())
            self.stack.addWidget(self.view_users())
        else:
            self.stack.addWidget(self.view_catalog())
            self.stack.addWidget(self.view_my_orders())
            self.stack.addWidget(self.view_settings())
        self.stack.setCurrentIndex(current if current >= 0 else 0)

    def view_dashboard(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); l = QVBoxLayout(content); l.setSpacing(30)
        l.addWidget(QLabel("📊 TABLEAU DE BORD STRATÉGIQUE"))
        try:
            # 1. Ventes par Jour (AVEC MARGES & REMPLISSAGE)
            fig1 = Figure(facecolor='#1e1e2e', figsize=(5, 4)); ax1 = fig1.add_subplot(111); ax1.set_facecolor('#1e1e2e')
            fig1.subplots_adjust(bottom=0.3)
            sales = self.db.get_sales_per_day()
            if sales:
                ax1.bar(sales.keys(), sales.values(), color='#3498db')
                ax1.tick_params(axis='x', colors='white', rotation=90, labelsize=10)
                ax1.tick_params(axis='y', colors='white')
            else: ax1.text(0.5, 0.5, "Pas de ventes", color='white', ha='center')
            ax1.set_title("Ventes par Jour", color='white'); ax1.spines['bottom'].set_color('white'); ax1.spines['left'].set_color('white')
            l.addWidget(FigureCanvas(fig1))

            # 2. Top Produits
            fig2 = Figure(facecolor='#1e1e2e', figsize=(5, 3)); ax2 = fig2.add_subplot(111); ax2.set_facecolor('#1e1e2e')
            fig2.subplots_adjust(left=0.3)
            top = self.db.get_top_products()
            if top: ax2.barh([x[0] for x in top], [x[1] for x in top], color='#f9e2af')
            else: ax2.text(0.5, 0.5, "Pas de données", color='white', ha='center')
            ax2.set_title("Top Produits", color='white'); ax2.tick_params(colors='white'); ax2.spines['bottom'].set_color('white'); ax2.spines['left'].set_color('white')
            l.addWidget(FigureCanvas(fig2))

            # 3. Historique Stock
            fig3 = Figure(facecolor='#1e1e2e', figsize=(5, 4)); ax3 = fig3.add_subplot(111); ax3.set_facecolor('#1e1e2e')
            fig3.subplots_adjust(bottom=0.3)
            hist = self.db.get_stock_history()
            if hist:
                ax3.plot(list(hist.keys()), list(hist.values()), marker='o', color='#89b4fa', linewidth=2)
                ax3.tick_params(axis='x', colors='white', rotation=90, labelsize=10)
                ax3.tick_params(axis='y', colors='white')
            else: ax3.text(0.5, 0.5, "Historique vide", color='white', ha='center')
            ax3.set_title("Évolution Stock Total", color='white'); ax3.spines['bottom'].set_color('white'); ax3.spines['left'].set_color('white')
            l.addWidget(FigureCanvas(fig3))

        except Exception as e: l.addWidget(QLabel(f"Erreur graphique: {e}"))
        scroll.setWidget(content)
        return scroll

    def view_stock(self):
        w = QWidget(); l = QVBoxLayout(w)
        form = QHBoxLayout()
        self.n = QLineEdit(); self.n.setPlaceholderText("Nom")
        self.p = QLineEdit(); self.p.setPlaceholderText("Prix")
        self.q = QLineEdit(); self.q.setPlaceholderText("Qté")
        btn = QPushButton("AJOUTER"); btn.clicked.connect(self.add_p)
        form.addWidget(self.n); form.addWidget(self.p); form.addWidget(self.q); form.addWidget(btn)
        tab = QTableWidget(0, 4); tab.setHorizontalHeaderLabels(["Produit", "Prix Unitaire", "Stock Total", "Disponibilité"])
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for r, p in enumerate(self.db.get_all_products()):
            tab.insertRow(r); tab.setItem(r, 0, QTableWidgetItem(p['nom'])); tab.setItem(r, 1, QTableWidgetItem(f"{p['prix']} €")); tab.setItem(r, 2, QTableWidgetItem(p['quantite']))
            real, res, av = self.db.get_stock_status(p['id'])
            tab.setItem(r, 3, QTableWidgetItem(f"{av} dispo (Réservé: {res})"))
        l.addLayout(form); l.addWidget(tab)
        return w

    def add_p(self):
        try: self.db.add_product({"nom":self.n.text(), "prix":float(self.p.text()), "quantite":int(self.q.text()), "categorie":"Divers"}); self.refresh_pages()
        except: pass

    def view_orders(self):
        w = QWidget(); l = QVBoxLayout(w)
        tab = QTableWidget(0, 4); tab.setHorizontalHeaderLabels(["ID Commande", "Client", "Total", "Statut"])
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for r, o in enumerate(self.db.get_all_orders()):
            tab.insertRow(r); tab.setItem(r, 0, QTableWidgetItem(o['id'])); tab.setItem(r, 1, QTableWidgetItem(o['user'])); tab.setItem(r, 2, QTableWidgetItem(f"{o['total']} €"))
            btn = QPushButton("EN ATTENTE" if o['status'] == 'PENDING' else "EXPÉDIÉE")
            if o['status'] == 'PENDING': btn.setStyleSheet("background: orange; color: black"); btn.clicked.connect(lambda ch, oid=o['id']: self.ship(oid))
            else: btn.setStyleSheet("background: green; border: none; color: white"); btn.setDisabled(True)
            tab.setCellWidget(r, 3, btn)
        l.addWidget(tab)
        return w

    def ship(self, oid):
        if self.db.validate_order(oid): QMessageBox.information(self, "Succès", "Commande validée !"); self.refresh_pages()

    def view_users(self):
        w = QWidget(); l = QVBoxLayout(w); l.addWidget(QLabel("GESTION DES UTILISATEURS"))
        tab = QTableWidget(0, 3); tab.setHorizontalHeaderLabels(["Identifiant", "Rôle", "Action"]); tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        users = self.db.get_all_users_list(); row = 0
        for u, data in users.items():
            if u == self.username: continue 
            tab.insertRow(row); tab.setItem(row, 0, QTableWidgetItem(u)); tab.setItem(row, 1, QTableWidgetItem(data.get('role', 'client').upper()))
            btn_del = QPushButton("SUPPRIMER"); btn_del.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
            btn_del.clicked.connect(lambda ch, usr=u: self.del_user(usr))
            tab.setCellWidget(row, 2, btn_del); row += 1
        l.addWidget(tab)
        return w

    def del_user(self, u):
        if QMessageBox.question(self, "Confirmer", f"Supprimer {u} ?") == QMessageBox.Yes: self.db.delete_user(u); self.refresh_pages()

    def view_catalog(self):
        w = QWidget(); l = QVBoxLayout(w)
        tab = QTableWidget(0, 4); tab.setHorizontalHeaderLabels(["Nom Produit", "Prix", "Disponibilité", "Panier"])
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for r, p in enumerate(self.db.get_all_products()):
            real, res, av = self.db.get_stock_status(p['id'])
            tab.insertRow(r); tab.setItem(r, 0, QTableWidgetItem(p['nom'])); tab.setItem(r, 1, QTableWidgetItem(f"{p['prix']} €")); tab.setItem(r, 2, QTableWidgetItem(f"{av} en stock"))
            btn = QPushButton("COMMANDER")
            if av > 0: btn.clicked.connect(lambda ch, prod=p, m=av: self.buy(prod, m))
            else: btn.setDisabled(True); btn.setText("RUPTURE"); btn.setStyleSheet("background: #45475a; color: #a6adc8;")
            tab.setCellWidget(r, 3, btn)
        l.addWidget(tab)
        return w

    def buy(self, p, m):
        d = OrderDialog(p, m, self)
        if d.exec_(): self.db.place_order(self.username, [{"id":p['id'], "nom":p['nom'], "qty":d.qty.value(), "price":float(p['prix']) }]); QMessageBox.information(self, "Info", "Envoyée !"); self.refresh_pages()

    def view_my_orders(self):
        w = QWidget(); l = QVBoxLayout(w); lst = QListWidget()
        for o in [x for x in self.db.get_all_orders() if x['user'] == self.username]:
            icon = "🟢" if o['status'] == 'SHIPPED' else "🟠"
            lst.addItem(f"{o['date']} | Total: {o['total']} € | {icon}")
        l.addWidget(lst)
        return w
        
    def view_settings(self):
        w = QWidget(); l = QVBoxLayout(w); l.addWidget(QLabel("CHANGER MDP"))
        self.new_p = QLineEdit(); self.new_p.setEchoMode(QLineEdit.Password)
        btn = QPushButton("VALIDER"); btn.clicked.connect(self.chg_pass)
        l.addWidget(self.new_p); l.addWidget(btn); l.addStretch()
        return w
        
    def chg_pass(self):
        if self.new_p.text(): self.db.change_password(self.username, SecurityService.hash_password(self.new_p.text())); QMessageBox.information(self, "OK", "Fait.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guardia App")
        self.resize(1200, 800)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.login_widget = LoginWidget(self)
        self.stack.addWidget(self.login_widget)

    def show_login(self):
        self.clear_stack()
        self.stack.addWidget(LoginWidget(self))

    def show_2fa_setup(self, u, r, s):
        self.clear_stack()
        self.stack.addWidget(Setup2FAWidget(self, u, r, s))

    def show_2fa_verify(self, u, r, s):
        self.clear_stack()
        self.stack.addWidget(Verify2FAWidget(self, u, r, s))

    def show_app(self, u, r):
        self.clear_stack()
        self.stack.addWidget(AppWidget(u, r, self.show_login))

    def clear_stack(self):
        while self.stack.count() > 0:
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
