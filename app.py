import sys
import sqlite3
import os
import fitz  # PyMuPDF
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# --- المحرك الرئيسي لقاعدة البيانات ---
class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect('smart_archive.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # 1. المستخدمين والصلاحيات
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE, password TEXT, role TEXT)''')
        
        # 2. السجلات (الوثائق)
        cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_num TEXT UNIQUE, book_num TEXT, doc_date TEXT,
            subject TEXT, sender TEXT, receiver TEXT,
            details TEXT, doc_type TEXT, status TEXT)''')
        
        # 3. الملفات المرفقة
        cursor.execute('''CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_ref TEXT, file_path TEXT)''')
        
        # 4. الربط بين الوثائق
        cursor.execute('''CREATE TABLE IF NOT EXISTS linked_docs (
            parent_ref TEXT, child_ref TEXT)''')
        
        # إضافة مستخدم افتراضي
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin', 'مدير')")
        self.conn.commit()

# --- واجهة المستخدم الاحترافية ---
class ArchiveApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.setWindowTitle("نظام الأرشفة الإلكتروني المتكامل - Dark Mode")
        self.resize(1200, 850)
        self.apply_styles()
        self.init_ui()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', Tahoma; }
            QLineEdit, QTextEdit, QComboBox, QDateEdit { 
                background-color: #1e1e1e; border: 1px solid #333; padding: 8px; border-radius: 4px; color: white;
            }
            QPushButton { background-color: #0078d4; color: white; padding: 10px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #005a9e; }
            QTableWidget { background-color: #1e1e1e; gridline-color: #333; color: white; }
            QHeaderView::section { background-color: #252525; padding: 5px; border: 1px solid #333; }
        """)

    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # القائمة الجانبية (Navigation)
        self.sidebar = QVBoxLayout()
        nav_items = [
            ("➕ وثيقة جديدة", 0),
            ("🔍 البحث الشامل", 1),
            ("👥 إدارة المستخدمين", 2),
            ("⚙️ إعدادات النظام", 3)
        ]
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.clicked.connect(lambda ch, i=idx: self.tabs.setCurrentIndex(i))
            self.sidebar.addWidget(btn)
        self.sidebar.addStretch()

        # صفحات النظام
        self.tabs = QStackedWidget()
        self.tabs.addWidget(self.ui_add_document())
        self.tabs.addWidget(self.ui_search_archive())
        self.tabs.addWidget(self.ui_user_management())
        self.tabs.addWidget(self.ui_settings())

        main_layout.addLayout(self.sidebar, 1)
        main_layout.addWidget(self.tabs, 5)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # --- صفحة إضافة وثيقة ---
    def ui_add_document(self):
        page = QWidget()
        layout = QFormLayout(page)
        
        self.ref_num = QLineEdit()
        self.book_num = QLineEdit()
        self.doc_date = QDateEdit(calendarPopup=True)
        self.doc_date.setDate(QDate.currentDate())
        self.subject = QLineEdit()
        self.sender = QLineEdit()
        self.receiver = QLineEdit()
        self.details = QTextEdit()
        
        self.doc_type = QComboBox()
        self.doc_type.addItems(["وارد", "صادر", "خاص"])
        
        self.status = QComboBox()
        self.status.addItems(["قيد المراجعة", "مكتمل", "تقديم"])

        self.temp_files = []
        btn_files = QPushButton("رفع ملفات / مسح ضوئي")
        btn_files.clicked.connect(self.upload_action)
        
        btn_save = QPushButton("حفظ الوثيقة في السجلات")
        btn_save.clicked.connect(self.save_document_action)
        btn_save.setStyleSheet("background-color: #28a745;")

        layout.addRow("الرقم المرجعي الفريد:", self.ref_num)
        layout.addRow("رقم الكتاب:", self.book_num)
        layout.addRow("التاريخ:", self.doc_date)
        layout.addRow("الموضوع:", self.subject)
        layout.addRow("المرسل:", self.sender)
        layout.addRow("المستلم:", self.receiver)
        layout.addRow("نوع البريد:", self.doc_type)
        layout.addRow("الحالة:", self.status)
        layout.addRow("التفاصيل:", self.details)
        layout.addRow(btn_files)
        layout.addRow(btn_save)
        
        return page

    # --- صفحة البحث الشامل ---
    def ui_search_archive(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("بحث في الموضوع، الأرقام المرجعية، أو التفاصيل...")
        search_input.textChanged.connect(self.search_action)
        
        self.search_table = QTableWidget(0, 7)
        self.search_table.setHorizontalHeaderLabels(["المرجعي", "رقم الكتاب", "الموضوع", "النوع", "الحالة", "التاريخ", "الإجراء"])
        self.search_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(search_input)
        layout.addWidget(self.search_table)
        return page

    # --- صفحة إدارة المستخدمين ---
    def ui_user_management(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("إضافة / حذف مستخدمين"))
        # (يمكن إضافة نموذج هنا بنفس أسلوب إضافة الوثيقة)
        layout.addWidget(QTableWidget(3, 3)) 
        return page

    # --- صفحة الإعدادات (السكانر) ---
    def ui_settings(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("إعدادات المساح الضوئي (DPI, Format)"))
        layout.addWidget(QComboBox()) # اختيار جهاز السكانر
        return page

    # --- الوظائف المنطقية ---
    def upload_action(self):
        files, _ = QFileDialog.getOpenFileNames(self, "اختر الملفات")
        if files: self.temp_files.extend(files)

    def save_document_action(self):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''INSERT INTO documents (ref_num, book_num, doc_date, subject, sender, receiver, details, doc_type, status)
                           VALUES (?,?,?,?,?,?,?,?,?)''', 
                           (self.ref_num.text(), self.book_num.text(), self.doc_date.text(), self.subject.text(),
                            self.sender.text(), self.receiver.text(), self.details.toPlainText(), 
                            self.doc_type.currentText(), self.status.currentText()))
            
            for f in self.temp_files:
                cursor.execute("INSERT INTO attachments (doc_ref, file_path) VALUES (?,?)", (self.ref_num.text(), f))
            
            self.db.conn.commit()
            QMessageBox.information(self, "نجاح", "تمت الأرشفة بنجاح")
            self.temp_files = []
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {str(e)}")

    def search_action(self, text):
        cursor = self.db.conn.cursor()
        query = "SELECT ref_num, book_num, subject, doc_type, status, doc_date FROM documents WHERE subject LIKE ? OR ref_num LIKE ?"
        cursor.execute(query, (f'%{text}%', f'%{text}%'))
        rows = cursor.fetchall()
        
        self.search_table.setRowCount(0)
        for row_idx, row_data in enumerate(rows):
            self.search_table.insertRow(row_idx)
            for col_idx, data in enumerate(row_data):
                self.search_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
            
            btn = QPushButton("عرض / ربط")
            btn.clicked.connect(lambda ch, r=row_data[0]: self.show_details_dialog(r))
            self.search_table.setCellWidget(row_idx, 6, btn)

    def show_details_dialog(self, ref):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"عرض الوثيقة: {ref}")
        dialog.resize(500, 400)
        layout = QVBoxLayout(dialog)
        
        cursor = self.db.conn.cursor()
        # جلب الملفات المرفقة
        cursor.execute("SELECT file_path FROM attachments WHERE doc_ref = ?", (ref,))
        files = cursor.fetchall()
        
        # جلب الوثائق المرتبطة
        cursor.execute("SELECT child_ref FROM linked_docs WHERE parent_ref = ?", (ref,))
        links = cursor.fetchall()

        layout.addWidget(QLabel("📂 الملفات المرفقة:"))
        for f in files:
            b = QPushButton(os.path.basename(f[0]))
            b.clicked.connect(lambda ch, p=f[0]: os.startfile(p))
            layout.addWidget(b)
            
        layout.addWidget(QLabel("🔗 وثائق مرتبطة بهذا الكتاب:"))
        for l in links:
            layout.addWidget(QLabel(f"كتاب رقم: {l[0]}"))

        btn_pdf = QPushButton("تجميع الكل في PDF واحد")
        btn_pdf.clicked.connect(lambda: self.make_pdf(ref, [f[0] for f in files]))
        layout.addWidget(btn_pdf)
        
        dialog.exec()

    def make_pdf(self, ref, paths):
        doc = fitz.open()
        for p in paths:
            if p.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = fitz.open(p)
                doc.insert_pdf(fitz.open("pdf", img.convert_to_pdf()))
            elif p.lower().endswith('.pdf'):
                doc.insert_pdf(fitz.open(p))
        doc.save(f"Archive_{ref}.pdf")
        QMessageBox.information(self, "تم", "تم تجميع الوثائق بنجاح")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    window = ArchiveApp()
    window.show()
    sys.exit(app.exec())
