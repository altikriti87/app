import streamlit as st
import pandas as pd
import openpyxl
import os
from datetime import datetime
from PyPDF2 import PdfMerger

# --- الإعدادات الثابتة ---
EXCEL_FILE = "archive.xlsx"
ARCHIVE_FOLDER = "archive_files"
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

# --- نظام الحماية (كلمة السر) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 نظام أرشفة مكتب إشبيلية")
        pwd = st.text_input("أدخل كلمة المرور للدخول:", type="password")
        if st.button("دخول"):
            if pwd == "Seville2026": # يمكنك تغيير كلمة السر هنا
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة")
        return False
    return True

# --- وظائف قاعدة البيانات (نفس منطق البوت) ---
def load_data():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            "ID NO", "Type", "Document Number", "Document Date", "From", "To",
            "Subject", "Keywords", "Attachment Description", "File Names"
        ])
        df.to_excel(EXCEL_FILE, index=False)
    return pd.read_excel(EXCEL_FILE)

# --- الواجهة الرئيسية ---
if check_password():
    st.sidebar.title("📑 القائمة الرئيسية")
    menu = st.sidebar.radio("اختر العملية:", ["🔍 بحث وعرض", "➕ إضافة وثيقة جديدة", "🔄 النسخ الاحتياطي"])

    df = load_data()

    # --- القسم 1: البحث وعرض التفاصيل ---
    if menu == "🔍 بحث وعرض":
        st.header("🔍 البحث في الأرشيف")
        search_q = st.text_input("ابحث برقم الوثيقة، الجهة، أو الموضوع:")
        
        if search_q:
            # البحث في كل الأعمدة
            results = df[df.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)]
            st.write(f"تم العثور على {len(results)} نتيجة:")
            
            for index, row in results.iterrows():
                with st.expander(f"📄 {row['Type']} - رقم {row['Document Number']} ({row['Subject']})"):
                    st.write(f"**من:** {row['From']} | **إلى:** {row['To']}")
                    st.write(f"**التاريخ:** {row['Document Date']}")
                    st.write(f"**الكلمات المفتاحية:** {row['Keywords']}")
                    
                    # عرض الملفات المرفقة
                    if pd.notna(row['File Names']):
                        files = str(row['File Names']).split(";")
                        for f in files:
                            f_path = os.path.join(ARCHIVE_FOLDER, f)
                            if os.path.exists(f_path):
                                with open(f_path, "rb") as file:
                                    st.download_button(f"تحميل {f}", file, file_name=f)

    # --- القسم 2: إضافة وثيقة ---
    elif menu == "➕ إضافة وثيقة جديدة":
        st.header("📤 أرشفة وثيقة جديدة")
        with st.form("upload_form"):
            col1, col2 = st.columns(2)
            with col1:
                doc_type = st.selectbox("النوع", ["Incoming", "Outgoing"])
                doc_num = st.text_input("رقم الوثيقة")
                doc_date = st.date_input("تاريخ الوثيقة")
            with col2:
                doc_from = st.text_input("من")
                doc_to = st.text_input("إلى")
                subject = st.text_input("الموضوع")
            
            keywords = st.text_area("الكلمات المفتاحية")
            uploaded_files = st.file_uploader("ارفق الملفات (PDF/صور)", accept_multiple_files=True)
            
            if st.form_submit_button("حفظ الأرشفة"):
                # حفظ الملفات في المجلد
                saved_filenames = []
                for f in uploaded_files:
                    f_path = os.path.join(ARCHIVE_FOLDER, f.name)
                    with open(f_path, "wb") as buffer:
                        buffer.write(f.getbuffer())
                    saved_filenames.append(f.name)
                
                # إضافة البيانات للاكسل
                new_row = {
                    "ID NO": datetime.now().strftime("%y%m%d%H%M%S"),
                    "Type": doc_type,
                    "Document Number": doc_num,
                    "Document Date": doc_date.strftime("%Y-%m-%d"),
                    "From": doc_from,
                    "To": doc_to,
                    "Subject": subject,
                    "Keywords": keywords,
                    "File Names": ";".join(saved_filenames)
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_excel(EXCEL_FILE, index=False)
                st.success("✅ تم حفظ الوثيقة بنجاح في الأرشيف")
