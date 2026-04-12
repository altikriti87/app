import streamlit as st
import sqlite3
import os
import fitz  # PyMuPDF
from datetime import datetime
import pandas as pd

# --- إعدادات الصفحة والمظهر ---
st.set_page_config(page_title="Seville Scientific Archive", layout="wide")

# تخصيص المظهر الداكن عبر CSS
st.markdown("""
    <style>
    .main { background-color: #121212; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #0078D4; color: white; }
    .stTextInput>div>div>input { background-color: #1E1E1E; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- إدارة قاعدة البيانات ---
def init_db():
    # استخدام إصدار جديد لتجنب أخطاء الهيكلية السابقة
    conn = sqlite3.connect('smart_archive_v3.db')
    c = conn.cursor()
    # 1. جدول الوثائق (8 أعمدة أساسية + التفاصيل)
    c.execute('''CREATE TABLE IF NOT EXISTS docs 
                 (ref_num TEXT PRIMARY KEY, book_num TEXT, doc_date TEXT, 
                  subject TEXT, sender TEXT, receiver TEXT, 
                  doc_type TEXT, status TEXT, details TEXT)''')
    
    # 2. جدول الملحقات (الملفات)
    c.execute('''CREATE TABLE IF NOT EXISTS files 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, doc_ref TEXT, file_name TEXT, binary_data BLOB)''')
    
    # 3. جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# --- القائمة الجانبية ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3843/3843517.png", width=100)
st.sidebar.title("نظام الأرشفة الذكي")
menu = ["وثيقة جديدة", "البحث الشامل", "إدارة المستخدمين", "إعدادات السكانر"]
choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

# --- 1. صفحة إضافة وثيقة جديدة ---
if choice == "وثيقة جديدة":
    st.header("➕ أرشفة وثيقة جديدة")
    
    with st.form("archive_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ref = st.text_input("الرقم المرجعي الفريد (Unique ID)*")
            date = st.date_input("تاريخ الكتاب", datetime.now())
            sender = st.text_input("المرسل")
            doc_type = st.selectbox("نوع البريد", ["وارد", "صادر", "خاص"])
        
        with col2:
            book = st.text_input("رقم الكتاب الداخلي")
            subject = st.text_input("الموضوع (العنوان)")
            receiver = st.text_input("المستلم")
            status = st.selectbox("الحالة", ["قيد المراجعة", "مكتمل", "تقديم"])
            
        details = st.text_area("تفاصيل إضافية عن المحتوى")
        uploaded_files = st.file_uploader("رفع الملحقات (صور/PDF)", accept_multiple_files=True)
        
        submit = st.form_submit_button("حفظ وأرشفة")
        
        if submit:
            if not ref or not subject:
                st.error("يرجى ملء الحقول الأساسية (الرقم المرجعي والموضوع)")
            else:
                conn = sqlite3.connect('smart_archive_v3.db')
                c = conn.cursor()
                try:
                    # حفظ البيانات النصية
                    c.execute("INSERT INTO docs VALUES (?,?,?,?,?,?,?,?,?)", 
                              (ref, book, str(date), subject, sender, receiver, doc_type, status, details))
                    
                    # حفظ الملفات المرفقة كمصفوفة ثنائية (BLOB)
                    if uploaded_files:
                        for f in uploaded_files:
                            c.execute("INSERT INTO files (doc_ref, file_name, binary_data) VALUES (?,?,?)", 
                                      (ref, f.name, f.read()))
                    
                    conn.commit()
                    st.success(f"✅ تم حفظ الوثيقة {ref} بنجاح مع ملحقاتها.")
                except sqlite3.IntegrityError:
                    st.error("الرقم المرجعي موجود مسبقاً! يرجى استخدام رقم فريد.")
                finally:
                    conn.close()

# --- 2. صفحة البحث والربط ---
elif choice == "البحث الشامل":
    st.header("🔍 محرك البحث والأرشفة")
    search_q = st.text_input("ابحث برقم الكتاب، الموضوع، أو المرسل...")
    
    conn = sqlite3.connect('smart_archive_v3.db')
    query = f"SELECT * FROM docs WHERE subject LIKE '%{search_q}%' OR ref_num LIKE '%{search_q}%' OR book_num LIKE '%{search_q}%'"
    df = pd.read_sql_query(query, conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        selected_ref = st.selectbox("اختر وثيقة لعرض تفاصيلها وملفاتها المرتبطة", df['ref_num'])
        
        if selected_ref:
            st.divider()
            # جلب الملفات المرفقة للوثيقة المختارة
            c = conn.cursor()
            c.execute("SELECT file_name, binary_data FROM files WHERE doc_ref = ?", (selected_ref,))
            attached_files = c.fetchall()
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("📁 الملحقات المكتشفة")
                if attached_files:
                    for name, data in attached_files:
                        st.download_button(label=f"فتح: {name}", data=data, file_name=name)
                else:
                    st.info("لا توجد ملفات مرفقة.")

            with col_b:
                st.subheader("📑 إجراءات PDF")
                if st.button("تجميع كافة الملحقات في ملف PDF واحد"):
                    if attached_files:
                        out_pdf = fitz.open()
                        for name, data in attached_files:
                            # تحويل الصور إلى صفحات PDF
                            if name.lower().endswith(('.png', '.jpg', '.jpeg')):
                                img_doc = fitz.open(stream=data, filetype="img")
                                pdf_bytes = img_doc.convert_to_pdf()
                                out_pdf.insert_pdf(fitz.open("pdf", pdf_bytes))
                            elif name.lower().endswith('.pdf'):
                                out_pdf.insert_pdf(fitz.open(stream=data, filetype="pdf"))
                        
                        pdf_output = out_pdf.tobytes()
                        st.download_button("⬇️ تحميل الملف المجمع", data=pdf_output, file_name=f"Bundle_{selected_ref}.pdf")
                    else:
                        st.warning("لا توجد ملفات لدمجها.")
    conn.close()

# --- 3. إدارة المستخدمين ---
elif choice == "إدارة المستخدمين":
    st.header("👥 إدارة صلاحيات المستخدمين")
    with st.expander("إضافة مستخدم جديد"):
        new_user = st.text_input("اسم المستخدم")
        new_pass = st.text_input("كلمة المرور", type="password")
        new_role = st.selectbox("الصلاحية", ["مدير", "مدخل بيانات", "عرض فقط"])
        if st.button("حفظ المستخدم"):
            st.success("تم إضافة المستخدم بنجاح (محاكاة)")

# --- 4. إعدادات السكانر ---
elif choice == "إعدادات السكانر":
    st.header("⚙️ إعدادات المسح الضوئي")
    st.info("ملاحظة: في نسخة الويب، يتم استلام الصور من السكانر بعد حفظها على الجهاز ورفعها يدوياً.")
    st.selectbox("دقة المسح (DPI)", [150, 300, 600])
    st.selectbox("صيغة الملف الافتراضية", ["PDF", "JPG", "PNG"])
