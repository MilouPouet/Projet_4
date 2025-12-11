import sys
import os
import io
import qrcode
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QHeaderView, QStackedWidget, QListWidget, QFrame,
    QProgressBar, QCheckBox, QAbstractItemView, QDialog, QSpinBox, QInputDialog
)
from PyQt5.QtGui import QPixmap, QColor, QFont, QPalette
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.security import SecurityService
from src.data_manager import DataManager

STYLESHEET = """
    QMainWindow, QDialog { background-color: #1e1e2e; color: #cdd6f4; }
    QLabel { color: #ffffff; font-size: 14px; }
    QLineEdit { 
        background-color: #313244; color: white; border: 2px solid #45475a; 
        border-radius: 6px; padding: 10px; font-size: 14px;
    }
    QLineEdit:focus { border: 2px solid #89b4fa; }
    QPushButton {
        background-color: #89b4fa; color: #1e1e2e; border-radius: 6px; 
        padding: 12px; font-weight: bold; font-size: 14px; border: none;
    }
    QPushButton:hover { background-color: #b4befe; }
    QPushButton#BtnOutline {
        background-color: transparent; border: 2px solid #89b4fa; color: #89b4fa;
    }
    QPushButton#BtnOutline:hover { background-color: rgba(137, 180, 250, 0.1); }
    QCheckBox { color: #ffffff; spacing: 10px; font-size: 15px; font-weight: bold; background-color: transparent; }
    QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid #89b4fa; border-radius: 4px; background: #313244; }
    QCheckBox::indicator:checked { background-color: #89b4fa; border-color: #89b4fa; }
    QListWidget { background-color: #181825; border: none; font-size: 15px; color: #a6adc8; }
    QListWidget::item { padding: 15px; border-bottom: 1px solid #313244; }
    QListWidget::item:selected { background-color: #313244; color: #89b4fa; border-left: 4px solid #89b4fa; }
    QTableWidget { background-color: #1e1e2e; gridline-color: #45475a; color: white; border: 1px solid #45475a; }
    QHeaderView::section { background-color: #313244; color: white; padding: 8px; border: none; font-weight: bold; }
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

class TwoFactorDialog(QDialog):
    def __init__(self, username, secret, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sécurité 2FA")
        self.setFixedSize(400, 600)
        self.secret = secret
        layout = QVBoxLayout(self); layout.setSpacing(15)
        lbl = QLabel("🔐 ACTIVATION DOUBLE AUTHENTIFICATION"); lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa;")
        lbl.setAlignment(Qt.AlignCenter)
        
        uri = SecurityService.get_totp_uri(username, secret)
        qr = qrcode.QRCode(box_size=10, border=2); qr.add_data(uri); qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        temp_file = "temp_qr.png"
        img.save(temp_file)
        qimg = QPixmap(temp_file)
        lbl_img = QLabel(); lbl_img.setPixmap(qimg.scaled(200, 200, Qt.KeepAspectRatio)); lbl_img.setAlignment(Qt.AlignCenter)
        if os.path.exists(temp_file): os.remove(temp_file)
        
        key_input = QLineEdit(secret); key_input.setReadOnly(True); key_input.setAlignment(Qt.AlignCenter)
        self.code = QLineEdit(); self.code.setPlaceholderText("Code à 6 chiffres"); self.code.setAlignment(Qt.AlignCenter)
        self.code.setStyleSheet("font-size: 18px; padding: 10px;")
        
        btn = QPushButton("VÉRIFIER LE CODE"); btn.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e; padding: 12px; font-weight: bold;")
        btn.clicked.connect(self.check)
        
        layout.addWidget(lbl)
        layout.addWidget(lbl_img)
        layout.addWidget(QLabel("Si le QR ne marche pas, copiez cette clé :"))
        layout.addWidget(key_input)
        layout.addWidget(self.code)
        layout.addWidget(btn)

    def check(self):
        if SecurityService.verify_2fa_code(self.secret, self.code.text()): self.accept()
        else: QMessageBox.warning(self, "Erreur", "Code incorrect. Réessayez.")

class LoginWidget(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.switch_callback = switch_callback
        self.db = DataManager()
        
        l = QVBoxLayout(self); l.setAlignment(Qt.AlignCenter)
        frame = QFrame(); frame.setFixedSize(380, 580)
        frame.setStyleSheet("background-color: #181825; border-radius: 20px; border: 2px solid #313244;")
        fl = QVBoxLayout(frame); fl.setSpacing(20); fl.setContentsMargins(40,40,40,40)
        
        title = QLabel("GUARDIA ACCESS"); title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #cba6f7; letter-spacing: 2px;")
        
        self.u = QLineEdit(); self.u.setPlaceholderText("Nom d'utilisateur")
        self.p = QLineEdit(); self.p.setPlaceholderText("Mot de passe"); self.p.setEchoMode(QLineEdit.Password)
        self.chk = QCheckBox(" Créer un compte Administrateur")
        
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
                dlg = TwoFactorDialog(u, s, self)
                if dlg.exec_() == QDialog.Accepted:
                    self.db.update_user_2fa(u, s)
                    self.switch_callback(u, role)
            else:
                c, ok = QInputDialog.getText(self, "Sécurité", "Code Authenticator (Google/Apple) :")
                if ok and SecurityService.verify_2fa_code(d['2fa_secret'], c): self.switch_callback(u, role)
                else: QMessageBox.warning(self, "Erreur", "Code invalide")
        else: QMessageBox.warning(self, "Erreur", "Identifiants incorrects")

class AppWidget(QWidget):
    def __init__(self, username, role, logout_callback):
        super().__init__()
        self.username = username
        self.role = role
        self.logout = logout_callback
        self.db = DataManager()
        
        layout = QHBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        self.sidebar = QListWidget(); self.sidebar.setFixedWidth(240)
        if role == "admin":
            self.sidebar.addItems(["📊 Tableau de Bord", "📦 Gestion Stock", "🚚 Commandes", "👥 Utilisateurs", "🚪 Déconnexion"])
        else:
            self.sidebar.addItems(["🛍️ Catalogue", "🛒 Mes Commandes", "⚙️ Mon Compte", "🚪 Déconnexion"])
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
        w = QWidget(); l = QVBoxLayout(w)
        l.addWidget(QLabel("TABLEAU DE BORD"))
        try:
            fig = plt.figure(facecolor='#1e1e2e'); canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111); ax.set_facecolor('#1e1e2e')
            prods = self.db.get_all_products()
            cats = {}
            for p in prods: cats[p['categorie']] = cats.get(p['categorie'], 0) + int(p['quantite'])
            ax.bar(cats.keys(), cats.values(), color='#89b4fa')
            ax.tick_params(colors='white'); ax.spines['bottom'].set_color('white'); ax.spines['left'].set_color('white')
            l.addWidget(canvas)
        except: l.addWidget(QLabel("Erreur graphique"))
        return w

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
            tab.insertRow(r)
            tab.setItem(r, 0, QTableWidgetItem(p['nom']))
            tab.setItem(r, 1, QTableWidgetItem(f"{p['prix']} €"))
            tab.setItem(r, 2, QTableWidgetItem(p['quantite']))
            real, res, av = self.db.get_stock_status(p['id'])
            tab.setItem(r, 3, QTableWidgetItem(f"{av} dispo (Réservé: {res})"))
        l.addLayout(form); l.addWidget(tab)
        return w

    def add_p(self):
        try:
            self.db.add_product({"nom":self.n.text(), "prix":float(self.p.text()), "quantite":int(self.q.text()), "categorie":"Divers"})
            self.refresh_pages()
        except: pass

    def view_orders(self):
        w = QWidget(); l = QVBoxLayout(w)
        tab = QTableWidget(0, 4); tab.setHorizontalHeaderLabels(["ID Commande", "Client", "Total", "Statut"])
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        orders = self.db.get_all_orders()
        for r, o in enumerate(orders):
            tab.insertRow(r)
            tab.setItem(r, 0, QTableWidgetItem(o['id']))
            tab.setItem(r, 1, QTableWidgetItem(o['user']))
            tab.setItem(r, 2, QTableWidgetItem(f"{o['total']} €"))
            btn = QPushButton("EN ATTENTE" if o['status'] == 'PENDING' else "EXPÉDIÉE")
            if o['status'] == 'PENDING':
                btn.setStyleSheet("background: orange; color: black")
                btn.clicked.connect(lambda ch, oid=o['id']: self.ship(oid))
            else:
                btn.setStyleSheet("background: green; border: none; color: white")
                btn.setDisabled(True)
            tab.setCellWidget(r, 3, btn)
        l.addWidget(tab)
        return w

    def ship(self, oid):
        if self.db.validate_order(oid): QMessageBox.information(self, "Succès", "Commande validée et stock débité !")
        self.refresh_pages()

    def view_users(self):
        w = QWidget(); l = QVBoxLayout(w)
        l.addWidget(QLabel("GESTION DES UTILISATEURS"))
        tab = QTableWidget(0, 3); tab.setHorizontalHeaderLabels(["Identifiant", "Rôle", "Action"])
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        users = self.db.get_all_users_list()
        row = 0
        for u, data in users.items():
            if u == self.username: continue 
            tab.insertRow(row)
            tab.setItem(row, 0, QTableWidgetItem(u))
            role = data.get('role', 'client')
            tab.setItem(row, 1, QTableWidgetItem(role.upper()))
            btn_del = QPushButton("SUPPRIMER")
            btn_del.setStyleSheet("background-color: #f38ba8; color: black; font-weight: bold;")
            btn_del.clicked.connect(lambda ch, usr=u: self.del_user(usr))
            tab.setCellWidget(row, 2, btn_del)
            row += 1
        l.addWidget(tab)
        return w

    def del_user(self, u):
        if QMessageBox.question(self, "Confirmer", f"Supprimer l'utilisateur {u} ?") == QMessageBox.Yes:
            self.db.delete_user(u)
            self.refresh_pages()

    def view_catalog(self):
        w = QWidget(); l = QVBoxLayout(w)
        tab = QTableWidget(0, 4); tab.setHorizontalHeaderLabels(["Nom Produit", "Prix", "Disponibilité", "Panier"])
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for r, p in enumerate(self.db.get_all_products()):
            real, res, av = self.db.get_stock_status(p['id'])
            tab.insertRow(r)
            tab.setItem(r, 0, QTableWidgetItem(p['nom']))
            tab.setItem(r, 1, QTableWidgetItem(f"{p['prix']} €"))
            tab.setItem(r, 2, QTableWidgetItem(f"{av} en stock"))
            btn = QPushButton("COMMANDER")
            if av > 0:
                btn.clicked.connect(lambda ch, prod=p, m=av: self.buy(prod, m))
            else: btn.setDisabled(True); btn.setText("RUPTURE"); btn.setStyleSheet("background: #45475a; color: #a6adc8;")
            tab.setCellWidget(r, 3, btn)
        l.addWidget(tab)
        return w

    def buy(self, p, m):
        d = OrderDialog(p, m, self)
        if d.exec_():
            self.db.place_order(self.username, [{"id":p['id'], "nom":p['nom'], "qty":d.qty.value(), "price":float(p['prix'])}])
            QMessageBox.information(self, "Info", "Commande envoyée !")
            self.refresh_pages()

    def view_my_orders(self):
        w = QWidget(); l = QVBoxLayout(w)
        lst = QListWidget()
        for o in [x for x in self.db.get_all_orders() if x['user'] == self.username]:
            icon = "🟢 EXPÉDIÉE" if o['status'] == 'SHIPPED' else "🟠 EN ATTENTE"
            lst.addItem(f"{o['date']} | Total: {o['total']} € | {icon}")
        l.addWidget(lst)
        return w
        
    def view_settings(self):
        w = QWidget(); l = QVBoxLayout(w)
        l.addWidget(QLabel("CHANGER MON MOT DE PASSE"))
        self.new_p = QLineEdit(); self.new_p.setEchoMode(QLineEdit.Password)
        btn = QPushButton("VALIDER"); btn.clicked.connect(self.chg_pass)
        l.addWidget(self.new_p); l.addWidget(btn); l.addStretch()
        return w
        
    def chg_pass(self):
        if self.new_p.text():
            self.db.change_password(self.username, SecurityService.hash_password(self.new_p.text()))
            QMessageBox.information(self, "OK", "Mot de passe modifié.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guardia App")
        self.resize(1200, 800)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.login_widget = LoginWidget(self.on_login_success)
        self.stack.addWidget(self.login_widget)

    def on_login_success(self, username, role):
        self.app_widget = AppWidget(username, role, self.on_logout)
        self.stack.addWidget(self.app_widget)
        self.stack.setCurrentWidget(self.app_widget)

    def on_logout(self):
        self.stack.removeWidget(self.app_widget)
        self.app_widget.deleteLater()
        self.app_widget = None
        self.stack.setCurrentWidget(self.login_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
