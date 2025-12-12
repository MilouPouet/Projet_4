import sys
import os
import io
import qrcode
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QHeaderView, QStackedWidget, QListWidget, QFrame,
    QProgressBar, QCheckBox, QAbstractItemView, QDialog, QSpinBox, QInputDialog, QScrollArea, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QColor, QFont, QPalette
from PyQt5.QtCore import Qt, QTimer
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
        background-color: #3498db; color: white; border-radius: 6px; 
        padding: 12px; font-weight: bold; font-size: 14px; border: none;
    }
    QPushButton:hover { background-color: #5dade2; }
    
    QPushButton.btn-danger { background-color: #e74c3c; color: white; }
    QPushButton.btn-danger:hover { background-color: #c0392b; }
    
    QPushButton.btn-success { background-color: #2ecc71; color: white; }
    QPushButton.btn-success:hover { background-color: #27ae60; }

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
    
    QPushButton.tab-btn { padding: 5px; font-size: 12px; min-width: 30px; margin: 2px; }
"""

class OrderDialog(QDialog):
    def __init__(self, product, max_qty, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter au Panier")
        self.setFixedSize(350, 250)
        l = QVBoxLayout(self)
        self.qty = QSpinBox(); self.qty.setRange(1, max_qty)
        self.qty.setStyleSheet("background: #313244; color: white; padding: 10px; font-size: 18px;")
        btn = QPushButton("AJOUTER AU PANIER"); btn.clicked.connect(self.accept)
        l.addWidget(QLabel(f"Produit : {product['nom']}")); l.addWidget(QLabel(f"Prix : {product['prix']} €"))
        l.addWidget(QLabel("Quantité :")); l.addWidget(self.qty); l.addWidget(btn)

class StockQuickDialog(QDialog):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Stock: {product['nom']}")
        self.setFixedSize(300, 200)
        self.delta = 0
        l = QVBoxLayout(self)
        l.addWidget(QLabel(f"Stock actuel: {product['quantite']}"))
        l.addWidget(QLabel("Ajustement (+ pour ajout, - pour retrait):"))
        self.spin = QSpinBox(); self.spin.setRange(-1000, 1000); self.spin.setValue(0)
        self.spin.setStyleSheet("background: #313244; color: white; padding: 10px; font-size: 18px;")
        btn = QPushButton("VALIDER"); btn.clicked.connect(self.accept)
        l.addWidget(self.spin); l.addWidget(btn)
    def accept(self):
        self.delta = self.spin.value()
        super().accept()

class ProductEditDialog(QDialog):
    def __init__(self, p, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier Produit")
        self.setFixedSize(400, 350)
        l = QVBoxLayout(self)
        self.n = QLineEdit(p['nom'])
        self.p = QLineEdit(str(p['prix']))
        self.c = QLineEdit(p['categorie'])
        self.s = QLineEdit(p.get('secret_info', ''))
        l.addWidget(QLabel("Nom:")); l.addWidget(self.n)
        l.addWidget(QLabel("Prix:")); l.addWidget(self.p)
        l.addWidget(QLabel("Catégorie:")); l.addWidget(self.c)
        l.addWidget(QLabel("Info Secrète:")); l.addWidget(self.s)
        btn = QPushButton("ENREGISTRER"); btn.clicked.connect(self.accept)
        l.addWidget(btn)
    def get_data(self):
        return {"nom": self.n.text(), "prix": float(self.p.text()) if self.p.text() else 0.0, "categorie": self.c.text(), "secret_info": self.s.text()}

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
                QTimer.singleShot(10, lambda: self.parent_controller.show_2fa_setup(u, role, s))
            else:
                QTimer.singleShot(10, lambda: self.parent_controller.show_2fa_verify(u, role, d['2fa_secret']))
        else: QMessageBox.warning(self, "Erreur", "Identifiants incorrects")

class Setup2FAWidget(QWidget):
    def __init__(self, parent_controller, username, role, secret):
        super().__init__()
        self.parent_controller = parent_controller
        self.username = username; self.role = role; self.secret = secret; self.db = DataManager()
        
        l = QVBoxLayout(self); l.setAlignment(Qt.AlignCenter)
        frame = QFrame(); frame.setFixedSize(400, 650)
        frame.setStyleSheet("background-color: #181825; border-radius: 20px; border: 2px solid #313244;")
        fl = QVBoxLayout(frame); fl.setSpacing(15); fl.setContentsMargins(30,30,30,30)
        
        lbl = QLabel("🔐 CONFIGURATION 2FA"); lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498db; background: transparent;")
        lbl.setAlignment(Qt.AlignCenter)
        
        uri = SecurityService.get_totp_uri(username, secret)
        qr = qrcode.QRCode(box_size=10, border=2); qr.add_data(uri); qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        temp = "temp_qr.png"; img.save(temp); qimg = QPixmap(temp)
        lbl_img = QLabel(); lbl_img.setPixmap(qimg.scaled(200, 200, Qt.KeepAspectRatio)); lbl_img.setAlignment(Qt.AlignCenter)
        if os.path.exists(temp): os.remove(temp)
        
        key_input = QLineEdit(secret); key_input.setReadOnly(True); key_input.setAlignment(Qt.AlignCenter)
        self.code = QLineEdit(); self.code.setPlaceholderText("Code 6 chiffres"); self.code.setAlignment(Qt.AlignCenter)
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
        self.cart = [] # PANIER DU CLIENT
        
        layout = QHBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        sidebar_container = QWidget()
        sidebar_container.setFixedWidth(240)
        sidebar_container.setStyleSheet("background-color: #181825; border-right: 1px solid #45475a;")
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        self.nav_list = QListWidget(); self.nav_list.setStyleSheet("border: none;")
        if role == "admin": 
            self.nav_list.addItems(["📊 Tableau de Bord", "📦 Gestion Stock", "🚚 Commandes", "👥 Utilisateurs"])
        else: 
            self.nav_list.addItems(["🛍️ Catalogue", "🛒 Mon Panier", "📦 Mes Commandes", "⚙️ Mon Compte"])
            
        self.nav_list.currentRowChanged.connect(self.switch_page)
        btn_logout = QPushButton("🚪 DÉCONNEXION")
        btn_logout.setProperty("class", "btn-danger")
        btn_logout.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(btn_logout)
        layout.addWidget(sidebar_container)
        self.stack = QStackedWidget()
        self.refresh_pages()
        layout.addWidget(self.stack)

    def switch_page(self, i):
        self.stack.setCurrentIndex(i); self.refresh_pages()

    def refresh_pages(self):
        current = self.stack.currentIndex()
        while self.stack.count():
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
            
        if self.role == "admin":
            self.stack.addWidget(self.view_dashboard())
            self.stack.addWidget(self.view_stock())
            self.stack.addWidget(self.view_orders())
            self.stack.addWidget(self.view_users())
        else:
            self.stack.addWidget(self.view_catalog())
            self.stack.addWidget(self.view_cart()) # VUE PANIER
            self.stack.addWidget(self.view_my_orders())
            self.stack.addWidget(self.view_settings())
        
        self.stack.setCurrentIndex(current if current >= 0 else 0)

    # --- VUE CLIENT : PANIER ---
    def view_cart(self):
        w = QWidget(); l = QVBoxLayout(w)
        l.addWidget(QLabel(f"MON PANIER ({len(self.cart)} articles)"))
        
        table = QTableWidget(0, 4); table.setHorizontalHeaderLabels(["Produit", "Prix Unitaire", "Quantité", "Total"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        total_cmd = 0
        for r, item in enumerate(self.cart):
            table.insertRow(r)
            table.setItem(r, 0, QTableWidgetItem(item['nom']))
            table.setItem(r, 1, QTableWidgetItem(f"{item['price']} €"))
            table.setItem(r, 2, QTableWidgetItem(str(item['qty'])))
            subtotal = item['price'] * item['qty']
            table.setItem(r, 3, QTableWidgetItem(f"{subtotal:.2f} €"))
            total_cmd += subtotal
            
        l.addWidget(table)
        
        footer = QHBoxLayout()
        lbl_total = QLabel(f"TOTAL À PAYER : {total_cmd:.2f} €")
        lbl_total.setStyleSheet("font-size: 18px; font-weight: bold; color: #a6e3a1;")
        
        btn_clear = QPushButton("VIDER"); btn_clear.setProperty("class", "btn-danger")
        btn_clear.clicked.connect(self.clear_cart)
        
        btn_valid = QPushButton("VALIDER LA COMMANDE"); btn_valid.setProperty("class", "btn-success")
        if not self.cart: btn_valid.setDisabled(True)
        btn_valid.clicked.connect(self.checkout)
        
        footer.addWidget(btn_clear); footer.addStretch(); footer.addWidget(lbl_total); footer.addWidget(btn_valid)
        l.addLayout(footer)
        return w

    def add_to_cart(self, p, qty):
        # Ajout au panier local
        self.cart.append({
            "id": p['id'],
            "nom": p['nom'],
            "qty": qty,
            "price": float(p['prix'])
        })
        QMessageBox.information(self, "Panier", f"{qty}x {p['nom']} ajouté au panier !")

    def clear_cart(self):
        self.cart = []
        self.refresh_pages()

    def checkout(self):
        if not self.cart: return
        self.db.place_order(self.username, self.cart)
        QMessageBox.information(self, "Succès", "Commande validée et envoyée !")
        self.cart = [] # Vider le panier
        self.nav_list.setCurrentRow(2) # Rediriger vers "Mes Commandes"

    # --- AUTRES VUES ---
    def view_dashboard(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); l = QVBoxLayout(content); l.setSpacing(30)
        l.addWidget(QLabel("📊 TABLEAU DE BORD STRATÉGIQUE"))
        try:
            fig1 = Figure(facecolor='#1e1e2e', figsize=(5, 4)); ax1 = fig1.add_subplot(111); ax1.set_facecolor('#1e1e2e'); fig1.subplots_adjust(bottom=0.3)
            sales = self.db.get_sales_per_day()
            if sales: ax1.bar(sales.keys(), sales.values(), color='#3498db'); ax1.tick_params(colors='white', rotation=90)
            ax1.set_title("Ventes par Jour", color='white'); ax1.spines['bottom'].set_color('white'); ax1.spines['left'].set_color('white'); l.addWidget(FigureCanvas(fig1))

            fig2 = Figure(facecolor='#1e1e2e', figsize=(5, 3)); ax2 = fig2.add_subplot(111); ax2.set_facecolor('#1e1e2e'); fig2.subplots_adjust(left=0.3)
            top = self.db.get_top_products()
            if top: ax2.barh([x[0] for x in top], [x[1] for x in top], color='#f9e2af'); ax2.tick_params(colors='white')
            ax2.set_title("Top Produits", color='white'); ax2.spines['bottom'].set_color('white'); ax2.spines['left'].set_color('white'); l.addWidget(FigureCanvas(fig2))

            fig3 = Figure(facecolor='#1e1e2e', figsize=(5, 4)); ax3 = fig3.add_subplot(111); ax3.set_facecolor('#1e1e2e'); fig3.subplots_adjust(bottom=0.3)
            hist = self.db.get_stock_history()
            if hist: ax3.plot(list(hist.keys()), list(hist.values()), marker='o', color='#89b4fa'); ax3.tick_params(colors='white', rotation=90)
            ax3.set_title("Évolution Stock", color='white'); ax3.spines['bottom'].set_color('white'); ax3.spines['left'].set_color('white'); l.addWidget(FigureCanvas(fig3))
        except Exception as e: l.addWidget(QLabel(f"Erreur graphique: {e}"))
        scroll.setWidget(content); return scroll

    def view_stock(self):
        w = QWidget(); l = QVBoxLayout(w)
        search_bar = QLineEdit(); search_bar.setPlaceholderText("🔍 Rechercher un produit...")
        search_bar.textChanged.connect(lambda text: self.filter_table(self.table_stock, text)); l.addWidget(search_bar)
        form = QHBoxLayout()
        self.n = QLineEdit(); self.n.setPlaceholderText("Nom")
        self.p = QLineEdit(); self.p.setPlaceholderText("Prix")
        self.q = QLineEdit(); self.q.setPlaceholderText("Qté")
        btn = QPushButton("AJOUTER"); btn.clicked.connect(self.add_p)
        form.addWidget(self.n); form.addWidget(self.p); form.addWidget(self.q); form.addWidget(btn); l.addLayout(form)
        self.table_stock = QTableWidget(0, 5); self.table_stock.setHorizontalHeaderLabels(["Produit", "Prix", "Stock", "Dispo", "Actions"])
        self.table_stock.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for r, p in enumerate(self.db.get_all_products()):
            self.table_stock.insertRow(r); self.table_stock.setItem(r, 0, QTableWidgetItem(p['nom'])); self.table_stock.setItem(r, 1, QTableWidgetItem(f"{p['prix']} €")); self.table_stock.setItem(r, 2, QTableWidgetItem(p['quantite']))
            real, res, av = self.db.get_stock_status(p['id'])
            self.table_stock.setItem(r, 3, QTableWidgetItem(f"{av} (Res:{res})"))
            frame = QWidget(); hl = QHBoxLayout(frame); hl.setContentsMargins(0,0,0,0)
            btn_edit = QPushButton("📝"); btn_edit.setProperty("class", "tab-btn"); btn_edit.setStyleSheet("background-color: #f9e2af; color: black;")
            btn_edit.clicked.connect(lambda ch, prod=p: self.edit_p(prod))
            btn_stock = QPushButton("📦"); btn_stock.setProperty("class", "tab-btn"); btn_stock.setStyleSheet("background-color: #a6e3a1; color: black;")
            btn_stock.clicked.connect(lambda ch, prod=p: self.adjust_s(prod))
            hl.addWidget(btn_edit); hl.addWidget(btn_stock); self.table_stock.setCellWidget(r, 4, frame)
        l.addWidget(self.table_stock); return w

    def filter_table(self, table, text):
        for i in range(table.rowCount()):
            item = table.item(i, 0)
            if text.lower() in item.text().lower(): table.setRowHidden(i, False)
            else: table.setRowHidden(i, True)

    def add_p(self):
        try: self.db.add_product({"nom":self.n.text(), "prix":float(self.p.text()), "quantite":int(self.q.text()), "categorie":"Divers"}); self.refresh_pages()
        except: pass

    def edit_p(self, p):
        d = ProductEditDialog(p, self)
        if d.exec_(): self.db.update_product_data(p['id'], d.get_data()); self.refresh_pages()

    def adjust_s(self, p):
        d = StockQuickDialog(p, self)
        if d.exec_(): self.db.adjust_stock(p['id'], d.delta); self.refresh_pages()

    def view_orders(self):
        w = QWidget(); l = QVBoxLayout(w)
        tab = QTableWidget(0, 4); tab.setHorizontalHeaderLabels(["ID", "Client", "Total", "Statut"]); tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # --- TRI INVERSÉ ---
        orders = self.db.get_all_orders()[::-1]
        for r, o in enumerate(orders):
            tab.insertRow(r); tab.setItem(r, 0, QTableWidgetItem(o['id'])); tab.setItem(r, 1, QTableWidgetItem(o['user'])); tab.setItem(r, 2, QTableWidgetItem(f"{o['total']} €"))
            btn = QPushButton("EN ATTENTE" if o['status'] == 'PENDING' else "EXPÉDIÉE")
            if o['status'] == 'PENDING': btn.setStyleSheet("background: orange; color: black"); btn.clicked.connect(lambda ch, oid=o['id']: self.ship(oid))
            else: btn.setStyleSheet("background: green; border: none; color: white"); btn.setDisabled(True)
            tab.setCellWidget(r, 3, btn)
        l.addWidget(tab); return w

    def ship(self, oid):
        if self.db.validate_order(oid): QMessageBox.information(self, "Succès", "Validée !"); self.refresh_pages()

    def view_users(self):
        w = QWidget(); l = QVBoxLayout(w); l.addWidget(QLabel("GESTION DES UTILISATEURS"))
        tab = QTableWidget(0, 3); tab.setHorizontalHeaderLabels(["Identifiant", "Rôle", "Action"]); tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        users = self.db.get_all_users_list(); row = 0
        for u, data in users.items():
            if u == self.username: continue
            tab.insertRow(row); tab.setItem(row, 0, QTableWidgetItem(u)); tab.setItem(row, 1, QTableWidgetItem(data.get('role', 'client').upper()))
            btn = QPushButton("SUPP"); btn.setProperty("class", "btn-danger"); btn.clicked.connect(lambda ch, usr=u: self.del_user(usr))
            tab.setCellWidget(row, 2, btn); row += 1
        l.addWidget(tab); return w

    def del_user(self, u):
        if QMessageBox.question(self, "Confirmer", f"Supprimer {u}?") == QMessageBox.Yes: self.db.delete_user(u); self.refresh_pages()

    def view_catalog(self):
        w = QWidget(); l = QVBoxLayout(w)
        search_bar = QLineEdit(); search_bar.setPlaceholderText("🔍 Rechercher un produit...")
        search_bar.textChanged.connect(lambda text: self.filter_table(self.table_cat, text)); l.addWidget(search_bar)
        self.table_cat = QTableWidget(0, 4); self.table_cat.setHorizontalHeaderLabels(["Produit", "Prix", "Dispo", "Panier"])
        self.table_cat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for r, p in enumerate(self.db.get_all_products()):
            real, res, av = self.db.get_stock_status(p['id'])
            self.table_cat.insertRow(r); self.table_cat.setItem(r, 0, QTableWidgetItem(p['nom'])); self.table_cat.setItem(r, 1, QTableWidgetItem(f"{p['prix']} €")); self.table_cat.setItem(r, 2, QTableWidgetItem(str(av)))
            btn = QPushButton("AJOUTER AU PANIER") # Nouveau texte
            av > 0 and btn.clicked.connect(lambda ch, pr=p, m=av: self.add_to_cart_dialog(pr, m)) or btn.setDisabled(True)
            self.table_cat.setCellWidget(r, 3, btn)
        l.addWidget(self.table_cat); return w

    def add_to_cart_dialog(self, p, m):
        d = OrderDialog(p, m, self)
        if d.exec_(): self.add_to_cart(p, d.qty.value())

    def view_my_orders(self):
        w = QWidget(); l = QVBoxLayout(w); lst = QListWidget()
        # --- TRI INVERSÉ ---
        my_orders = [o for o in self.db.get_all_orders() if o['user'] == self.username][::-1]
        for o in my_orders: lst.addItem(f"{o['date']} | Total: {o['total']} € | {o['status']}")
        l.addWidget(lst); return w
        
    def view_settings(self):
        w = QWidget(); l = QVBoxLayout(w); l.addWidget(QLabel("CHANGER MDP"))
        self.new_p = QLineEdit(); self.new_p.setEchoMode(QLineEdit.Password); btn = QPushButton("VALIDER"); btn.clicked.connect(self.chg_pass)
        l.addWidget(self.new_p); l.addWidget(btn); l.addStretch(); return w

    def chg_pass(self):
        if self.new_p.text(): self.db.change_password(self.username, SecurityService.hash_password(self.new_p.text())); QMessageBox.information(self, "OK", "Fait.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guardia App")
        self.resize(1200, 800)
        self.stack = QStackedWidget(); self.setCentralWidget(self.stack)
        self.login_widget = LoginWidget(self); self.stack.addWidget(self.login_widget)

    def show_login(self): self.clear_stack(); self.stack.addWidget(LoginWidget(self))
    def show_2fa_setup(self, u, r, s): self.clear_stack(); self.stack.addWidget(Setup2FAWidget(self, u, r, s))
    def show_2fa_verify(self, u, r, s): self.clear_stack(); self.stack.addWidget(Verify2FAWidget(self, u, r, s))
    def show_app(self, u, r): self.clear_stack(); self.stack.addWidget(AppWidget(u, r, self.show_login))
    def clear_stack(self):
        while self.stack.count() > 0: w = self.stack.widget(0); self.stack.removeWidget(w); w.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyleSheet(STYLESHEET)
    win = MainWindow(); win.show(); sys.exit(app.exec_())
