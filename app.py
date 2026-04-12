import streamlit as st
import sqlite3
import os

# إعداد واجهة المتصفح
st.set_page_config(page_title="Seville Archive", layout="wide")

def init_db():
    conn = sqlite3.connect('archive_web.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS docs 
                 (ref_num TEXT, book_num TEXT, subject TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.title("📂 نظام الأرشفة الإلكتروني (نسخة الويب)")

# القائمة الجانبية
menu = ["إضافة وثيقة", "البحث الشامل"]
choice = st.sidebar.radio("القائمة الرئيسية", menu)

if choice == "إضافة وثيقة":
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        ref = col1.text_input("الرقم المرجعي")
        book = col2.text_input("رقم الكتاب")
        subject = st.text_input("الموضوع")
        status = st.selectbox("الحالة", ["قيد المراجعة", "مكتمل", "تقديم"])
        files = st.file_uploader("ارفق الملفات", accept_multiple_files=True)
        
        if st.form_submit_button("حفظ الوثيقة"):
            conn = sqlite3.connect('archive_web.db')
            c = conn.cursor()
            c.execute("INSERT INTO docs VALUES (?,?,?,?)", (ref, book, subject, status))
            conn.commit()
            st.success(f"تم حفظ الوثيقة {ref} بنجاح!")

elif choice == "البحث الشامل":
    search = st.text_input("بحث بالاسم أو الرقم")
    # هنا يتم عرض النتائج من قاعدة البيانات
