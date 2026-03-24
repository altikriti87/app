import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS جبري للألوان والقياسات (استهداف مباشر للمكونات)
st.markdown("""
<style>
    /* تنسيق الحاوية لضمان الترتيب */
    [data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }

    /* التنسيق الموحد لجميع الأزرار ككروت */
    div.stButton > button {
        width: 100% !important;
        height: 140px !important;
        border-radius: 15px !important;
        border: none !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
        margin: 0px !important;
    }

    /* تلوين الأزرار بدقة باستخدام مفتاح الـ Key */
    button[key="add"] { background: #28a745 !important; }    /* أخضر */
    button[key="search"] { background: #007bff !important; } /* أزرق */
    button[key="edit"] { background: #fd7e14 !important; }   /* برتقالي */
    button[key="delete"] { background: #dc3545 !important; } /* أحمر */
    button[key="show"] { background: #6c757d !important; }   /* رمادي */
    button[key="link"] { background: #6f42c1 !important; }   /* أرجواني */
    button[key="backup"] { background: #17a2b8 !important; } /* سماوي */
    button[key="restore"] { background: #ffc107 !important; }/* أصفر */

    /* تأثير المرور (Hover) */
    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        filter: brightness(1.1) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# إدارة التنقل بين الصفحات
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

# --- صفحة إضافة مستند ---
def add_document_page():
    st.markdown("<h2 style='text-align: center; color: #28a745;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
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
        
        st.file_uploader("رفع المرفقات", accept_multiple_files=True)
        if st.button("حفظ المستند المؤرشف", key="save_doc", use_container_width=True):
            st.success("✅ تم الحفظ بنجاح!")

# --- لوحة التحكم الرئيسية ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>نظام الأرشفة الإلكتروني</h1>", unsafe_allow_html=True)
    st.write("---")

    # الصف الأول - 4 أعمدة
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Add Document", key="add"):
            st.session_state['page'] = 'add_doc'
            st.rerun()
    with c2: st.button("Search", key="search")
    with c3: st.button("Edit Document", key="edit")
    with c4: st.button("Delete Document", key="delete")

    # الصف الثاني - 4 أعمدة
    c5, c6, c7, c8 = st.columns(4)
    with c5: st.button("Show All", key="show")
    with c6: st.button("Link Documents", key="link")
    with c7: st.button("Backup Data", key="backup")
    with c8: st.button("Restore Backup", key="restore")

# التشغيل النهائي
if st.session_state['page'] == 'dashboard':
    main_dashboard()
elif st.session_state['page'] == 'add_doc':
    add_document_page()
