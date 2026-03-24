import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS سحري لجعل الأزرار شفافة وتغطي البطاقات بالكامل
st.markdown("""
<style>
    /* جعل حاوية الزر تأخذ وضعية مطلقة فوق البطاقة */
    .stButton {
        position: relative;
    }
    .stButton > button {
        position: absolute;
        top: -140px; /* يغطي ارتفاع البطاقة */
        left: 0;
        width: 100%;
        height: 120px;
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10;
    }
    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.1) !important; /* تأثير بسيط عند المرور */
        border: none !important;
    }
    .stButton > button:active {
        background-color: rgba(0, 0, 0, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# إدارة حالة التنقل
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- صفحة إضافة مستند ---
def add_document_page():
    st.markdown("<h2 style='text-align: right;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة للوحة التحكم"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    st.write("---")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            doc_type = st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار", "أخرى"])
            # التاريخ الافتراضي هو اليوم
            doc_date = st.date_input("Enter document date", value=date.today())
            sender = st.text_input("Enter sender")
            receiver = st.text_input("Enter receiver")
        
        with col2:
            subject = st.text_input("Document subject")
            keywords = st.text_input("Keywords (comma separated)")
            tags = st.text_input("Enter tags (use - for words, , or ; for tags)")
            attach_desc = st.text_area("Attachment description or type")
        
        uploaded_files = st.file_uploader("رفع المرفقات للوثيقة", accept_multiple_files=True)
        
        if st.button("حفظ المستند", use_container_width=True):
            st.success("✅ تم حفظ البيانات بنجاح!")

# --- لوحة التحكم الرئيسية ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center; color: #333;'>لوحة تحكم نظام الأرشفة</h1>", unsafe_allow_html=True)
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

    cols = st.columns(4)
    for index, card in enumerate(cards):
        with cols[index % 4]:
            # 1. تصميم البطاقة (HTML)
            st.markdown(f"""
            <div style="
                background-color: {card['color']};
                height: 120px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 19px;
                font-weight: bold;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            ">
                {card['name']}
            </div>
            """, unsafe_allow_html=True)
            
            # 2. الزر المخفي (الذي يتم تفعيله بالضغط)
            if st.button("", key=f"btn_{card['id']}"):
                if card['id'] == "add":
                    st.session_state['page'] = 'add_doc'
                    st.rerun()
                else:
                    st.toast(f"الخدمة {card['name']} قيد البرمجة")

# --- منطق التشغيل ---
if not st.session_state['logged_in']:
    # دالة تسجيل الدخول المبسطة
    st.markdown("<h2 style='text-align: center;'>تسجيل الدخول</h2>", unsafe_allow_html=True)
    user = st.text_input("User")
    pw = st.text_input("Pass", type="password")
    if st.button("دخول"):
        if user == "admin" and pw == "1234":
            st.session_state['logged_in'] = True
            st.rerun()
else:
    if st.session_state['page'] == 'dashboard':
        main_dashboard()
    elif st.session_state['page'] == 'add_doc':
        add_document_page()
