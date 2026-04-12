import sys
import sqlite3
import os
import fitz  # PyMuPDF لتجميع الـ PDF
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# --- إعداد قاعدة البيانات ---
def setup_database():
    conn = sqlite3.connect('archive_system.db')
    cursor = conn.cursor()
    # جدول الوثائق الأساسي
    cursor.execute('''CREATE TABLE IF NOT EXISTS docs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ref_num TEXT UNIQUE,
        book_num TEXT,
        doc_date TEXT,
        subject TEXT,
        sender TEXT,
        receiver TEXT,
        details TEXT,
        doc_type TEXT,
        status TEXT
    )''')
    # جدول الملفات المرتبطة
    cursor.execute('''CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_ref TEXT,
        file_path TEXT,
        FOREIGN KEY(doc_ref) REFERENCES docs(ref_num)
    )''')
    conn.commit()
    conn.close()

# --- واجهة المستخدم الحديثة (Dark Mode) ---
STYLE_SHEET = """
    QMainWindow { background-color: #121212; }
    QWidget { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI', Arial; }
    QLineEdit, QTextEdit, QComboBox, QDateEdit {
        background-color: #1E1E1E; border: 1px solid #333; padding: 8px; border-radius: 5px; color: white;
    }
    QPushButton {
        background-color: #0078D4; color: white; border-radius: 5px; padding: 10px; font-weight: bold; min-width: 100px;
    }
    QPushButton:hover { background-color: #005A9E; }
    QTableWidget { background-color: #1E1E1E; gridline-color: #333; border: none; }
    QHeaderView::section { background-color: #252525; color: white; padding: 5px; border: 1px solid #333; }
    QGroupBox { border: 1px solid #333; margin-top: 10px; padding: 10px; font-weight: bold; }
"""

class ArchivingSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        setup_database()
        self.setWindowTitle("نظام الأرشفة الإلكتروني - Seville Scientific")
        self.resize(1200, 800)
        self.setStyleSheet(STYLE_SHEET)
        self.attached_files_paths = []
        self.init_ui()

    def init_ui(self):
        # القائمة الجانبية والصفحات
        main_layout = QHBoxLayout()
        self.sidebar = QVBoxLayout()
        
        # أزرار التنقل
        btn_add = QPushButton("➕ إضافة وثيقة")
        btn_search = QPushButton("🔍 البحث الشامل")
        btn_add.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_search.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        self.sidebar.addWidget(btn_add)
        self.sidebar.addWidget(btn_search)
        self.sidebar.addStretch()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_add_page())
        self.stack.addWidget(self.create_search_page())

        main_layout.addLayout(self.sidebar, 1)
        main_layout.addWidget(self.stack, 5)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_add_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        form = QFormLayout()

        self.ref_num = QLineEdit()
        self.book_num = QLineEdit()
        self.date_in = QDateEdit(calendarPopup=True)
        self.date_in.setDate(QDate.currentDate())
        self.subject = QLineEdit()
        self.sender = QLineEdit()
        self.receiver = QLineEdit()
        self.details = QTextEdit()
        self.doc_type = QComboBox()
        self.doc_type.addItems(["وارد", "صادر", "خاص"])
        self.status = QComboBox()
        self.status.addItems(["مكتمل", "قيد المراجعة", "تقديم"])

        form.addRow("الرقم المرجعي:", self.ref_num)
        form.addRow("رقم الكتاب:", self.book_num)
        form.addRow("التاريخ:", self.date_in)
        form.addRow("الموضوع:", self.subject)
        form.addRow("المرسل:", self.sender)
        form.addRow("المستلم:", self.receiver)
        form.addRow("التفاصيل:", self.details)
        form.addRow("نوع البريد:", self.doc_type)
        form.addRow("الحالة:", self.status)

        upload_btn = QPushButton("📎 رفع ملفات / سكنر")
        upload_btn.clicked.connect(self.handle_upload)
        upload_btn.setStyleSheet("background-color: #444;")
        
        save_btn = QPushButton("💾 حفظ الوثيقة")
        save_btn.clicked.connect(self.handle_save)
        save_btn.setStyleSheet("background-color: #28a745;")

        layout.addLayout(form)
        layout.addWidget(upload_btn)
        layout.addWidget(save_btn)
        return page

    def create_search_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("ابحث برقم الكتاب، المرجعي، أو الموضوع...")
        search_bar.textChanged.connect(self.perform_search)
        
        self.result_table = QTableWidget(0, 7)
        self.result_table.setHorizontalHeaderLabels(["المرجعي", "رقم الكتاب", "الموضوع", "التاريخ", "النوع", "الحالة", "إجراءات"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(QLabel("📂 الأرشيف المركزي"))
        layout.addWidget(search_bar)
        layout.addWidget(self.result_table)
        return page

    # --- المنطق البرمجي ---
    def handle_upload(self):
        files, _ = QFileDialog.getOpenFileNames(self, "اختر الملفات")
        if files:
            self.attached_files_paths.extend(files)
            QMessageBox.information(self, "نجاح", f"تم تحديد {len(files)} ملفات للرفع")

    def handle_save(self):
        try:
            conn = sqlite3.connect('archive_system.db')
            c = conn.cursor()
            c.execute("INSERT INTO docs (ref_num, book_num, doc_date, subject, sender, receiver, details, doc_type, status) VALUES (?,?,?,?,?,?,?,?,?)",
                      (self.ref_num.text(), self.book_num.text(), self.date_in.text(), self.subject.text(), 
                       self.sender.text(), self.receiver.text(), self.details.toPlainText(), self.doc_type.currentText(), self.status.currentText()))
            
            for path in self.attached_files_paths:
                c.execute("INSERT INTO files (doc_ref, file_path) VALUES (?,?)", (self.ref_num.text(), path))
            
            conn.commit()
            conn.close()
            QMessageBox.information(self, "تم", "تم حفظ الوثيقة بنجاح")
            self.attached_files_paths = []
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")

    def perform_search(self, text):
        conn = sqlite3.connect('archive_system.db')
        c = conn.cursor()
        c.execute("SELECT ref_num, book_num, subject, doc_date, doc_type, status FROM docs WHERE subject LIKE ? OR ref_num LIKE ?", (f'%{text}%', f'%{text}%'))
        results = c.fetchall()
        
        self.result_table.setRowCount(0)
        for row_idx, row_data in enumerate(results):
            self.result_table.insertRow(row_idx)
            for col_idx, data in enumerate(row_data):
                self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
            
            btn_view = QPushButton("فتح")
            btn_view.clicked.connect(lambda ch, r=row_data[0]: self.open_doc_details(r))
            self.result_table.setCellWidget(row_idx, 6, btn_view)
        conn.close()

    def open_doc_details(self, ref):
        conn = sqlite3.connect('archive_system.db')
        c = conn.cursor()
        c.execute("SELECT file_path FROM files WHERE doc_ref = ?", (ref,))
        files = c.fetchall()
        
        detail_dialog = QDialog(self)
        detail_dialog.setWindowTitle(f"وثائق مرتبطة بـ {ref}")
        layout = QVBoxLayout(detail_dialog)
        
        if not files:
            layout.addWidget(QLabel("لا توجد ملفات مرفقة لهذه الوثيقة"))
        else:
            for f in files:
                btn = QPushButton(os.path.basename(f[0]))
                btn.clicked.connect(lambda ch, p=f[0]: os.startfile(p))
                layout.addWidget(btn)
            
            btn_compile = QPushButton("📥 دمج الكل في PDF واحد")
            btn_compile.clicked.connect(lambda: self.merge_to_pdf(ref, [f[0] for f in files]))
            layout.addWidget(btn_compile)
            
        detail_dialog.exec()

    def merge_to_pdf(self, ref, paths):
        target = f"تجميع_{ref}.pdf"
        doc = fitz.open()
        for p in paths:
            if p.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = fitz.open(p)
                rect = img[0].rect
                pdfbytes = img.convert_to_pdf()
                img.close()
                imgpdf = fitz.open("pdf", pdfbytes)
                doc.insert_pdf(imgpdf)
            elif p.lower().endswith('.pdf'):
                doc.insert_pdf(fitz.open(p))
        doc.save(target)
        QMessageBox.information(self, "نجاح", f"تم التجميع في ملف: {target}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft) # قلب الواجهة للعربية
    window = ArchivingSystem()
    window.show()
    sys.exit(app.exec())
