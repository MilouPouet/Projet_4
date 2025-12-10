import sys
import os
import io
import json
import qrcode
from PIL import Image

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QHeaderView, QStackedWidget, QListWidget, QFrame,
    QProgressBar, QCheckBox, QAbstractItemView, QStatusBar, QDialog, QInputDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.security import SecurityService
from src.data_manager import DataManager

class TwoFactorSetupDialog(QDialog):
    def __init__(self, username, secret):
        super().__init__()
        self.setWindowTitle("Configuration 2FA")
        self.setFixedSize(450, 600)
        layout = QVBoxLayout(self)
        
        lbl_info = QLabel("📲 Scannez ce QR Code")
        lbl_info.setStyleSheet("font-size: 18px; font-weight: bold;")
        lbl_info.setAlignment(Qt.AlignCenter)
        
        uri = SecurityService.get_totp_uri(username, secret)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qimg = QPixmap()
        qimg.loadFromData(buffer.getvalue())
        pixmap = qimg.scaled(250, 250, Qt.KeepAspectRatio)
        
        lbl_img = QLabel()
        lbl_img.setPixmap(pixmap)
        lbl_img.setAlignment(Qt.AlignCenter)
        
        lbl_manual = QLabel("⚠️ Si le scan ne marche pas (iPhone) :")
        lbl_manual.setStyleSheet("color: #c0392b; font-weight: bold; margin-top: 10px;")
        
        self.txt_manual = QLineEdit(secret)
        self.txt_manual.setReadOnly(True)
        self.txt_manual.setStyleSheet("background: #ecf0f1; font-family: monospace; font-size: 14px; padding: 5px;")
        self.txt_manual.setAlignment(Qt.AlignCenter)
        
        lbl_help = QLabel("Dans Apple Passwords ou Google Auth > Saisir clé de configuration")
        lbl_help.setStyleSheet("font-size: 10px; color: grey;")
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Entrez le code 6 chiffres généré")
        self.code_input.setStyleSheet("font-size: 16px; padding: 5px; margin-top: 15px;")
        
        btn_verify = QPushButton("Activer la Sécurité")
        btn_verify.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; font-weight: bold;")
        btn_verify.clicked.connect(self.accept)
        
        layout.addWidget(lbl_info)
        layout.addWidget(lbl_img)
        layout.addWidget(lbl_manual)
        layout.addWidget(self.txt_manual)
        layout.addWidget(lbl_help)
        layout.addWidget(self.code_input)
        layout.addWidget(btn_verify)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guardia Secure Access V3.3")
        self.setFixedSize(400, 600)
        self.db = DataManager() # Init DataManager
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40,40,40,40)
        
        lbl_title = QLabel("🛡️ GATEKEEPER")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50;")
        
        self.user_input = QLineEdit(); self.user_input.setPlaceholderText("Utilisateur")
        self.pass_input = QLineEdit(); self.pass_input.setPlaceholderText("Mot de passe")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.textChanged.connect(self.check_strength)
        
        self.strength_bar = QProgressBar(); self.strength_bar.setTextVisible(False); self.strength_bar.setRange(0, 4)
        self.lbl_strength = QLabel("Sécurité mdp")
        
        self.chk_admin = QCheckBox("Créer compte ADMIN (Sinon Visiteur)")
        
        btn_login = QPushButton("SE CONNECTER")
        btn_login.setStyleSheet("background-color: #3498db; color: white; padding: 10px; font-weight: bold;")
        btn_login.clicked.connect(self.login)
        
        btn_reg = QPushButton("S'INSCRIRE")
        btn_reg.clicked.connect(self.register)
        
        layout.addWidget(lbl_title); layout.addSpacing(20)
        layout.addWidget(self.user_input); layout.addWidget(self.pass_input)
        layout.addWidget(self.strength_bar); layout.addWidget(self.lbl_strength)
        layout.addWidget(self.chk_admin)
        layout.addSpacing(20); layout.addWidget(btn_login); layout.addWidget(btn_reg)
        self.setLayout(layout)

    def check_strength(self, text):
        res = SecurityService.check_password_strength(text)
        self.strength_bar.setValue(res['score'])
        colors = ["red", "orange", "yellow", "lightgreen", "green"]
        self.strength_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {colors[res['score']]}; }}")
        self.lbl_strength.setText(", ".join(res['feedback']) if res['score'] < 4 else "Robuste")

    def register(self):
        try:
            u, p = self.user_input.text(), self.pass_input.text()
            if not u or not p: return
            
            if SecurityService.is_password_pwned(p):
                return QMessageBox.critical(self, "STOP", "Mot de passe compromis (Pwned API)!")
                
            hashed = SecurityService.hash_password(p)
            role = "admin" if self.chk_admin.isChecked() else "viewer"
            
            user_data = {
                "hash": hashed,
                "role": role,
                "2fa_secret": None 
            }
            
            # UTILISATION DE LA METHODE ROBUSTE DU DATAMANAGER
            self.db.register_user(u, user_data)
            
            SecurityService.log_action(u, "INSCRIPTION")
            QMessageBox.information(self, "OK", f"Compte {role} créé avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Crash Evité", f"Erreur lors de l'inscription: {str(e)}")

    def login(self):
        u, p = self.user_input.text(), self.pass_input.text()
        user_data = self.db.get_user_data(u)
        
        if not user_data: return QMessageBox.warning(self, "Erreur", "Utilisateur inconnu")
        
        stored_hash = user_data if isinstance(user_data, str) else user_data['hash']
        role = user_data.get('role', 'admin') if isinstance(user_data, dict) else 'admin'
        
        if SecurityService.verify_password(stored_hash, p):
            secret = user_data.get('2fa_secret')
            
            if not secret:
                new_secret = SecurityService.generate_2fa_secret()
                dlg = TwoFactorSetupDialog(u, new_secret)
                if dlg.exec_() == QDialog.Accepted:
                    code = dlg.code_input.text()
                    if SecurityService.verify_2fa_code(new_secret, code):
                        self.db.update_user_2fa(u, new_secret)
                        self.launch_main(u, role)
                    else:
                        QMessageBox.critical(self, "Erreur", "Code 2FA incorrect")
            else:
                code, ok = QInputDialog.getText(self, "2FA Requis", "Entrez le code Google/Apple Auth:")
                if ok and SecurityService.verify_2fa_code(secret, code):
                    SecurityService.log_action(u, "LOGIN SUCCESS")
                    self.launch_main(u, role)
                else:
                    SecurityService.log_action(u, "LOGIN FAILED 2FA")
                    QMessageBox.critical(self, "Erreur", "Code 2FA invalide")
        else:
            QMessageBox.warning(self, "Erreur", "Mot de passe invalide")

    def launch_main(self, user, role):
        self.main = MainWindow(user, role)
        self.main.show()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role 
        self.db = DataManager()
        self.setWindowTitle(f"Guardia Enterprise [Rôle: {role.upper()}]")
        self.resize(1200, 800)
        
        main_widget = QWidget(); layout = QHBoxLayout(); main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet("background:#2c3e50; color:white; font-size:16px; padding:10px;")
        self.sidebar.addItems(["📊 Dashboard", "📦 Gestion Stock", "🛡️ Audit", "⚙️ Options"])
        self.sidebar.currentRowChanged.connect(self.switch_page)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.page_dash())
        self.stack.addWidget(self.page_manage())
        self.stack.addWidget(self.page_audit())
        self.stack.addWidget(QWidget()) 
        
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

    def switch_page(self, idx):
        self.stack.setCurrentIndex(idx)

    def page_dash(self):
        w = QWidget(); l = QVBoxLayout(w)
        l.addWidget(QLabel(f"Bienvenue {self.username} (Privilèges: {self.role})"))
        
        kpi_layout = QHBoxLayout()
        prods = self.db.get_all_products()
        val = sum(float(p['prix']) * int(p['quantite']) for p in prods)
        kpi_layout.addWidget(QLabel(f"Valeur Stock: {val} €"))
        kpi_layout.addWidget(QLabel(f"Références: {len(prods)}"))
        
        fig = plt.figure(figsize=(5,4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        cats = {}
        for p in prods: cats[p['categorie']] = cats.get(p['categorie'], 0) + 1
        ax.bar(cats.keys(), cats.values())
        ax.set_title("Produits par Catégorie")
        
        l.addLayout(kpi_layout)
        l.addWidget(canvas)
        return w

    def page_manage(self):
        w = QWidget(); l = QVBoxLayout(w)
        
        self.form_frame = QFrame()
        fl = QHBoxLayout(self.form_frame)
        self.in_nom = QLineEdit(); self.in_nom.setPlaceholderText("Nom")
        self.in_prix = QLineEdit(); self.in_prix.setPlaceholderText("Prix")
        self.in_qty = QLineEdit(); self.in_qty.setPlaceholderText("Qté")
        self.in_cat = QLineEdit(); self.in_cat.setPlaceholderText("Catégorie")
        self.in_secret = QLineEdit(); self.in_secret.setPlaceholderText("Info Secrète (Sera chiffrée)")
        
        btn_add = QPushButton("Ajouter")
        btn_add.setStyleSheet("background-color:green; color:white;")
        btn_add.clicked.connect(self.add_product)
        
        fl.addWidget(self.in_nom); fl.addWidget(self.in_prix); fl.addWidget(self.in_qty)
        fl.addWidget(self.in_cat); fl.addWidget(self.in_secret); fl.addWidget(btn_add)
        
        if self.role != "admin":
            self.form_frame.hide()
            l.addWidget(QLabel("🔒 Mode Lecture Seule (Role: Viewer)"))
        else:
            l.addWidget(self.form_frame)
            
        self.table = QTableWidget(); self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prix", "Qté", "Cat", "Secret (Décrypté)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        btn_del = QPushButton("Supprimer")
        btn_del.setStyleSheet("background-color:red; color:white;")
        btn_del.clicked.connect(self.delete_product)
        
        if self.role != "admin": btn_del.setDisabled(True)
        
        btn_html = QPushButton("Rapport HTML")
        btn_html.clicked.connect(self.export)
        
        l.addWidget(self.table)
        l.addWidget(btn_del)
        l.addWidget(btn_html)
        
        self.refresh_table()
        return w

    def add_product(self):
        try:
            p = {
                "nom": self.in_nom.text(),
                "prix": float(self.in_prix.text()),
                "quantite": int(self.in_qty.text()),
                "categorie": self.in_cat.text(),
                "secret_info": self.in_secret.text()
            }
            self.db.add_product(p)
            SecurityService.log_action(self.username, f"ADD {p['nom']}")
            self.refresh_table()
        except: QMessageBox.warning(self, "Erreur", "Données invalides")

    def delete_product(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel: return
        pid = self.table.item(sel[0].row(), 0).text()
        self.db.delete_product(pid)
        SecurityService.log_action(self.username, f"DEL {pid}")
        self.refresh_table()

    def export(self):
        self.db.generate_html_report()

    def refresh_table(self):
        data = self.db.get_all_products()
        self.table.setRowCount(len(data))
        for r, p in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem(p['id']))
            self.table.setItem(r, 1, QTableWidgetItem(p['nom']))
            self.table.setItem(r, 2, QTableWidgetItem(p['prix']))
            self.table.setItem(r, 3, QTableWidgetItem(p['quantite']))
            self.table.setItem(r, 4, QTableWidgetItem(p['categorie']))
            self.table.setItem(r, 5, QTableWidgetItem(p.get('secret_info', '')))

    def page_audit(self):
        w = QWidget(); l = QVBoxLayout(w)
        l.addWidget(QLabel("Journal d'Audit"))
        table = QTableWidget(); table.setColumnCount(1); table.horizontalHeader().setStretchLastSection(True)
        
        path = "logs/audit.log"
        if os.path.exists(path):
            with open(path, 'r') as f: lines = f.readlines()
            table.setRowCount(len(lines))
            for i, line in enumerate(reversed(lines)):
                table.setItem(i, 0, QTableWidgetItem(line.strip()))
        
        l.addWidget(table)
        return w

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
