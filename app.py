import os, sqlite3, sys, tempfile, hashlib
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from cryptography.fernet import Fernet

# --- 1. إعدادات الأمان والتشفير ---
def get_key():
    if not os.path.exists("master.key"):
        key = Fernet.generate_key()
        with open("master.key", "wb") as kf: kf.write(key)
    return open("master.key", "rb").read()

FERNET = Fernet(get_key())

# --- 2. لغة التصميم (Material UI + Validation CSS) ---
STYLE = """
    QMainWindow { background-color: #F4F7F9; }
    QFrame#MainCard { background-color: white; border-radius: 12px; border: 1px solid #E0E6ED; }
    
    QLabel { color: #444; font-size: 13px; font-weight: 500; }
    
    /* حقول الإدخال مع التحقق الفوري */
    QLineEdit { 
        border: 2px solid #DCDFE6; border-radius: 8px; 
        padding: 10px; background: white; color: #202124; font-size: 14px;
    }
    QLineEdit[valid="true"] { border: 2px solid #67C23A; }
    QLineEdit[valid="false"] { border: 2px solid #F56C6C; }
    
    QLabel#ErrorHint { color: #F56C6C; font-size: 11px; margin-top: 2px; }
    
    /* الأزرار */
    QPushButton#Primary { 
        background-color: #2196F3; color: white; border-radius: 8px; 
        padding: 10px 20px; font-weight: bold; border: none;
    }
    QPushButton#Primary:hover { background-color: #1976D2; }
    QPushButton#Primary:disabled { background-color: #DCDFE6; color: #909399; }
    
    QPushButton#FileBtn { background-color: #F8F9FA; border: 1px dashed #DCDFE6; color: #606266; }

    /* الجدول */
    QTableWidget { background-color: white; color: #202124; gridline-color: #F0F2F5; border: none; }
    QHeaderView::section { 
        background-color: #F5F7FA; color: #5F6368; 
        padding: 12px; font-weight: bold; border: none; border-bottom: 2px solid #E4E7ED;
    }
"""

