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

# 3. CSS لتحسين مظهر الأزرار
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
    if st.button("🔍 البحث عن مستند"): st.session_state['menu_option'] = 'بحث'  # الزر الجديد
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
        
        submit = st.form_submit_button("حفظ في الأرشيف")
        if submit:
            if subject and sender:
                new_doc = {
                    "الموضوع": subject,
                    "النوع": doc_type,
                    "تاريخ المستند": str(doc_date),
                    "المرسل": sender,
                    "المستلم": receiver,
                    "الوسوم": tags,
                    "تاريخ الأرشفة": str(date.today())
                }
                st.session_state['archive_data'].append(new_doc)
                st.success(f"✅ تم حفظ المستند '{subject}' بنجاح!")
            else:
                st.error("⚠️ يرجى ملء الحقول الأساسية")

# 3. صفحة البحث (الجديدة)
elif st.session_state['menu_option'] == 'بحث':
    st.header("🔍 البحث عن مستند")
    
    if not st.session_state['archive_data']:
        st.warning("لا توجد بيانات للبحث فيها. يرجى إضافة مستندات أولاً.")
    else:
        # خيارات البحث
        search_query = st.text_input("أدخل كلمة البحث (موضوع، مرسل، أو وسم):")
        search_col = st.selectbox("ابحث في حقل محدد:", ["الكل", "الموضوع", "المرسل", "الوسوم"])
        
        if search_query:
            df = pd.DataFrame(st.session_state['archive_data'])
            
            # منطق الفلترة
            if search_col == "الكل":
                mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            else:
                mask = df[search_col].str.contains(search_query, case=False)
            
            results = df[mask]
            
            if not results.empty:
                st.write(f"تم العثور على {len(results)} نتيجة:")
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                st.error("لم يتم العثور على نتائج تطابق بحثك.")

# 4. صفحة عرض الكل
elif st.session_state['menu_option'] == 'عرض':
    st.header("📊 جميع المستندات المؤرشفة")
    if st.session_state['archive_data']:
        df = pd.DataFrame(st.session_state['archive_data'])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("الأرشيف فارغ حالياً.")
