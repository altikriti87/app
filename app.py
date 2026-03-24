import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. كود CSS المطور (لحل مشكلة الضغط فوق الكلمة)
st.markdown("""
<style>
    /* حاوية العمود */
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
        /* السر هنا: تجعل النص لا يعترض النقرات */
        pointer-events: none; 
    }

    /* تصميم زر ستريم ليت الشفاف */
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

    /* تأثيرات عند تمرير الماوس فوق الكارت */
    .stButton > button:hover {
        border: 2px solid rgba(255,255,255,0.5) !important;
        background-color: rgba(255,255,255,0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# إدارة التنقل
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

# --- صفحة إضافة مستند ---
def add_document_page():
    st.markdown("<h2 style='text-align: center;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة للوحة التحكم", key="back_home"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    st.write("---")
    with st.form("archive_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار", "تقرير"])
            st.date_input("Enter document date", value=date.today())
            st.text_input("Enter sender")
            st.text_input("Enter receiver")
        with col2:
            st.text_input("Document subject")
            st.text_input("Keywords (comma separated)")
            st.text_input("Enter tags")
            st.text_area("Attachment description")
        
        st.file_uploader("رفع المرفقات", accept_multiple_files=True)
        if st.form_submit_button("حفظ المستند", use_container_width=True):
            st.success("تم الحفظ بنجاح!")

# --- لوحة التحكم الرئيسية ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>لوحة تحكم نظام الأرشفة</h1>", unsafe_allow_html=True)
    st.write("---")

    cards = [
        {"name": "Add Document", "color": "#28a745", "id": "add"},
        {"name": "Search", "color": "#007bff", "id": "search"},
        {"name": "Edit Document", "color": "#fd7e14", "id": "edit"},
        {"name": "Delete Document", "color": "#dc3545", "id": "delete"},
        {"name": "Show All Documents", "color": "#6c757d", "id": "show"},
        {"name": "Link Documents", "color": "#6f42c1", "id": "link"},
        {"name": "Backup Data", "color": "#17a2b8", "id": "backup"},
        {"name": "Restore Backup", "color": "#ffc107", "id": "restore"}
    ]

    # رسم الكروت في صفوف (4 في كل صف)
    for i in range(0, len(cards), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(cards):
                card = cards[i + j]
                with cols[j]:
                    # 1. طبقة التصميم (الخلفية الملونة والنص)
                    st.markdown(f'<div class="custom-card" style="background-color: {card["color"]};">{card["name"]}</div>', unsafe_allow_html=True)
                    # 2. طبقة الزر (الشفافة التي تغطي كل شيء وتستقبل النقرات)
                    if st.button("", key=f"btn_{card['id']}"):
                        if card['id'] == "add":
                            st.session_state['page'] = 'add_doc'
                            st.rerun()
                        else:
                            st.toast(f"تم النقر على {card['name']}")

# التشغيل
if st.session_state['page'] == 'dashboard':
    main_dashboard()
else:
    add_document_page()
