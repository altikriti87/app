import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS متطور لتحويل الأزرار إلى كروت تفاعلية بالكامل
st.markdown("""
<style>
    /* تنسيق الحاوية لتبدو ككارت */
    div.stButton > button {
        display: block;
        width: 100%;
        height: 150px; /* طول الكارت */
        border-radius: 15px;
        border: none;
        color: white !important;
        font-size: 22px !important;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 10px;
    }

    /* تخصيص الألوان لكل زر بناءً على المفتاح (Key) */
    button[key="add"] { background-color: #28a745 !important; }
    button[key="search"] { background-color: #007bff !important; }
    button[key="edit"] { background-color: #fd7e14 !important; }
    button[key="delete"] { background-color: #dc3545 !important; }
    button[key="show"] { background-color: #6c757d !important; }
    button[key="link"] { background-color: #6f42c1 !important; }
    button[key="backup"] { background-color: #17a2b8 !important; }
    button[key="restore"] { background-color: #ffc107 !important; }

    /* تأثير الحركية عند تمرير الماوس فوق أي مكان في الكارت */
    div.stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        filter: brightness(1.1);
        border: none !important;
    }
    
    /* إلغاء تأثير الضغط الافتراضي المشوه */
    div.stButton > button:active {
        transform: scale(0.98);
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# إدارة حالة التطبيق
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- صفحة إضافة مستند ---
def add_document_page():
    st.markdown("<h2 style='text-align: center;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة للوحة التحكم", key="back_btn"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    st.divider()
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار", "تقرير"])
            st.date_input("Enter document date", value=date.today())
            st.text_input("Enter sender")
            st.text_input("Enter receiver")
        with col2:
            st.text_input("Document subject")
            st.text_input("Keywords (comma separated)")
            st.text_input("Enter tags (use - or ;)")
            st.text_area("Attachment description")
        
        st.file_uploader("رفع المرفقات للوثيقة", accept_multiple_files=True)
        
        if st.button("حفظ البيانات الآن", use_container_width=True, type="primary"):
            st.success("✅ تم الحفظ بنجاح!")

# --- لوحة التحكم ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>لوحة تحكم نظام الأرشفة</h1>", unsafe_allow_html=True)
    st.write("---")

    # تقسيم الكروت إلى صفوف وأعمدة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Add Document", key="add"):
            st.session_state['page'] = 'add_doc'
            st.rerun()

    with col2:
        if st.button("Search", key="search"):
            st.toast("جاري فتح البحث...")

    with col3:
        st.button("Edit Document", key="edit")

    with col4:
        st.button("Delete Document", key="delete")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.button("Show All", key="show")
    with col6:
        st.button("Link Documents", key="link")
    with col7:
        st.button("Backup Data", key="backup")
    with col8:
        st.button("Restore Backup", key="restore")

# التشغيل
if not st.session_state['logged_in']:
    # محاكاة تسجيل الدخول لغرض العرض
    st.info("اضغط على الزر أدناه للدخول للنظام")
    if st.button("تسجيل الدخول (تجريبي)"):
        st.session_state['logged_in'] = True
        st.rerun()
else:
    if st.session_state['page'] == 'dashboard':
        main_dashboard()
    elif st.session_state['page'] == 'add_doc':
        add_document_page()
