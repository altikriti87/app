import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. كود CSS (يجب أن يكون داخل st.markdown ليعمل)
st.markdown("""
<style>
    /* جعل الحاوية تسمح بتداخل العناصر */
    [data-testid="column"] {
        position: relative;
    }

    /* تصميم الكارت الملون */
    .custom-card {
        height: 140px;
        width: 100%;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }

    /* جعل زر ستريم ليت شفافاً تماماً ومطابقاً لحجم الكارت */
    .stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100% !important;
        height: 140px !important;
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10 !important;
        cursor: pointer;
    }

    /* إخفاء حدود الزر عند الضغط */
    .stButton > button:focus, .stButton > button:active {
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)

# إدارة التنقل
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

# --- صفحة إضافة مستند ---
def add_document_page():
    st.markdown("<h2 style='text-align: center;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة", key="back_nav"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    st.write("---")
    with st.form("doc_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار"])
            st.date_input("Enter document date", value=date.today())
            st.text_input("Enter sender")
            st.text_input("Enter receiver")
        with col2:
            st.text_input("Document subject")
            st.text_input("Keywords")
            st.text_input("Enter tags")
            st.text_area("Attachment description")
        
        st.file_uploader("رفع المرفقات", accept_multiple_files=True)
        if st.form_submit_button("حفظ البيانات", use_container_width=True):
            st.success("تم الحفظ بنجاح!")

# --- لوحة التحكم الرئيسية ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>لوحة تحكم نظام الأرشفة</h1>", unsafe_allow_html=True)
    st.write("---")

    # بيانات الكروت
    cards_data = [
        {"name": "Add Document", "color": "#28a745", "id": "add"},
        {"name": "Search", "color": "#007bff", "id": "search"},
        {"name": "Edit Document", "color": "#fd7e14", "id": "edit"},
        {"name": "Delete Document", "color": "#dc3545", "id": "delete"},
        {"name": "Show All Documents", "color": "#6c757d", "id": "show"},
        {"name": "Link Documents", "color": "#6f42c1", "id": "link"},
        {"name": "Backup Data", "color": "#17a2b8", "id": "backup"},
        {"name": "Restore Backup", "color": "#ffc107", "id": "restore"}
    ]

    # رسم الكروت في صفين (4 أعمدة لكل صف)
    for i in range(0, len(cards_data), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(cards_data):
                card = cards_data[i + j]
                with cols[j]:
                    # رسم الشكل الملون
                    st.markdown(f'<div class="custom-card" style="background-color: {card["color"]};">{card["name"]}</div>', unsafe_allow_html=True)
                    # وضع الزر الشفاف فوقه
                    if st.button("", key=f"btn_{card['id']}"):
                        if card['id'] == "add":
                            st.session_state['page'] = 'add_doc'
                            st.rerun()
                        else:
                            st.toast(f"تم اختيار: {card['name']}")

# التشغيل
if st.session_state['page'] == 'dashboard':
    main_dashboard()
else:
    add_document_page()
