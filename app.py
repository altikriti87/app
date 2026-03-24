import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS القوي والمباشر لتلوين الأزرار حسب ترتيبها
st.markdown("""
<style>
    /* تنسيق الحاوية الكبيرة للأزرار */
    .stColumn {
        padding: 5px !important;
    }

    /* التنسيق الموحد لجميع الأزرار */
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
    }

    /* تلوين الأزرار حسب ترتيب ظهورها في الصفحة */
    /* الصف الأول */
    div.stColumn:nth-of-type(1) div.stButton > button { background-color: #28a745 !important; } /* أخضر */
    div.stColumn:nth-of-type(2) div.stButton > button { background-color: #007bff !important; } /* أزرق */
    div.stColumn:nth-of-type(3) div.stButton > button { background-color: #fd7e14 !important; } /* برتقالي */
    div.stColumn:nth-of-type(4) div.stButton > button { background-color: #dc3545 !important; } /* أحمر */

    /* الصف الثاني (يبدأ من العمود 5 تقنياً في بعض النسخ أو يعيد العد) */
    /* ملاحظة: لضمان عملها على كل النسخ، نستخدم كود إضافي */
    
    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        filter: brightness(1.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# إدارة التنقل
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

# --- صفحة الإضافة ---
def add_document_page():
    st.markdown("<h2 style='text-align: center;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ عودة"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار"])
            st.date_input("Enter document date", value=date.today())
            st.text_input("Enter sender")
            st.text_input("Enter receiver")
        with c2:
            st.text_input("Document subject")
            st.text_input("Keywords")
            st.text_input("Enter tags")
            st.text_area("Attachment description")
        
        st.file_uploader("رفع المرفقات", accept_multiple_files=True)
        if st.form_submit_button("حفظ", use_container_width=True):
            st.success("تم الحفظ")

# --- لوحة التحكم ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>نظام الأرشفة الإلكتروني</h1>", unsafe_allow_html=True)
    st.write("---")

    # الصف الأول
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Add Document"):
            st.session_state['page'] = 'add_doc'
            st.rerun()
    with col2: st.button("Search")
    with col3: st.button("Edit Document")
    with col4: st.button("Delete Document")

    # الصف الثاني (سنستخدم كود CSS مختلف قليلاً لتلوينها)
    # لإبقاء الكود بسيطاً ومضمون الألوان، سنستخدم Markdown مدمج للألوان المتبقية
    
    col5, col6, col7, col8 = st.columns(4)
    with col5: 
        st.markdown("<style>div[data-testid='stHorizontalBlock'] > div:nth-child(1) button { background-color: #6c757d !important; }</style>", unsafe_allow_html=True)
        st.button("Show All")
    with col6:
        st.markdown("<style>div[data-testid='stHorizontalBlock'] > div:nth-child(2) button { background-color: #6f42c1 !important; }</style>", unsafe_allow_html=True)
        st.button("Link Docs")
    with col7:
        st.markdown("<style>div[data-testid='stHorizontalBlock'] > div:nth-child(3) button { background-color: #17a2b8 !important; }</style>", unsafe_allow_html=True)
        st.button("Backup")
    with row_8 := col8:
        st.markdown("<style>div[data-testid='stHorizontalBlock'] > div:nth-child(4) button { background-color: #ffc107 !important; }</style>", unsafe_allow_html=True)
        st.button("Restore")

# التشغيل
if st.session_state['page'] == 'dashboard':
    main_dashboard()
else:
    add_document_page()
