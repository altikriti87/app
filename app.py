import os
import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image
import easyocr
import numpy as np

# --- 1. إعداد المسارات ---
# قم بتغيير هذا المسار للمسار الموجود في جهازك لقرص جوجل درايف
CLOUD_PATH = r"G:\My Drive\Archive_Cloud" 

if not os.path.exists(CLOUD_PATH):
    # إذا لم يجد قرص G، سيستخدم مجلد محلي مؤقت
    CLOUD_PATH = "local_archive"
    os.makedirs(CLOUD_PATH, exist_ok=True)

# --- 2. قاعدة البيانات (لحفظ النصوص والبحث) ---
conn = sqlite3.connect('my_archive.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS docs 
             (id INTEGER PRIMARY KEY, title TEXT, content TEXT, path TEXT)''')
conn.commit()

# --- 3. واجهة البرنامج ---
st.set_page_config(page_title="أرشفة سحابية مجانية")
st.title("📂 نظام الأرشفة المتصل بجوجل درايف")

menu = st.sidebar.selectbox("القائمة", ["إضافة وثيقة", "بحث في الأرشيف"])

if menu == "إضافة وثيقة":
    st.header("رفع وثيقة جديدة للسحابة")
    uploaded_file = st.file_uploader("اختر صورة الوثيقة", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        if st.button("أرشفة وحفظ في درايف"):
            # حفظ الملف في مجلد جوجل درايف على الجهاز
            file_path = os.path.join(CLOUD_PATH, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # قراءة النص (OCR)
            with st.spinner("جاري استخراج النصوص..."):
                reader = easyocr.Reader(['ar', 'en'])
                img = Image.open(uploaded_file)
                result = reader.readtext(np.array(img), detail=0)
                full_text = " ".join(result)
            
            # حفظ البيانات في قاعدة البيانات للبحث السريع
            c.execute("INSERT INTO docs (title, content, path) VALUES (?, ?, ?)", 
                      (uploaded_file.name, full_text, file_path))
            conn.commit()
            
            st.success(f"✅ تم الحفظ! الملف الآن في طريقه لجوجل درايف عبر المزامنة.")
            st.info(f"المسار الحالي: {file_path}")

elif menu == "بحث في الأرشيف":
    st.header("🔍 ابحث في وثائقك")
    search_query = st.text_input("أدخل كلمة للبحث عنها داخل الصور...")
    
    if search_query:
        c.execute("SELECT * FROM docs WHERE content LIKE ?", ('%' + search_query + '%',))
        results = c.fetchall()
        
        for res in results:
            with st.expander(f"📄 {res[1]}"):
                st.write(f"المحتوى المستخرج: {res[2]}")
                if os.path.exists(res[3]):
                    st.image(res[3], caption="معاينة من المجلد المزامَن")
                else:
                    st.warning("الملف موجود على السحابة ولكن غير محمل محلياً حالياً.")
