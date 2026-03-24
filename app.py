import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS احترافي لإجبار الألوان والقياسات على الأزرار
st.markdown("""
<style>
    /* تنسيق موحد لجميع الأزرار */
    div.stButton > button {
        width: 100% !important;
        height: 140px !important;
        border-radius: 12px !important;
        border: none !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        transition: 0.3s !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* تخصيص الألوان لكل زر بناءً على الـ Key */
    button[key="add"] { background-color: #28a745 !important; }
    button[key="search"] { background-color: #007bff !important; }
    button[key="edit"] { background-color: #fd7e14 !important; }
    button[key="delete"] { background-color: #dc3545 !important; }
    button[key="show"] { background-color: #6c757d !important; }
    button[key="link"] { background-color: #6f42c1 !important; }
    button[key="backup"] { background-color: #17a2b8 !important; }
    button[key="restore"] { background-color: #ffc107 !important; }

    /* تأثير عند تمرير الماوس */
    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        filter: brightness(1.1) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# إدارة حالة الصفحة
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

# --- صفحة إضافة مستند ---
def add_document_page():
    st.markdown("<h2 style='text-align: center;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة للوحة التحكم", key="back_btn"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    st.write("---")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار"])
            st.date_input("Enter document date", value=date.today())
            st.text_input("Enter sender")
            st.text_input("Enter receiver")
        with col2:
            st.text_input("Document subject")
            st.text_input("Keywords (comma separated)")
            st.text_input("Enter tags")
            st.text_area("Attachment description")
        
        st.file_uploader("رفع المرفقات للوثيقة", accept_multiple_files=True)
        if st.button("حفظ البيانات", use_container_width=True):
            st.success("✅ تم حفظ البيانات بنجاح!")

# --- لوحة التحكم ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>لوحة تحكم نظام الأرشفة</h1>", unsafe_allow_html=True)
    st.write("---")

    # الصف الأول (4 أعمدة)
    row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
    with row1_col1:
        if st.button("Add Document", key="add"):
            st.session_state['page'] = 'add_doc'
            st.rerun()
    with row1_col2:
        st.button("Search", key="search")
    with row1_col3:
        st.button("Edit Document", key="edit")
    with row1_col4:
        st.button("Delete Document", key="delete")

    # الصف الثاني (4 أعمدة)
    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
    with row2_col1:
        st.button("Show All Documents", key="show")
    with row2_col2:
        st.button("Link Documents", key="link")
    with row2_col3:
        st.button("Backup Data", key="backup")
    with row2_col4:
        st.button("Restore Backup", key="restore")

# التشغيل
if st.session_state['page'] == 'dashboard':
    main_dashboard()
elif st.session_state['page'] == 'add_doc':
    add_document_page()
