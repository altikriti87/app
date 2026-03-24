import streamlit as st
import pandas as pd
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide")

# 2. تهيئة مخزن البيانات
if 'archive_data' not in st.session_state:
    st.session_state['archive_data'] = []

if 'menu_option' not in st.session_state:
    st.session_state['menu_option'] = 'الرئيسية'

# 3. CSS لتحسين مظهر الأزرار الجانبية
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        text-align: right;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .stButton > button:hover {
        border-color: #28a745;
        color: #28a745;
    }
</style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.title("🗄️ نظام الأرشفة")
    st.write("---")
    if st.button("🏠 الصفحة الرئيسية"): st.session_state['menu_option'] = 'الرئيسية'
    if st.button("➕ إضافة مستند جديد"): st.session_state['menu_option'] = 'إضافة'
    if st.button("🔍 البحث عن مستند"): st.session_state['menu_option'] = 'بحث'
    if st.button("📊 عرض الكل"): st.session_state['menu_option'] = 'عرض'
    st.write("---")
    if st.button("🚪 خروج", key="logout"): st.info("تم تسجيل الخروج")

# --- محتوى الصفحة الرئيسي ---

# 1. الصفحة الرئيسية
if st.session_state['menu_option'] == 'الرئيسية':
    st.title("لوحة التحكم الرئيسية")
    total_docs = len(st.session_state['archive_data'])
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المستندات", total_docs)
    col2.metric("مستندات اليوم", sum(1 for d in st.session_state['archive_data'] if d['تاريخ الأرشفة'] == str(date.today())))
    col3.metric("حالة النظام", "متصل")

# 2. صفحة إضافة مستند (مع خاصية رفع الملفات)
elif st.session_state['menu_option'] == 'إضافة':
    st.header("➕ إضافة مستند جديد وأرشفة الوثائق")
    
    with st.form("add_doc_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            doc_type = st.selectbox("نوع المستند", ["كتاب رسمي", "تعميم", "قرار", "تقرير", "عقد"])
            doc_date = st.date_input("تاريخ المستند", value=date.today())
            sender = st.text_input("الجهة المرسلة (Sender)")
        with c2:
            subject = st.text_input("الموضوع (Subject)")
            receiver = st.text_input("الجهة المستلمة (Receiver)")
            tags = st.text_input("الكلمات الدلالية / الوسوم")
        
        st.write("---")
        # خاصية رفع الوثائق
        uploaded_files = st.file_uploader("📂 اختر الوثائق لرفعها (PDF, Image, Docx)", accept_multiple_files=True)
        
        submit = st.form_submit_button("حفظ المستند والملفات")
        
        if submit:
            if subject and sender:
                # استخراج أسماء الملفات المرفوعة
                file_names = [file.name for file in uploaded_files] if uploaded_files else ["لا توجد مرفقات"]
                
                new_doc = {
                    "الموضوع": subject,
                    "النوع": doc_type,
                    "تاريخ المستند": str(doc_date),
                    "المرسل": sender,
                    "المستلم": receiver,
                    "الوسوم": tags,
                    "المرفقات": ", ".join(file_names), # حفظ أسماء الملفات كالنص
                    "تاريخ الأرشفة": str(date.today())
                }
                st.session_state['archive_data'].append(new_doc)
                st.success(f"✅ تم حفظ المستند '{subject}' مع {len(uploaded_files)} ملف مرفق!")
            else:
                st.error("⚠️ يرجى ملء الحقول الأساسية (الموضوع والجهة المرسلة)")

# 3. صفحة البحث
elif st.session_state['menu_option'] == 'بحث':
    st.header("🔍 البحث في الأرشيف")
    query = st.text_input("ابحث عن مستند (بواسطة الموضوع، المرسل، أو اسم الملف المرفق):")
    if query and st.session_state['archive_data']:
        df = pd.DataFrame(st.session_state['archive_data'])
        results = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)]
        st.dataframe(results, use_container_width=True, hide_index=True)

# 4. صفحة عرض الكل
elif st.session_state['menu_option'] == 'عرض':
    st.header("📊 سجل الأرشيف الكامل")
    if st.session_state['archive_data']:
        df = pd.DataFrame(st.session_state['archive_data'])
        # عرض الجدول مع عمود المرفقات
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("الأرشيف فارغ.")
