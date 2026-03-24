import streamlit as st
from datetime import date

# إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# إدارة الحالة (Navigation)
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 1. دالة تسجيل الدخول
def login():
    st.markdown("<h2 style='text-align: center;'>تسجيل الدخول للنظام</h2>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            if st.button("دخول", use_container_width=True):
                if username == "admin" and password == "1234":
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("خطأ في البيانات")

# 2. صفحة إضافة مستند (Add Document)
def add_document_page():
    st.markdown("<h2 style='text-align: center;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ العودة للوحة التحكم"):
        st.session_state['page'] = 'dashboard'
        st.rerun()

    with st.form("document_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            doc_type = st.selectbox("Document Type", ["كتاب رسمي", "تقرير", "عقد", "مراسلة internal"])
            doc_date = st.date_input("Enter document date", value=date.today())
            sender = st.text_input("Enter sender")
            receiver = st.text_input("Enter receiver")

        with col2:
            subject = st.text_input("Document subject")
            keywords = st.text_input("Keywords (comma separated)", placeholder="e.g. finance, urgent, 2024")
            tags = st.text_input("Enter tags", placeholder="tag-one, tag-two")
            attachment_desc = st.text_area("Attachment description or type")
        
        uploaded_file = st.file_uploader("رفع المرفقات (Attachments)", accept_multiple_files=True)

        submit_btn = st.form_submit_button("حفظ المستند")
        
        if submit_btn:
            # هنا يمكنك إضافة كود حفظ البيانات في قاعدة البيانات
            st.success("تم حفظ المستند بنجاح!")

# 3. الواجهة الرئيسية
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
            # تصميم البطاقة
            st.markdown(f"""
                <div style="
                    background-color: {card['color']};
                    padding: 30px 10px;
                    border-radius: 12px 12px 0 0;
                    text-align: center;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                ">
                    {card['name']}
                </div>
            """, unsafe_allow_html=True)
            
            # زر التفاعل أسفل كل بطاقة
            if st.button(f"فتح {card['name']}", key=card['id'], use_container_width=True):
                if card['id'] == "add":
                    st.session_state['page'] = 'add_doc'
                    st.rerun()
                else:
                    st.info(f"تم النقر على {card['name']} - هذه الخاصية قيد التطوير")

# منطق التشغيل النهائي
if not st.session_state['logged_in']:
    login()
else:
    if st.session_state['page'] == 'dashboard':
        main_dashboard()
    elif st.session_state['page'] == 'add_doc':
        add_document_page()
