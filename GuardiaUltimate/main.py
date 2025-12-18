import sys
import os
import qrcode
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QHeaderView, QStackedWidget, QListWidget, QFrame,
    QCheckBox, QDialog, QSpinBox, QScrollArea, QSizePolicy, QGridLayout
)
from PyQt5.QtGui import QPixmap, QColor, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Essai d'import pour le lissage
try:
    from scipy.interpolate import make_interp_spline
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from src.security import SecurityService
from src.data_manager import DataManager

# --- STYLESHEET CLEAN ---
STYLESHEET = """
    * { font-family: 'Segoe UI', 'Roboto', sans-serif; font-size: 14px; color: #ffffff; outline: none; }
    
    QMainWindow, QDialog { background-color: #151521; }
    
    QWidget#Sidebar { background-color: #1e1e2d; border-right: 1px solid #2b2b40; }
    
    QFrame#Card {
        background-color: #1e1e2d;
        border-radius: 12px;
        border: 1px solid #2b2b40;
    }
    
    /* BOUTONS TABLEAU */
    QPushButton.TableBtn {
        background-color: #3699ff;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 12px; 
        min-height: 24px;
        font-weight: bold;
        font-size: 13px;
    }
    QPushButton.TableBtn:hover { background-color: #2b7bdb; }
    
    QPushButton.TableBtnDanger {
        background-color: #f4516c;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        min-height: 24px;
        font-weight: bold;
        font-size: 13px;
    }
    QPushButton.TableBtnDanger:hover { background-color: #d93d56; }
    
    QPushButton.TableBtnSec {
        background-color: #2b2b40;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        min-height: 24px;
        font-weight: bold;
        font-size: 13px;
    }
    QPushButton.TableBtnSec:hover { background-color: #3a3a50; }
    
    QPushButton.TableBtnStat {
        background-color: transparent;
        border: 1px solid #000;
        border-radius: 6px;
        padding: 4px 8px;
        min-height: 22px;
        font-weight: bold;
        font-size: 12px;
    }

    QPushButton:focus, QListWidget:focus, QLineEdit:focus, QTableWidget:focus {
        outline: none;
        border: 1px solid #3699ff; 
    }

    QPushButton#NavBtn {
        background-color: transparent;
        color: #a1a5b7;
        text-align: left;
        padding: 12px 20px;
        border: none;
        font-weight: 600;
        border-radius: 8px;
        outline: none;
    }
    QPushButton#NavBtn:hover { background-color: #2b2b40; color: white; }
    QPushButton#NavBtn:checked { 
        background-color: #2b2b40; 
        color: #3699ff; 
        border-left: 3px solid #3699ff; 
    }

    QPushButton {
        background-color: #3699ff;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #2b7bdb; }
    QPushButton:disabled { background-color: #444; color: #888; }
    
    QPushButton.btn-danger { background-color: #f4516c; }
    QPushButton.btn-danger:hover { background-color: #d93d56; }
    
    QPushButton.btn-secondary { background-color: #2b2b40; color: #ffffff; }
    QPushButton.btn-secondary:hover { background-color: #3a3a50; }

    QLineEdit, QSpinBox {
        background-color: #151521;
        color: white;
        border: 1px solid #2b2b40;
        border-radius: 6px;
        padding: 10px;
    }
    QLineEdit:focus { border: 1px solid #3699ff; }

    QTableWidget {
        background-color: #1e1e2d;
        border: none;
        gridline-color: #2b2b40;
        color: #a1a5b7;
    }
    QTableWidget::item { padding: 5px; border-bottom: 1px solid #2b2b40; }
    
    QHeaderView::section {
        background-color: #151521;
        color: #ffffff;
        padding: 10px;
        border: none;
        border-bottom: 2px solid #2b2b40;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 12px;
    }
    QHeaderView::section:vertical {
        background-color: #1e1e2d; 
        border-right: 1px solid #2b2b40;
        padding-left: 5px;
    }
    
    QLabel#H1 { font-size: 28px; font-weight: bold; color: white; }
    QLabel#H2 { font-size: 18px; font-weight: 600; color: white; }
    QLabel#Subtitle { font-size: 13px; color: #a1a5b7; }
    QLabel#MetricValue { font-size: 32px; font-weight: bold; color: white; margin-top: 5px; }
    QLabel#MetricLabel { font-size: 14px; color: #a1a5b7; font-weight: 500; }
"""

