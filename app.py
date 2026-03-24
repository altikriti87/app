import streamlit as st
import pandas as pd
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide")

# 2. تهيئة مخزن البيانات (إذا لم يكن موجوداً)
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
    if st.button("📊 عرض الكل"): st.session_state['menu_option'] = 'عرض'
    st.write("---")
    if st.button("🚪 خروج", key="logout"): st.info("تم تسجيل الخروج")

# --- محتوى الصفحة الرئيسي ---

# 1. الصفحة الرئيسية (إحصائيات)
if st.session_state['menu_option'] == 'الرئيسية':
    st.title("لوحة التحكم الرئيسية")
    total_docs = len(st.session_state['archive_data'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المستندات المؤرشفة", total_docs)
    col2.metric("مستندات اليوم", sum(1 for d in st.session_state['archive_data'] if d['تاريخ الأرشفة'] == str(date.today())))
    col3.metric("حالة النظام", "متصل")

# 2. صفحة إضافة مستند
elif st.session_state['menu_option'] == 'إضافة':
    st.header("إضافة مستند جديد")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            doc_type = st.selectbox("نوع المستند", ["كتاب رسمي", "تعميم", "قرار", "تقرير"])
            doc_date = st.date_input("تاريخ المستند", value=date.today())
            sender = st.text_input("الجهة المرسلة")
        with c2:
            subject = st.text_input("الموضوع (Subject)")
            receiver = st.text_input("الجهة المستلمة")
            tags = st.text_input("الكلمات الدلالية / الوسوم")
        
        uploaded_files = st.file_uploader("إرفاق الملفات", accept_multiple_files=True)
        submit = st.form_submit_button("حفظ في الأرشيف")
        
        if submit:
            if subject and sender:
                # إنشاء قاموس بالبيانات الجديدة
                new_doc = {
                    "الموضوع": subject,
                    "النوع": doc_type,
                    "تاريخ المستند": str(doc_date),
                    "المرسل": sender,
                    "المستلم": receiver,
                    "الوسوم": tags,
                    "تاريخ الأرشفة": str(date.today())
                }
                # إضافة البيانات للمخزن
                st.session_state['archive_data'].append(new_doc)
                st.success(f"✅ تم حفظ المستند '{subject}' بنجاح!")
            else:
                st.error("⚠️ يرجى ملء الحقول الأساسية (الموضوع والجهة المرسلة)")

# 3. صفحة عرض الكل
elif st.session_state['menu_option'] == 'عرض':
    st.header("📊 جميع المستندات المؤرشفة")
    
    if len(st.session_state['archive_data']) > 0:
        # تحويل قائمة البيانات إلى DataFrame (جدول)
        df = pd.DataFrame(st.session_state['archive_data'])
        
        # إضافة خاصية البحث داخل الجدول
        search_term = st.text_input("🔍 بحث سريع في الجدول...", "")
        if search_term:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        
        # عرض الجدول بشكل تفاعلي
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # خيار تحميل البيانات كملف Excel
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير (CSV)", data=csv, file_name="archive_report.csv", mime="text/csv")
    else:
        st.warning("لا توجد مستندات مؤرشفة حالياً. قم بإضافة مستند أولاً.")
