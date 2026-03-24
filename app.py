import streamlit as st
from datetime import date

st.set_page_config(page_title="نظام الأرشفة", layout="wide", initial_sidebar_state="collapsed")

# CSS لإجبار الأزرار على أخذ شكل الكروت والألوان
st.markdown("""
<style>
    /* تنسيق عام لكل الأزرار */
    div.stButton > button {
        width: 100% !important;
        height: 140px !important;
        border-radius: 15px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        transition: 0.3s !important;
    }

    /* ربط الألوان بالترتيب (الأعمدة) */
    /* الصف الأول */
    div[data-testid="column"]:nth-of-type(1) button { background-color: #28a745 !important; }
    div[data-testid="column"]:nth-of-type(2) button { background-color: #007bff !important; }
    div[data-testid="column"]:nth-of-type(3) button { background-color: #fd7e14 !important; }
    div[data-testid="column"]:nth-of-type(4) button { background-color: #dc3545 !important; }
    
    /* الصف الثاني (في بعض المتصفحات نحتاج لتحديد أدق) */
    div[data-testid="stHorizontalBlock"]:nth-of-type(3) div[data-testid="column"]:nth-of-type(1) button { background-color: #6c757d !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(3) div[data-testid="column"]:nth-of-type(2) button { background-color: #6f42c1 !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(3) div[data-testid="column"]:nth-of-type(3) button { background-color: #17a2b8 !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(3) div[data-testid="column"]:nth-of-type(4) button { background-color: #ffc107 !important; }

    div.stButton > button:hover {
        transform: scale(1.03) !important;
        filter: brightness(1.1) !important;
    }
</style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state['page'] = 'main'

if st.session_state['page'] == 'main':
    st.markdown("<h1 style='text-align: center;'>لوحة التحكم</h1>", unsafe_allow_html=True)
    
    # الصف الأول
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Add Document"): 
            st.session_state['page'] = 'add'
            st.rerun()
    with col2: st.button("Search")
    with col3: st.button("Edit Document")
    with col4: st.button("Delete Document")

    # الصف الثاني
    col5, col6, col7, col8 = st.columns(4)
    with col5: st.button("Show All")
    with col6: st.button("Link Documents")
    with col7: st.button("Backup Data")
    with col8: st.button("Restore Backup")

elif st.session_state['page'] == 'add':
    st.header("إضافة مستند جديد")
    if st.button("عودة"): 
        st.session_state['page'] = 'main'
        st.rerun()
    
    # حقول الإدخال
    doc_type = st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار"])
    doc_date = st.date_input("Enter document date", value=date.today())
    sender = st.text_input("Enter sender")
    receiver = st.text_input("Enter receiver")
    subject = st.text_input("Document subject")
    keywords = st.text_input("Keywords (comma separated)")
    tags = st.text_input("Enter tags")
    desc = st.text_area("Attachment description")
    files = st.file_uploader("رفع المرفقات", accept_multiple_files=True)
    if st.button("حفظ"): st.success("تم الحفظ!")