class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")

class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(f"  {text}", parent)
        self.setObjectName("NavBtn")
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.PointingHandCursor)

# --- DIALOGUES ---
class QuantityDialog(QDialog):
    def __init__(self, product, max_qty, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter au Panier")
        self.setFixedSize(300, 200)
        l = QVBoxLayout(self); l.setSpacing(15)
        l.addWidget(QLabel(f"Produit : {product['nom']}", objectName="H2"))
        l.addWidget(QLabel(f"Prix : {product['prix']} €"))
        self.qty = QSpinBox(); self.qty.setRange(1, max_qty if max_qty > 0 else 1)
        self.qty.setStyleSheet("font-size: 16px; padding: 10px;")
        l.addWidget(self.qty)
        btn = QPushButton("VALIDER"); btn.clicked.connect(self.accept)
        l.addWidget(btn)

class ProductEditDialog(QDialog):
    def __init__(self, p, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier Produit")
        self.setFixedSize(400, 350)
        l = QVBoxLayout(self)
        self.n = QLineEdit(p['nom']); self.p = QLineEdit(str(p['prix']))
        self.c = QLineEdit(p['categorie']); self.s = QLineEdit(p.get('secret_info', ''))
        l.addWidget(QLabel("Nom")); l.addWidget(self.n)
        l.addWidget(QLabel("Prix")); l.addWidget(self.p)
        l.addWidget(QLabel("Catégorie")); l.addWidget(self.c)
        l.addWidget(QLabel("Info Secrète")); l.addWidget(self.s)
        btn = QPushButton("ENREGISTRER"); btn.clicked.connect(self.accept); l.addWidget(btn)
    def get_data(self): return {"nom": self.n.text(), "prix": float(self.p.text() or 0), "categorie": self.c.text(), "secret_info": self.s.text()}

class StockAdjustDialog(QDialog):
    def __init__(self, p, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Stock: {p['nom']}")
        self.setFixedSize(300, 200)
        l = QVBoxLayout(self)
        l.addWidget(QLabel(f"Actuel: {p['quantite']}"))
        self.sb = QSpinBox(); self.sb.setRange(-1000, 1000); l.addWidget(self.sb)
        btn = QPushButton("VALIDER"); btn.clicked.connect(self.accept); l.addWidget(btn)
    def get_val(self): return self.sb.value()

# --- LOGIN (MODIFIE : PLUS D'OPTION ADMIN) ---
class LoginWidget(QWidget):
    def __init__(self, parent_controller):
        super().__init__()
        self.parent_controller = parent_controller; self.db = DataManager()
        l = QVBoxLayout(self); l.setAlignment(Qt.AlignCenter)
        card = Card(); card.setFixedSize(400, 450) # Hauteur réduite
        cl = QVBoxLayout(card); cl.setSpacing(20); cl.setContentsMargins(40,40,40,40)
        
        lbl = QLabel("Guardia Analytics"); lbl.setObjectName("H1"); lbl.setAlignment(Qt.AlignCenter)
        self.u = QLineEdit(); self.u.setPlaceholderText("Utilisateur")
        self.p = QLineEdit(); self.p.setPlaceholderText("Mot de passe"); self.p.setEchoMode(QLineEdit.Password)
        # Checkbox Admin SUPPRIMÉE
        
        b_in = QPushButton("Se Connecter"); b_in.setFixedHeight(45); b_in.clicked.connect(self.login)
        b_up = QPushButton("Créer Compte"); b_up.setProperty("class", "btn-secondary"); b_up.clicked.connect(self.register)
        
        cl.addWidget(lbl); cl.addSpacing(20); cl.addWidget(self.u); cl.addWidget(self.p)
        cl.addSpacing(10); cl.addWidget(b_in); cl.addWidget(b_up)
        l.addWidget(card)

    def login(self):
        u, p = self.u.text(), self.p.text()
        d = self.db.get_user_data(u)
        if d and SecurityService.verify_password(d.get('hash'), p):
            if d.get('2fa_secret'): self.parent_controller.show_2fa_verify(u, d['role'], d['2fa_secret'])
            else: self.parent_controller.show_2fa_setup(u, d['role'], SecurityService.generate_2fa_secret())
        else: QMessageBox.warning(self, "Erreur", "Identifiants invalides")

    def register(self):
        u, p = self.u.text(), self.p.text()
        if u and p: 
            # FORCE ROLE CLIENT
            self.db.register_user(u, {"hash": SecurityService.hash_password(p), "role": "client"})
            QMessageBox.information(self, "OK", "Compte créé (Client)")

# --- 2FA ---
class TwoFAWidget(QWidget):
    def __init__(self, ctrl, u, r, s, setup=False):
        super().__init__()
        self.ctrl = ctrl; self.u = u; self.r = r; self.s = s
        l = QVBoxLayout(self); l.setAlignment(Qt.AlignCenter)
        card = Card(); card.setFixedSize(350, 450)
        cl = QVBoxLayout(card); cl.setSpacing(15); cl.setContentsMargins(30,30,30,30)
        
        cl.addWidget(QLabel("Configuration 2FA" if setup else "Vérification 2FA", objectName="H2"))
        if setup:
            qr = qrcode.make(SecurityService.get_totp_uri(u, s))
            qr.save("temp_qr.png"); pm = QPixmap("temp_qr.png")
            lbl_img = QLabel(); lbl_img.setPixmap(pm.scaled(180, 180, Qt.KeepAspectRatio)); lbl_img.setAlignment(Qt.AlignCenter)
            cl.addWidget(lbl_img); os.remove("temp_qr.png")
        
        self.code = QLineEdit(); self.code.setPlaceholderText("Code 6 chiffres"); self.code.setAlignment(Qt.AlignCenter)
        btn = QPushButton("Valider"); btn.clicked.connect(self.check)
        cl.addWidget(self.code); cl.addWidget(btn); l.addWidget(card)

    def check(self):
        if SecurityService.verify_2fa_code(self.s, self.code.text()):
            if hasattr(self, 'setup'): DataManager().update_user_2fa(self.u, self.s)
            self.ctrl.show_app(self.u, self.r)
        else: QMessageBox.warning(self, "Erreur", "Code incorrect")

# --- MAIN APP ---
class AppWidget(QWidget):
    def __init__(self, u, r, logout_cb):
        super().__init__()
        self.u = u; self.r = r; self.logout_cb = logout_cb; self.db = DataManager()
        self.cart = []
        
        layout = QHBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        
        sidebar = QWidget(); sidebar.setObjectName("Sidebar"); sidebar.setFixedWidth(250)
        sl = QVBoxLayout(sidebar); sl.setContentsMargins(20, 30, 20, 30); sl.setSpacing(10)
        sl.addWidget(QLabel("Guardia Analytics", objectName="H2"))
        sl.addSpacing(20)
        
        self.btn_dash = SidebarButton("Tableau de bord"); self.btn_dash.setChecked(True)
        self.btn_stock = SidebarButton("Produits & Stock")
        self.btn_order = SidebarButton("Commandes")
        self.btn_users = SidebarButton("Utilisateurs" if r == "admin" else "Mon Panier")
        
        for b in [self.btn_dash, self.btn_stock, self.btn_order, self.btn_users]:
            b.clicked.connect(self.nav_click)
            sl.addWidget(b)
            
        sl.addStretch()
        btn_out = QPushButton("Déconnexion"); btn_out.setProperty("class", "btn-secondary"); btn_out.clicked.connect(logout_cb)
        sl.addWidget(btn_out)
        layout.addWidget(sidebar)
        
        content_area = QWidget(); cal = QVBoxLayout(content_area); cal.setContentsMargins(30,30,30,30)
        header = QHBoxLayout()
        self.lbl_title = QLabel("Aperçu des Performances", objectName="H1")
        header.addWidget(self.lbl_title); header.addStretch()
        header.addWidget(QLabel(f"{u} ({r})", objectName="Subtitle"))
        cal.addLayout(header); cal.addSpacing(20)
        
        self.stack = QStackedWidget()
        cal.addWidget(self.stack)
        layout.addWidget(content_area)
        
        self.init_views()

    def nav_click(self):
        sender = self.sender()
        if sender == self.btn_dash: self.stack.setCurrentIndex(0); self.lbl_title.setText("Tableau de Bord")
        elif sender == self.btn_stock: self.stack.setCurrentIndex(1); self.lbl_title.setText("Gestion Stock" if self.r=='admin' else "Catalogue")
        elif sender == self.btn_order: self.stack.setCurrentIndex(2); self.lbl_title.setText("Historique Commandes")
        elif sender == self.btn_users: self.stack.setCurrentIndex(3); self.lbl_title.setText("Administration" if self.r=='admin' else "Mon Panier")
        self.refresh_all()

    def init_views(self):
        self.view_dashboard = QWidget()
        self.view_stock = QWidget() 
        self.view_orders = QWidget()
        self.view_extra = QWidget()
        self.stack.addWidget(self.view_dashboard)
        self.stack.addWidget(self.view_stock)
        self.stack.addWidget(self.view_orders)
        self.stack.addWidget(self.view_extra)
        self.refresh_all()

    def refresh_all(self):
        self.render_dashboard()
        if self.r == 'admin':
            self.render_stock_admin()
            self.render_orders_admin()
            self.render_users_admin()
        else:
            self.render_catalog_client()
            self.render_orders_client()
            self.render_cart_client()

    # --- HELPER POUR CREER LES BOUTONS DANS LE TABLEAU ---
    def create_action_widget(self, buttons):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignCenter)
        for btn in buttons:
            layout.addWidget(btn)
        return widget

    # ========================== DASHBOARDS ==========================
    def render_dashboard(self):
        w = self.view_dashboard; 
        if w.layout(): QWidget().setLayout(w.layout())
        if self.r == 'admin': self.render_dashboard_admin(w)
        else: self.render_dashboard_client(w)

    # --- DASHBOARD ADMIN ---
    def render_dashboard_admin(self, w):
        l = QVBoxLayout(w); l.setSpacing(20); l.setContentsMargins(0,0,0,0)
        prods = self.db.get_all_products()
        total_items = sum(int(float(p['quantite'])) for p in prods)
        total_val = sum(int(float(p['quantite'])) * float(p['prix']) for p in prods)
        
        row1 = QHBoxLayout(); row1.setSpacing(20)
        c1 = Card(); c1.setFixedHeight(120); c1l = QVBoxLayout(c1)
        c1l.addWidget(QLabel("Produits & Variété", objectName="MetricLabel"))
        c1l.addWidget(QLabel(f"{total_items:,}".replace(',', ' '), objectName="MetricValue"))
        c1l.addWidget(QLabel(f"{len(prods)} références uniques", objectName="Subtitle"))
        c2 = Card(); c2.setFixedHeight(120); c2l = QVBoxLayout(c2)
        c2l.addWidget(QLabel("Valeur du Stock", objectName="MetricLabel"))
        c2l.addWidget(QLabel(f"€{total_val:,.0f}".replace(',', ' '), objectName="MetricValue"))
        c2l.addWidget(QLabel("Basé sur le prix unitaire", objectName="Subtitle"))
        row1.addWidget(c1); row1.addWidget(c2); l.addLayout(row1)
        
        row2 = QHBoxLayout(); row2.setSpacing(20)
        g1_card = Card(); g1l = QVBoxLayout(g1_card); g1l.addWidget(QLabel("Ventes & Stock (Tendance)", objectName="H2"))
        fig1 = Figure(facecolor='#1e1e2d', figsize=(5, 3)); ax1 = fig1.add_subplot(111); ax1.set_facecolor('#1e1e2d')
        sales_data = self.db.get_sales_per_day(); stock_data = self.db.get_stock_history()
        dates = sorted(list(set(list(sales_data.keys()) + list(stock_data.keys()))))
        y_sales = np.array([sales_data.get(d, 0) for d in dates])
        y_stock = np.array([stock_data.get(d, 0) for d in dates])
        x_indices = np.arange(len(dates))
        if len(dates) > 2 and HAS_SCIPY:
            x_smooth = np.linspace(x_indices.min(), x_indices.max(), 300)
            spl_sales = make_interp_spline(x_indices, y_sales, k=3); y_sales_smooth = np.maximum(spl_sales(x_smooth), 0)
            spl_stock = make_interp_spline(x_indices, y_stock, k=3); y_stock_smooth = np.maximum(spl_stock(x_smooth), 0)
            ax1.plot(x_smooth, y_sales_smooth, color='#3699ff', linewidth=2, label='Ventes')
            ax1.fill_between(x_smooth, y_sales_smooth, color='#3699ff', alpha=0.2)
            ax1.plot(x_smooth, y_stock_smooth, color='#444', linestyle='--', linewidth=1, label='Stock')
        else:
            ax1.plot(x_indices, y_sales, color='#3699ff', linewidth=2, label='Ventes')
            ax1.fill_between(x_indices, y_sales, color='#3699ff', alpha=0.2)
            ax1.plot(x_indices, y_stock, color='#444', linestyle='--', linewidth=1, label='Stock')
        ax1.grid(color='#2b2b40', linestyle='-', linewidth=0.5); ax1.spines['bottom'].set_color('#2b2b40'); ax1.spines['top'].set_visible(False)
        ax1.spines['left'].set_color('#2b2b40'); ax1.spines['right'].set_visible(False)
        ax1.tick_params(axis='x', colors='#a1a5b7'); ax1.tick_params(axis='y', colors='#a1a5b7')
        if len(dates) > 5: ax1.set_xticks([0, len(dates)-1]); ax1.set_xticklabels([dates[0], dates[-1]])
        else: ax1.set_xticks(x_indices); ax1.set_xticklabels(dates)
        annot = ax1.annotate("", xy=(0,0), xytext=(15, 15), textcoords="offset points", bbox=dict(boxstyle="round", fc="#1e1e2d", ec="#3699ff", alpha=0.95))
        annot.set_visible(False)
        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax1:
                if len(dates) > 0:
                    idx = int(round(event.xdata))
                    if 0 <= idx < len(dates):
                        annot.xy = (event.xdata, event.ydata); annot.set_text(f"{dates[idx]}\nVentes: {y_sales[idx]}\nStock: {y_stock[idx]}")
                        annot.set_color('white'); annot.set_visible(True); fig1.canvas.draw_idle(); return
            if vis: annot.set_visible(False); fig1.canvas.draw_idle()
        fig1.canvas.mpl_connect("motion_notify_event", hover); g1l.addWidget(FigureCanvas(fig1))
        
        g2_card = Card(); g2l = QVBoxLayout(g2_card); g2l.addWidget(QLabel("Catégories", objectName="H2"))
        fig2 = Figure(facecolor='#1e1e2d', figsize=(4, 3)); ax2 = fig2.add_subplot(111)
        cats = self.db.get_categories_distribution()
        if cats:
            wedges, texts, autotexts = ax2.pie(list(cats.values()), labels=None, autopct='%1.0f%%', startangle=90, 
                                               colors=['#3699ff', '#ffb822', '#f4516c', '#00d2d3', '#5f5f5f'], wedgeprops={'width': 0.4, 'edgecolor': '#1e1e2d'})
            ax2.legend(wedges, list(cats.keys()), loc="center left", bbox_to_anchor=(1, 0.5), frameon=False, labelcolor='white', fontsize=8)
            fig2.subplots_adjust(left=0.0, bottom=0.0, right=0.5, top=1.0)
            for at in autotexts: at.set_fontsize(9); at.set_weight('bold'); at.set_color('white')
        else: ax2.text(0.5, 0.5, "Vide", ha='center', va='center', color='white')
        g2l.addWidget(FigureCanvas(fig2))
        row2.addWidget(g1_card, 2); row2.addWidget(g2_card, 1); l.addLayout(row2); l.addStretch()

    # --- DASHBOARD CLIENT ---
    def render_dashboard_client(self, w):
        l = QVBoxLayout(w); l.setSpacing(20); l.setContentsMargins(0,0,0,0)
        my_orders = [o for o in self.db.get_all_orders() if o['user'] == self.u]
        total_spent = sum(o['total'] for o in my_orders)
        
        row1 = QHBoxLayout(); row1.setSpacing(20)
        c1 = Card(); c1.setFixedHeight(120); c1l = QVBoxLayout(c1)
        c1l.addWidget(QLabel("Mes Commandes", objectName="MetricLabel"))
        c1l.addWidget(QLabel(f"{len(my_orders)}", objectName="MetricValue"))
        c2 = Card(); c2.setFixedHeight(120); c2l = QVBoxLayout(c2)
        c2l.addWidget(QLabel("Dépenses Totales", objectName="MetricLabel"))
        c2l.addWidget(QLabel(f"€{total_spent:,.2f}", objectName="MetricValue"))
        row1.addWidget(c1); row1.addWidget(c2); l.addLayout(row1)
        
        card_orders = Card(); col = QVBoxLayout(card_orders)
        col.addWidget(QLabel("Dernières Commandes", objectName="H2"))
        t = QTableWidget(0, 4); t.setHorizontalHeaderLabels(["ID", "Date", "Total", "Statut"])
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.verticalHeader().setDefaultSectionSize(50); t.verticalHeader().setVisible(False)
        recent = my_orders[-5:][::-1] 
        for r, o in enumerate(recent):
            t.insertRow(r); t.setItem(r, 0, QTableWidgetItem(o['id'])); t.setItem(r, 1, QTableWidgetItem(o['date']))
            t.setItem(r, 2, QTableWidgetItem(f"{o['total']} €"))
            btn = QPushButton(o['status'])
            style = "color: #ffb822; border-color: #ffb822;" if o['status'] == 'PENDING' else "color: #50cd89; border: none;"
            btn.setProperty("class", "TableBtnStat"); btn.setStyleSheet(style); btn.setDisabled(True)
            t.setCellWidget(r, 3, self.create_action_widget([btn]))
        col.addWidget(t); l.addWidget(card_orders); l.addStretch()

    # ========================== ADMIN VIEWS ==========================
    def render_stock_admin(self):
        w = self.view_stock; 
        if w.layout(): QWidget().setLayout(w.layout())
        l = QVBoxLayout(w)
        top = QHBoxLayout()
        self.search_st = QLineEdit(); self.search_st.setPlaceholderText("Rechercher...")
        self.search_st.textChanged.connect(self.filter_stock)
        btn_add = QPushButton("AJOUTER"); btn_add.clicked.connect(self.add_product_dialog)
        top.addWidget(self.search_st); top.addWidget(btn_add)
        l.addLayout(top)
        
        self.tab_stock = QTableWidget(0, 5)
        self.tab_stock.setHorizontalHeaderLabels(["Nom", "Prix", "Catégorie", "Stock", "Actions"])
        header = self.tab_stock.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch); header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.tab_stock.setColumnWidth(4, 160); self.tab_stock.verticalHeader().setDefaultSectionSize(50)
        self.tab_stock.verticalHeader().setVisible(False) # HIDE VERTICAL HEADER
        self.load_stock_data(); l.addWidget(self.tab_stock)

    def load_stock_data(self):
        self.tab_stock.setRowCount(0)
        for r, p in enumerate(self.db.get_all_products()):
            self.tab_stock.insertRow(r)
            self.tab_stock.setItem(r, 0, QTableWidgetItem(p['nom']))
            self.tab_stock.setItem(r, 1, QTableWidgetItem(f"{p['prix']} €"))
            self.tab_stock.setItem(r, 2, QTableWidgetItem(p['categorie']))
            real, res, av = self.db.get_stock_status(p['id'])
            self.tab_stock.setItem(r, 3, QTableWidgetItem(f"{av} (Res: {res})"))
            b1 = QPushButton("EDIT"); b1.setProperty("class", "TableBtnSec"); b1.clicked.connect(lambda ch, x=p: self.edit_p(x))
            b2 = QPushButton("STOCK"); b2.setProperty("class", "TableBtn"); b2.clicked.connect(lambda ch, x=p: self.adj_p(x))
            self.tab_stock.setCellWidget(r, 4, self.create_action_widget([b1, b2]))

    def filter_stock(self, t):
        for r in range(self.tab_stock.rowCount()): self.tab_stock.setRowHidden(r, t.lower() not in self.tab_stock.item(r, 0).text().lower())
    def add_product_dialog(self): self.db.add_product({"nom":"Nouveau", "prix":0, "quantite":0, "categorie":"Divers"}); self.load_stock_data()
    def edit_p(self, p):
        if ProductEditDialog(p, self).exec_(): self.db.update_product_data(p['id'], p); self.load_stock_data()
    def adj_p(self, p):
        if StockAdjustDialog(p, self).exec_(): self.db.adjust_stock(p['id'], p['quantite']); self.load_stock_data()

    def render_orders_admin(self):
        w = self.view_orders; 
        if w.layout(): QWidget().setLayout(w.layout())
        l = QVBoxLayout(w)
        t = QTableWidget(0, 5); t.setHorizontalHeaderLabels(["ID", "Date", "Utilisateur", "Total", "Statut"])
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); t.verticalHeader().setDefaultSectionSize(50)
        t.verticalHeader().setVisible(False) # HIDE VERTICAL HEADER
        for r, o in enumerate(self.db.get_all_orders()[::-1]):
            t.insertRow(r); t.setItem(r, 0, QTableWidgetItem(o['id'])); t.setItem(r, 1, QTableWidgetItem(o['date']))
            t.setItem(r, 2, QTableWidgetItem(o['user'])); t.setItem(r, 3, QTableWidgetItem(f"{o['total']} €"))
            btn = QPushButton(o['status'])
            if o['status'] == 'PENDING': btn.setProperty("class", "TableBtnStat"); btn.setStyleSheet("color: #ffb822; border-color: #ffb822;"); btn.clicked.connect(lambda ch, x=o['id']: self.validate_o(x))
            else: btn.setProperty("class", "TableBtnStat"); btn.setStyleSheet("color: #50cd89; border: none;"); btn.setDisabled(True)
            t.setCellWidget(r, 4, self.create_action_widget([btn]))
        l.addWidget(t)
    def validate_o(self, oid):
        if self.db.validate_order(oid): self.refresh_all()

    def render_users_admin(self):
        w = self.view_extra; 
        if w.layout(): QWidget().setLayout(w.layout())
        l = QVBoxLayout(w); t = QTableWidget(0, 3); t.setHorizontalHeaderLabels(["Utilisateur", "Rôle", "Actions"])
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); t.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        t.setColumnWidth(2, 120); t.verticalHeader().setDefaultSectionSize(50); t.verticalHeader().setVisible(False)
        row = 0
        for u, d in self.db.get_all_users_list().items():
            if u == self.u: continue
            t.insertRow(row); t.setItem(row, 0, QTableWidgetItem(u)); t.setItem(row, 1, QTableWidgetItem(d.get('role','client')))
            btn = QPushButton("SUPP"); btn.setProperty("class", "TableBtnDanger"); btn.clicked.connect(lambda ch, x=u: self.del_u(x))
            t.setCellWidget(row, 2, self.create_action_widget([btn])); row += 1
        l.addWidget(t)
    def del_u(self, u): self.db.delete_user(u); self.render_users_admin()

    # ========================== CLIENT VIEWS ==========================
    def render_catalog_client(self):
        w = self.view_stock; 
        if w.layout(): QWidget().setLayout(w.layout())
        l = QVBoxLayout(w)
        search = QLineEdit(); search.setPlaceholderText("Recherche..."); search.textChanged.connect(lambda t: self.filter_cat(self.cat_tab, t)); l.addWidget(search)
        self.cat_tab = QTableWidget(0, 4); self.cat_tab.setHorizontalHeaderLabels(["Produit", "Prix", "Dispo", "Ajout"])
        header = self.cat_tab.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch); header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.cat_tab.setColumnWidth(3, 120); self.cat_tab.verticalHeader().setDefaultSectionSize(50)
        self.cat_tab.verticalHeader().setVisible(False) # HIDE
        
        for r, p in enumerate(self.db.get_all_products()):
            self.cat_tab.insertRow(r)
            self.cat_tab.setItem(r, 0, QTableWidgetItem(p['nom']))
            self.cat_tab.setItem(r, 1, QTableWidgetItem(f"{p['prix']} €"))
            real, res, av = self.db.get_stock_status(p['id'])
            self.cat_tab.setItem(r, 2, QTableWidgetItem(str(av)))
            btn = QPushButton("AJOUTER"); btn.setProperty("class", "TableBtn"); btn.clicked.connect(lambda ch, x=p: self.add_to_cart_dialog(x, av))
            if av <= 0: btn.setDisabled(True)
            self.cat_tab.setCellWidget(r, 3, self.create_action_widget([btn]))
        l.addWidget(self.cat_tab)
    
    def filter_cat(self, tab, txt):
        for i in range(tab.rowCount()): tab.setRowHidden(i, txt.lower() not in tab.item(i,0).text().lower())

    def add_to_cart_dialog(self, p, max_stock):
        d = QuantityDialog(p, max_stock, self)
        if d.exec_():
            qty = d.qty.value()
            self.cart.append({"id":p['id'], "nom":p['nom'], "qty":qty, "price":float(p['prix'])})
            QMessageBox.information(self, "Panier", f"{qty}x {p['nom']} ajoutés !")

    def render_cart_client(self):
        w = self.view_extra; 
        if w.layout(): QWidget().setLayout(w.layout())
        l = QVBoxLayout(w); l.addWidget(QLabel(f"Mon Panier ({len(self.cart)})", objectName="H2"))
        t = QTableWidget(0, 3); t.setHorizontalHeaderLabels(["Item", "Prix", "Qté"]); t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.verticalHeader().setDefaultSectionSize(50); t.verticalHeader().setVisible(False)
        tot = 0
        for r, item in enumerate(self.cart):
            t.insertRow(r); t.setItem(r, 0, QTableWidgetItem(item['nom'])); t.setItem(r, 1, QTableWidgetItem(str(item['price']))); t.setItem(r, 2, QTableWidgetItem(str(item['qty']))); tot += item['price'] * item['qty']
        l.addWidget(t)
        h = QHBoxLayout(); h.addWidget(QLabel(f"Total: {tot} €", objectName="H1")); h.addStretch()
        b1 = QPushButton("VIDER"); b1.setProperty("class", "btn-danger"); b1.clicked.connect(lambda: [self.cart.clear(), self.render_cart_client()])
        b2 = QPushButton("COMMANDER"); b2.clicked.connect(self.checkout); h.addWidget(b1); h.addWidget(b2); l.addLayout(h)
    def checkout(self):
        if not self.cart: return
        self.db.place_order(self.u, self.cart); self.cart = []; QMessageBox.information(self, "Succès", "Commande envoyée !"); self.render_cart_client()

    def render_orders_client(self):
        w = self.view_orders; 
        if w.layout(): QWidget().setLayout(w.layout())
        l = QVBoxLayout(w)
        
        t = QTableWidget(0, 4); t.setHorizontalHeaderLabels(["ID", "Date", "Total", "Statut"])
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.verticalHeader().setDefaultSectionSize(50); t.verticalHeader().setVisible(False) # HIDE
        
        my_orders = [o for o in self.db.get_all_orders() if o['user'] == self.u][::-1]
        
        for r, o in enumerate(my_orders):
            t.insertRow(r)
            t.setItem(r, 0, QTableWidgetItem(o['id']))
            t.setItem(r, 1, QTableWidgetItem(o['date']))
            t.setItem(r, 2, QTableWidgetItem(f"{o['total']} €"))
            btn = QPushButton(o['status'])
            style = "color: #ffb822; border-color: #ffb822;" if o['status'] == 'PENDING' else "color: #50cd89; border: none;"
            btn.setProperty("class", "TableBtnStat"); btn.setStyleSheet(style); btn.setDisabled(True)
            t.setCellWidget(r, 3, self.create_action_widget([btn]))
            
        l.addWidget(t)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guardia Analytics"); self.resize(1300, 850)
        self.stack = QStackedWidget(); self.setCentralWidget(self.stack)
        self.show_login()
    def show_login(self): self.stack.addWidget(LoginWidget(self)); self.stack.setCurrentIndex(self.stack.count()-1)
    def show_2fa_setup(self, u, r, s): self.stack.addWidget(TwoFAWidget(self, u, r, s, True)); self.stack.setCurrentIndex(self.stack.count()-1)
    def show_2fa_verify(self, u, r, s): self.stack.addWidget(TwoFAWidget(self, u, r, s, False)); self.stack.setCurrentIndex(self.stack.count()-1)
    def show_app(self, u, r): self.stack.addWidget(AppWidget(u, r, self.show_login)); self.stack.setCurrentIndex(self.stack.count()-1)

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyleSheet(STYLESHEET)
    win = MainWindow(); win.show(); sys.exit(app.exec_())
