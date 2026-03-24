import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS احترافي لتحويل الأزرار إلى كروت ملونة بالكامل
st.markdown("""
<style>
    /* تنسيق عام لكل الأزرار في الصفحة */
    div.stButton > button {
        width: 100%;
        height: 140px;
        border-radius: 12px;
        border: none;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* تخصيص الألوان بناءً على مفتاح الزر (Key) */
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
        transform: translateY(-5px);
        filter: brightness(1.1);
        color: white !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    
    /* إلغاء أي حدود افتراضية من ستريم ليت */
    div.stButton > button:focus, div.stButton > button:active {
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# إدارة الحالة (Navigation)
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- دالة صفحة الإضافة ---
def add_document_page():
    st.markdown("<h2 style='text-align: center;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة للوحة التحكم", key="back_nav"):
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
            st.success("تم الحفظ بنجاح!")

# --- لوحة التحكم ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>لوحة تحكم نظام الأرشفة</h1>", unsafe_allow_html=True)
    st.write("---")

    # توزيع الكروت في صفين (4 أعمدة لكل صف)
    row1 = st.columns(4)
    row2 = st.columns(4)

    # الصف الأول
    with row1[0]:
        if st.button("Add Document", key="add"):
            st.session_state['page'] = 'add_doc'
            st.rerun()
    with row1[1]:
        st.button("Search", key="search")
    with row1[2]:
        st.button("Edit Document", key="edit")
    with row1[3]:
        st.button("Delete Document", key="delete")

    # الصف الثاني
    with row2[0]:
        st.button("Show All Documents", key="show")
    with row2[1]:
        st.button("Link Documents", key="link")
    with row2[2]:
        st.button("Backup Data", key="backup")
    with row2[3]:
        st.button("Restore Backup", key="restore")

# --- التنفيذ ---
if not st.session_state['logged_in']:
    # شاشة دخول بسيطة جداً للتجربة
    if st.button("اضغط هنا للدخول للنظام (محاكاة)"):
        st.session_state['logged_in'] = True
        st.rerun()
else:
    if st.session_state['page'] == 'dashboard':
        main_dashboard()
    elif st.session_state['page'] == 'add_doc':
        add_document_page()
