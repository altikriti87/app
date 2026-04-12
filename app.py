import streamlit as st
import sqlite3
import hashlib
import os
import tempfile
from datetime import datetime
from cryptography.fernet import Fernet

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Seville ECM - Web Edition", layout="wide")

# --- 2. إعدادات التشفير ---
def get_key():
    if not os.path.exists("master.key"):
        key = Fernet.generate_key()
        with open("master.key", "wb") as kf:
            kf.write(key)
    return open("master.key", "rb").read()

FERNET = Fernet(get_key())

# --- 3. محرك قاعدة البيانات ---
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('seville_web_v1.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, user TEXT UNIQUE, pwd TEXT, role TEXT)')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, dept TEXT, 
            stored_name TEXT, original_name TEXT, created_by TEXT, date TEXT)''')
        hpw = hashlib.sha256("admin123".encode()).hexdigest()
        self.cursor.execute("INSERT OR IGNORE INTO users (user, pwd, role) VALUES (?,?,?)", ("admin", hpw, "Admin"))
        self.conn.commit()

db = Database()

# --- 4. منطق الجلسة (Login Session) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 5. واجهة تسجيل الدخول ---
def login_page():
    st.markdown("<h2 style='text-align: center;'>🔐 تسجيل الدخول - نظام سيفيل</h2>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            user = st.text_input("اسم المستخدم")
            pwd = st.text_input("كلمة المرور", type="password")
            if st.button("دخول", use_container_width=True):
                pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
                db.cursor.execute("SELECT user, role FROM users WHERE user=? AND pwd=?", (user, pwd_hash))
                res = db.cursor.fetchone()
                if res:
                    st.session_state.logged_in = True
                    st.session_state.user_data = res
                    st.rerun()
                else:
                    st.error("بيانات الدخول خاطئة")

# --- 6. لوحة التحكم الرئيسية ---
def main_dashboard():
    # الشريط الجانبي
    st.sidebar.title(f"👋 مرحباً {st.session_state.user_data[0]}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📂 الأرشيف المؤسساتي الذكي")
    
    # تبويبات النظام
    tab1, tab2 = st.tabs(["🔍 استعراض الأرشيف", "➕ إضافة مستند جديد"])

    with tab2:
        st.subheader("أرشفة مستند جديد")
        with st.form("upload_form", clear_on_submit=True):
            title = st.text_input("عنوان الوثيقة (أكثر من 4 أحرف)")
            dept = st.selectbox("القسم المختص", ["المبيعات", "المشتريات", "الحسابات", "الإدارة"])
            uploaded_file = st.file_uploader("اختر الملف")
            submit = st.form_submit_button("إتمام عملية الأرشفة")

            if submit:
                if len(title) < 4:
                    st.warning("⚠️ العنوان قصير جداً")
                elif not uploaded_file:
                    st.warning("⚠️ يرجى اختيار ملف")
                else:
                    # تشفير الملف
                    if not os.path.exists("vault"): os.makedirs("vault")
                    file_bytes = uploaded_file.read()
                    encrypted_data = FERNET.encrypt(file_bytes)
                    
                    stored_name = f"SEC_{datetime.now().strftime('%H%M%S')}_{uploaded_file.name}"
                    with open(os.path.join("vault", stored_name), "wb") as f:
                        f.write(encrypted_data)
                    
                    # حفظ في قاعدة البيانات
                    db.cursor.execute(
                        "INSERT INTO docs (title, dept, stored_name, original_name, created_by, date) VALUES (?,?,?,?,?,?)",
                        (title, dept, stored_name, uploaded_file.name, st.session_state.user_data[0], datetime.now().strftime("%Y-%m-%d"))
                    )
                    db.conn.commit()
                    st.success("✅ تم تشفير وأرشفة الملف بنجاح")

    with tab1:
        search = st.text_input("🔍 ابحث في العناوين...")
        query = "SELECT id, title, dept, created_by, date, stored_name, original_name FROM docs WHERE title LIKE ?"
        db.cursor.execute(query, (f"%{search}%",))
        rows = db.cursor.fetchall()

        if rows:
            for row in rows:
                with st.expander(f"📄 {row[1]} - {row[2]}"):
                    col_info, col_btn = st.columns([3, 1])
                    col_info.write(f"الموظف: {row[3]} | التاريخ: {row[4]}")
                    
                    if col_btn.button("فتح الملف", key=row[5]):
                        try:
                            with open(os.path.join("vault", row[5]), "rb") as f:
                                dec_data = FERNET.decrypt(f.read())
                            st.download_button(
                                label="⬇️ تحميل النسخة المفكوكة",
                                data=dec_data,
                                file_name=row[6],
                                mime="application/octet-stream"
                            )
                        except Exception as e:
                            st.error(f"خطأ في فك التشفير: {e}")
        else:
            st.info("لا توجد مستندات مطابقة للبحث")

# --- 7. التشغيل النهائي ---
if not st.session_state.logged_in:
    login_page()
else:
    main_dashboard()
