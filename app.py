import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class ElectronicArchivingSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام الأرشفة الإلكتروني الذكي - Seville Scientific")
        self.resize(1200, 800)
        
        # تفعيل المظهر الداكن
        self.set_dark_theme()
        
        # المكون الأساسي
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # القائمة الجانبية
        self.sidebar = QVBoxLayout()
        self.init_sidebar()
        
        # منطقة المحتوى الرئيسية
        self.content_area = QStackedWidget()
        self.init_main_pages()
        
        self.layout.addLayout(self.sidebar, 1)
        self.layout.addWidget(self.content_area, 4)

    def set_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                background-color: #333333;
                border: 1px solid #555555;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                padding: 5px;
                color: white;
            }
            QTableWidget {
                gridline-color: #3d3d3d;
                background-color: #2b2b2b;
            }
        """)

    def init_sidebar(self):
        buttons = [
            ("إضافة وثيقة", 0),
            ("البحث الشامل", 1),
            ("إدارة المستخدمين", 2),
            ("إعدادات السكانر", 3),
            ("التقارير", 4)
        ]
        for text, index in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda ch, i=index: self.content_area.setCurrentIndex(i))
            self.sidebar.addWidget(btn)
        self.sidebar.addStretch()

    def init_main_pages(self):
        # صفحة إضافة وثيقة جديدة
        self.add_doc_page = QWidget()
        layout = QFormLayout(self.add_doc_page)
        
        # حقول الإدخال المطلوبة
        self.ref_num = QLineEdit() # رقم مرجعي فريد
        self.book_num = QLineEdit()
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.subject = QLineEdit()
        self.sender = QLineEdit()
        self.receiver = QLineEdit()
        self.doc_type = QComboBox()
        self.doc_type.addItems(["وارد", "صادر", "خاص"])
        self.status = QComboBox()
        self.status.addItems(["قيد المراجعة", "مكتمل", "تقديم"])
        
        layout.addRow("الرقم المرجعي:", self.ref_num)
        layout.addRow("رقم الكتاب:", self.book_num)
        layout.addRow("التاريخ:", self.date_edit)
        layout.addRow("الموضوع:", self.subject)
        layout.addRow("المرسل:", self.sender)
        layout.addRow("المستلم:", self.receiver)
        layout.addRow("نوع البريد:", self.doc_type)
        layout.addRow("الحالة:", self.status)
        
        # أزرار الملفات
        file_btn = QPushButton("رفع ملفات / مسح ضوئي")
        save_btn = QPushButton("حفظ الوثيقة")
        save_btn.setStyleSheet("background-color: #0078d4;")
        
        layout.addRow(file_btn)
        layout.addRow(save_btn)
        
        self.content_area.addWidget(self.add_doc_page)
        
        # صفحة البحث (فارغة حالياً للهيكل)
        self.search_page = QWidget()
        self.content_area.addWidget(self.search_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ElectronicArchivingSystem()
    window.show()
    sys.exit(app.exec())