# --- 3. محرك قاعدة البيانات ---
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('seville_pro_v14.db')
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, user TEXT UNIQUE, pwd TEXT, role TEXT)')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, dept TEXT, status TEXT, 
            links TEXT, stored_name TEXT, original_name TEXT, created_by TEXT, date TEXT)''')
        hpw = hashlib.sha256("admin123".encode()).hexdigest()
        self.cursor.execute("INSERT OR IGNORE INTO users (user, pwd, role) VALUES (?,?,?)", ("admin", hpw, "Admin"))
        self.conn.commit()

# --- 4. محرر الوثائق مع Inline Validation ---
class DocEditor(QDialog):
    def __init__(self, db, user, data=None):
        super().__init__()
        self.db = db; self.user = user; self.data = data; self.f_path = ""
        self.setWindowTitle("أرشفة مستند جديد" if not data else "تعديل مستند")
        self.setFixedWidth(450)
        self.setStyleSheet(STYLE)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # حقل العنوان
        layout.addWidget(QLabel("عنوان الوثيقة:"))
        self.title_in = QLineEdit(self.data[1] if self.data else "")
        self.title_in.setPlaceholderText("أدخل عنواناً واضحاً (مثلاً: فاتورة رقم 502)")
        self.title_err = QLabel(""); self.title_err.setObjectName("ErrorHint")
        self.title_in.textChanged.connect(self.validate_form)
        layout.addWidget(self.title_in)
        layout.addWidget(self.title_err)

        # حقل القسم
        layout.addWidget(QLabel("القسم المختص:"))
        self.dept_in = QComboBox()
        self.dept_in.addItems(["المبيعات", "المشتريات", "الحسابات", "الإدارة"])
        if self.data: self.dept_in.setCurrentText(self.data[2])
        layout.addWidget(self.dept_in)

        # إرفاق الملف
        layout.addSpacing(10)
        self.btn_file = QPushButton("📁 اضغط هنا لاختيار الملف"); self.btn_file.setObjectName("FileBtn")
        self.btn_file.clicked.connect(self.pick_file)
        self.file_err = QLabel(""); self.file_err.setObjectName("ErrorHint")
        layout.addWidget(self.btn_file)
        layout.addWidget(self.file_err)

        # زر الحفظ
        layout.addSpacing(20)
        self.btn_save = QPushButton("إتمام عملية الأرشفة"); self.btn_save.setObjectName("Primary")
        self.btn_save.clicked.connect(self.accept)
        layout.addWidget(self.btn_save)

        self.validate_form()

    def validate_form(self):
        # التحقق من العنوان
        title_text = self.title_in.text().strip()
        is_title_ok = len(title_text) >= 4
        self.title_in.setProperty("valid", "true" if is_title_ok else "false")
        self.title_err.setText("" if is_title_ok else "⚠️ يجب أن يتكون العنوان من 4 أحرف على الأقل")
        
        # التحقق من الملف
        is_file_ok = True if self.data else self.f_path != ""
        self.file_err.setText("" if is_file_ok else "⚠️ لم يتم اختيار ملف للأرشفة")

        # تحديث التصميم البصري
        self.title_in.style().unpolish(self.title_in)
        self.title_in.style().polish(self.title_in)
        
        # تفعيل الزر
        self.btn_save.setEnabled(is_title_ok and is_file_ok)

    def pick_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "اختر ملف")
        if path:
            self.f_path = path
            self.btn_file.setText(f"✅ تم اختيار: {os.path.basename(path)}")
            self.validate_form()

# --- 5. الواجهة الرئيسية ---
class MainDashboard(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user; self.db = Database()
        self.setWindowTitle("نظام Seville ECM - لوحة التحكم")
        self.setMinimumSize(1150, 750)
        self.setStyleSheet(STYLE)
        if not os.path.exists("vault"): os.makedirs("vault")
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QVBoxLayout(central); main_layout.setContentsMargins(25, 25, 25, 25)

        # Top Bar
        top_card = QFrame(); top_card.setObjectName("MainCard"); top_card.setFixedHeight(80)
        tl = QHBoxLayout(top_card)
        
        welcome_v = QVBoxLayout()
        lbl_welcome = QLabel(f"<b>مرحباً، {self.user[0]}</b>"); lbl_welcome.setStyleSheet("font-size: 16px; color: #2196F3;")
        lbl_date = QLabel(datetime.now().strftime("%Y-%m-%d | %I:%M %p")); lbl_date.setStyleSheet("color: #909399;")
        welcome_v.addWidget(lbl_welcome); welcome_v.addWidget(lbl_date)
        
        self.search_in = QLineEdit(); self.search_in.setPlaceholderText("🔍 ابحث في الأرشيف المؤسساتي..."); self.search_in.setFixedWidth(400)
        self.search_in.textChanged.connect(self.refresh_table)
        
        btn_add = QPushButton("➕ إضافة مستند"); btn_add.setObjectName("Primary"); btn_add.clicked.connect(self.add_doc)
        
        tl.addLayout(welcome_v); tl.addStretch(); tl.addWidget(self.search_in); tl.addWidget(btn_add)
        main_layout.addWidget(top_card)

        # Table Area
        table_card = QFrame(); table_card.setObjectName("MainCard")
        table_l = QVBoxLayout(table_card)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "العنوان", "القسم", "بواسطة", "التاريخ", "الإجراءات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        table_l.addWidget(self.table)
        main_layout.addWidget(table_card)

    def refresh_table(self):
        self.table.setRowCount(0)
        search_txt = f"%{self.search_in.text()}%"
        self.db.cursor.execute("SELECT id, title, dept, created_by, date, stored_name, original_name FROM docs WHERE title LIKE ?", (search_txt,))
        for r_idx, row in enumerate(self.db.cursor.fetchall()):
            self.table.insertRow(r_idx)
            for c_idx in range(5):
                item = QTableWidgetItem(str(row[c_idx]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor("#202124"))
                self.table.setItem(r_idx, c_idx, item)
            
            btn_open = QPushButton("عرض الملف"); btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_open.clicked.connect(lambda _, sn=row[5], on=row[6]: self.open_secure(sn, on))
            self.table.setCellWidget(r_idx, 5, btn_open)

    def add_doc(self):
        ed = DocEditor(self.db, self.user)
        if ed.exec():
            # التشفير والحفظ
            stored_name = f"SEC_{datetime.now().strftime('%H%M%S')}_{os.path.basename(ed.f_path)}"
            with open(ed.f_path, "rb") as f: encrypted_data = FERNET.encrypt(f.read())
            with open(os.path.join("vault", stored_name), "wb") as f: f.write(encrypted_data)
            
            self.db.cursor.execute("INSERT INTO docs (title, dept, stored_name, original_name, created_by, date) VALUES (?,?,?,?,?,?)",
                                   (ed.title_in.text(), ed.dept_in.currentText(), stored_name, os.path.basename(ed.f_path), self.user[0], datetime.now().strftime("%Y-%m-%d")))
            self.db.conn.commit(); self.refresh_table()

    def open_secure(self, sn, on):
        try:
            with open(os.path.join("vault", sn), "rb") as f: decrypted_data = FERNET.decrypt(f.read())
            tmp_path = os.path.join(tempfile.gettempdir(), on)
            with open(tmp_path, "wb") as f: f.write(decrypted_data)
            os.startfile(tmp_path)
        except Exception as e: QMessageBox.critical(self, "خطأ", f"لا يمكن فتح الملف: {str(e)}")

# --- 6. بوابة الدخول ---
class LoginGate(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db; self.user_data = None; self.setWindowTitle("Login - Seville")
        self.setFixedSize(350, 400); self.setStyleSheet(STYLE)
        l = QVBoxLayout(self); l.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("تسجيل الدخول"); title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2196F3;")
        self.u = QLineEdit(placeholderText="اسم المستخدم"); self.p = QLineEdit(placeholderText="كلمة المرور")
        self.p.setEchoMode(QLineEdit.EchoMode.Password)
        btn = QPushButton("دخول"); btn.setObjectName("Primary"); btn.clicked.connect(self.auth)
        
        l.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter); l.addSpacing(20)
        l.addWidget(self.u); l.addWidget(self.p); l.addSpacing(20); l.addWidget(btn)

    def auth(self):
        pwd_hash = hashlib.sha256(self.p.text().encode()).hexdigest()
        self.db.cursor.execute("SELECT user, role FROM users WHERE user=? AND pwd=?", (self.u.text(), pwd_hash))
        res = self.db.cursor.fetchone()
        if res: self.user_data = res; self.accept()
        else: QMessageBox.critical(self, "فشل الدخول", "اسم المستخدم أو كلمة المرور غير صحيحة")

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setFont(QFont("Segoe UI", 10))
    db_instance = Database(); gate = LoginGate(db_instance)
    if gate.exec():
        dashboard = MainDashboard(gate.user_data); dashboard.show(); sys.exit(app.exec())
