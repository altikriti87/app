import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# CSS لإخفاء الأزرار وجعلها شفافة فوق البطاقات
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        height: 120px;
        background-color: transparent;
        color: transparent;
        border: none;
        position: absolute;
        z-index: 10;
    }
    .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.1);
        color: transparent;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# إدارة الحالة
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- الدوال ---

def login():
    st.markdown("<h2 style='text-align: center;'>تسجيل الدخول للنظام</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        if st.button("دخول", key="login_btn"):
            if username == "admin" and password == "1234":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("خطأ في البيانات")

def add_document_page():
    st.markdown("<h2 style='text-align: right;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة للوحة التحكم", key="back_home"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    st.write("---")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            doc_type = st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار", "أخرى"])
            doc_date = st.date_input("Enter document date", value=date.today())
            sender = st.text_input("Enter sender")
            receiver = st.text_input("Enter receiver")
        
        with col2:
            subject = st.text_input("Document subject")
            keywords = st.text_input("Keywords (comma separated)")
            tags = st.text_input("Enter tags (use - for words, , or ; for tags)")
            attach_desc = st.text_area("Attachment description or type")
        
        uploaded_files = st.file_uploader("رفع المرفقات", accept_multiple_files=True)
        
        if st.button("حفظ البيانات", use_container_width=True):
            st.success("تم الحفظ بنجاح (تجريبي)")

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
            # حاوية نسبية لجمع الزر مع التصميم
            st.markdown(f"""
            <div style="position: relative; height: 120px; margin-bottom: 20px;">
                <div style="
                    background-color: {card['color']};
                    height: 120px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                ">
                    {card['name']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # الزر الشفاف الذي يغطي البطاقة تماماً
            # ملاحظة: نضعه في "فراغ" فوق التصميم باستخدام CSS أعلاه
            if st.button("", key=f"btn_{card['id']}"):
                if card['id'] == "add":
                    st.session_state['page'] = 'add_doc'
                    st.rerun()
                else:
                    st.toast(f"تم اختيار {card['name']}")

# --- منطق التشغيل ---
if not st.session_state['logged_in']:
    login()
else:
    if st.session_state['page'] == 'dashboard':
        main_dashboard()
    elif st.session_state['page'] == 'add_doc':
        add_document_page()
