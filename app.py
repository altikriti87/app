import streamlit as st
import sqlite3
import os
import fitz # PyMuPDF

# إعداد الصفحة وتغيير الثيم للداكن
st.set_page_config(page_title="Seville Scientific Archive", layout="wide")

# إنشاء قاعدة البيانات والجداول
def init_db():
    conn = sqlite3.connect('archive_web.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS docs 
                 (ref_num TEXT PRIMARY KEY, book_num TEXT, doc_date TEXT, 
                  subject TEXT, sender TEXT, receiver TEXT, type TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT, password TEXT, role TEXT)''')
    conn.commit()
    conn.close()

init_db()

# واجهة النظام
st.sidebar.title("🛠 الإعدادات والتحكم")
page = st.sidebar.radio("انتقل إلى:", ["إضافة وثيقة جديدة", "البحث والتعديل", "إدارة المستخدمين"])

if page == "إضافة وثيقة جديدة":
    st.header("📑 إنشاء وثيقة أرشفة جديدة")
    with st.form("doc_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        ref = col1.text_input("الرقم المرجعي الفريد")
        book = col2.text_input("رقم الكتاب")
        date = col1.date_input("التاريخ")
        subject = col2.text_input("الموضوع")
        
        sender = col1.text_input("المرسل")
        receiver = col2.text_input("المستلم")
        
        doc_type = col1.selectbox("نوع البريد", ["وارد", "صادر", "خاص"])
        status = col2.selectbox("الحالة", ["قيد المراجعة", "مكتمل", "تقديم"])
        
        files = st.file_uploader("رفع ملفات / مسح ضوئي", accept_multiple_files=True)
        
        if st.form_submit_button("حفظ الأرشفة"):
            if ref:
                conn = sqlite3.connect('archive_web.db')
                c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO docs VALUES (?,?,?,?,?,?,?,?)", 
                          (ref, book, str(date), subject, sender, receiver, doc_type, status))
                conn.commit()
                st.success(f"تم حفظ الوثيقة رقم {ref} بنجاح!")
            else:
                st.error("يرجى إدخال الرقم المرجعي")

elif page == "البحث والتعديل":
    st.header("🔍 البحث الشامل في الأرشيف")
    search_query = st.text_input("ابحث بالموضوع أو الرقم المرجعي")
    
    conn = sqlite3.connect('archive_web.db')
    import pandas as pd
    df = pd.read_sql_query(f"SELECT * FROM docs WHERE subject LIKE '%{search_query}%' OR ref_num LIKE '%{search_query}%'", conn)
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        selected_ref = st.selectbox("اختر الرقم المرجعي لعرض الملفات أو التعديل", df['ref_num'])
        if st.button("تجميع الوثائق الملحقة في ملف PDF واحد"):
            st.info(f"جاري معالجة الوثائق للرقم {selected_ref}...")
            # هنا تضع منطق تجميع الـ PDF الخاص بمكتبة fitz
