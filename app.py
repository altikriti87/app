import sys
import sqlite3
import os
import fitz  # PyMuPDF
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from datetime import datetime

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('archiving_system.db')
    cursor = conn.cursor()
    # جدول المستخدمين
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                   (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    # جدول الوثائق
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    ref_num TEXT UNIQUE, book_num TEXT, date TEXT, 
                    subject TEXT, sender TEXT, receiver TEXT, 
                    details TEXT, doc_type TEXT, status TEXT)''')
    # جدول الملفات المرتبطة (Paths)
    cursor.execute('''CREATE TABLE IF NOT EXISTS attachments 
                   (id INTEGER PRIMARY KEY, doc_ref TEXT, file_path TEXT)''')
    # جدول ربط الوثائق ببعضها
    cursor.execute('''CREATE TABLE IF NOT EXISTS linked_docs 
                   (id INTEGER PRIMARY KEY, parent_ref TEXT, child_ref TEXT)''')
    conn.commit()
    conn.close()

# --- المظهر العام (Dark Mode UI) ---
DARK_STYLE = """
    QMainWindow, QWidget { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI', Tahoma; }
    QLineEdit, QTextEdit, QComboBox, QDateEdit { 
        background-color: #1E1E1E; border: 1px solid #333; padding: 8px; border-radius: 4px; color: white;
    }
    QPushButton { 
        background-color: #0078D4; color: white; border-radius: 4px; padding: 10px 20px; font-weight: bold;
    }
    QPushButton:hover { background-color: #005A9E; }
    QTableWidget { background-color: #1E1E1E; gridline-color: #333; color: white; }
    QHeaderView::section { background-color: #252525; padding: 4px; border: 1px solid #333; }
    QLabel { font-size: 14px; }
"""

class ArchivingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام الأرشفة الإلكتروني الذكي")
        self.resize(1100, 750)
        self.setStyleSheet(DARK_STYLE)
        
        init_db()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        
        # القائمة الجانبية
        self.sidebar = QVBoxLayout()
        btns = [("وثيقة جديدة", self.show_add), ("البحث والأرشفة", self.show_search), ("الإعدادات", None)]
        for text, func in btns:
            btn = QPushButton(text)
            if func: btn.clicked.connect(func)
            self.sidebar.addWidget(btn)
        self.sidebar.addStretch()
        
        # الصفحات
        self.stack = QStackedWidget()
        self.add_page = self.create_add_page()
        self.search_page = self.create_search_page()
        
        self.stack.addWidget(self.add_page)
        self.stack.addWidget(self.search_page)
        
        layout.addLayout(self.sidebar, 1)
        layout.addWidget(self.stack, 4)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_add_page(self):
        page = QWidget()
        layout = QFormLayout(page)
        layout.setSpacing(15)

        self.f_ref = QLineEdit()
        self.f_book = QLineEdit()
        self.f_date = QDateEdit(calendarPopup=True)
        self.f_date.setDate(QDate.currentDate())
        self.f_subject = QLineEdit()
        self.f_sender = QLineEdit()
        self.f_receiver = QLineEdit()
        self.f_details = QTextEdit()
        self.f_type = QComboBox()
        self.f_type.addItems(["وارد", "صادر", "خاص"])
        self.f_status = QComboBox()
        self.f_status.addItems(["مكتمل", "قيد المراجعة", "تقديم"])
        
        self.attached_files = []
        btn_upload = QPushButton("إرفاق ملفات")
        btn_upload.clicked.connect(self.upload_files)
        
        btn_save = QPushButton("حفظ الوثيقة")
        btn_save.clicked.connect(self.save_document)
        btn_save.setStyleSheet("background-color: #28a745;")

        layout.addRow("الرقم المرجعي (فريد):", self.f_ref)
        layout.addRow("رقم الكتاب:", self.f_book)
        layout.addRow("التاريخ:", self.f_date)
        layout.addRow("الموضوع:", self.f_subject)
        layout.addRow("المرسل:", self.f_sender)
        layout.addRow("المستلم:", self.f_receiver)
        layout.addRow("التفاصيل:", self.f_details)
        layout.addRow("نوع البريد:", self.f_type)
        layout.addRow("الحالة:", self.f_status)
        layout.addRow(btn_upload)
        layout.addRow(btn_save)
        
        return page

    def create_search_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("ابحث هنا (الموضوع، الرقم المرجعي، المرسل...)")
        search_bar.textChanged.connect(self.search_docs)
        
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["المرجعي", "رقم الكتاب", "التاريخ", "الموضوع", "النوع", "الحالة", "إجراءات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(QLabel("البحث الشامل في الأرشيف"))
        layout.addWidget(search_bar)
        layout.addWidget(self.table)
        
        return page

    # --- الوظائف ---
    def show_add(self): self.stack.setCurrentIndex(0)
    def show_search(self): 
        self.stack.setCurrentIndex(1)
        self.search_docs()

    def upload_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "اختر الملفات")
        if files:
            self.attached_files.extend(files)
            QMessageBox.information(self, "تم", f"تم إرفاق {len(files)} ملفات")

    def save_document(self):
        try:
            conn = sqlite3.connect('archiving_system.db')
            curr = conn.cursor()
            curr.execute('''INSERT INTO documents (ref_num, book_num, date, subject, sender, receiver, details, doc_type, status) 
                         VALUES (?,?,?,?,?,?,?,?,?)''', 
                         (self.f_ref.text(), self.f_book.text(), self.f_date.text(), self.f_subject.text(), 
                          self.f_sender.text(), self.f_receiver.text(), self.f_details.toPlainText(), 
                          self.f_type.currentText(), self.f_status.currentText()))
            
            for f in self.attached_files:
                curr.execute("INSERT INTO attachments (doc_ref, file_path) VALUES (?,?)", (self.f_ref.text(), f))
            
            conn.commit()
            conn.close()
            QMessageBox.information(self, "نجاح", "تم حفظ الوثيقة بنجاح")
            self.clear_fields()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الحفظ: {str(e)}")

    def search_docs(self, text=""):
        conn = sqlite3.connect('archiving_system.db')
        curr = conn.cursor()
        query = "SELECT ref_num, book_num, date, subject, doc_type, status FROM documents WHERE subject LIKE ? OR ref_num LIKE ?"
        curr.execute(query, (f'%{text}%', f'%{text}%'))
        rows = curr.fetchall()
        
        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
            
            btn_view = QPushButton("عرض/ربط")
            btn_view.clicked.connect(lambda ch, r=row_data[0]: self.view_document(r))
            self.table.setCellWidget(row_idx, 6, btn_view)
        conn.close()

    def view_document(self, ref_num):
        # نافذة عرض التفاصيل والوثائق المرتبطة
        detail_win = QDialog(self)
        detail_win.setWindowTitle(f"تفاصيل الوثيقة: {ref_num}")
        detail_win.resize(600, 500)
        layout = QVBoxLayout(detail_win)
        
        conn = sqlite3.connect('archiving_system.db')
        curr = conn.cursor()
        
        # جلب الوثائق المرتبطة
        curr.execute("SELECT file_path FROM attachments WHERE doc_ref = ?", (ref_num,))
        files = curr.fetchall()
        
        layout.addWidget(QLabel(f"الوثيقة الأساسية: {ref_num}"))
        layout.addWidget(QLabel("الملفات المرفقة:"))
        
        for f in files:
            path = f[0]
            btn_file = QPushButton(os.path.basename(path))
            btn_file.clicked.connect(lambda ch, p=path: os.startfile(p))
            layout.addWidget(btn_file)
            
        btn_pdf = QPushButton("تجميع الكل في ملف PDF")
        btn_pdf.clicked.connect(lambda: self.compile_to_pdf(ref_num, files))
        layout.addWidget(btn_pdf)
        
        detail_win.exec()

    def compile_to_pdf(self, ref, files):
        if not files: return
        doc = fitz.open()
        for f in files:
            path = f[0]
            if path.lower().endswith(('.png', '.jpg', '.jpeg')):
                imgdoc = fitz.open(path)
                pdfbytes = imgdoc.convert_to_pdf()
                imgpdf = fitz.open("pdf", pdfbytes)
                doc.insert_pdf(imgpdf)
            elif path.lower().endswith('.pdf'):
                doc.insert_pdf(fitz.open(path))
        
        save_path = f"Compiled_{ref}.pdf"
        doc.save(save_path)
        QMessageBox.information(self, "تم", f"تم حفظ الملف المجمع باسم: {save_path}")

    def clear_fields(self):
        self.f_ref.clear()
        self.f_book.clear()
        self.f_subject.clear()
        self.attached_files = []

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft) # دعم اللغة العربية
    ex = ArchivingApp()
    ex.show()
    sys.exit(app.exec())
