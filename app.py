import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS مخصص لصبغ الأزرار وتحويلها لكروت ملونة (نفس الألوان والقياسات)
st.markdown("""
<style>
    /* تنسيق موحد لجميع الكروت */
    div.stButton > button {
        width: 100%;
        height: 140px;
        border-radius: 12px;
        border: none;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold;
        transition: 0.3s;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    /* تخصيص الألوان لكل كارت بناءً على الـ Key */
    button[key="add"] { background-color: #28a745 !important; }    /* أخضر */
    button[key="search"] { background-color: #007bff !important; } /* أزرق */
    button[key="edit"] { background-color: #fd7e14 !important; }   /* برتقالي */
    button[key="delete"] { background-color: #dc3545 !important; } /* أحمر */
    button[key="show"] { background-color: #6c757d !important; }   /* رمادي */
    button[key="link"] { background-color: #6f42c1 !important; }   /* أرجواني */
    button[key="backup"] { background-color: #17a2b8 !important; } /* سماوي */
    button[key="restore"] { background-color: #ffc107 !important; }/* أصفر */

    /* تأثيرات عند تمرير الماوس فوق الكارت */
    div.stButton > button:hover {
        transform: translateY(-5px);
        filter: brightness(1.1);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        color: white !important;
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
    st.markdown("<h2 style='text-align: center;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة للوحة التحكم", key="back_btn"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    st.write("---")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار", "تقرير"])
            st.date_input("Enter document date", value=date.today()) # التاريخ الافتراضي اليوم
            st.text_input("Enter sender")
            st.text_input("Enter receiver")
        
        with col2:
            st.text_input("Document subject")
            st.text_input("Keywords (comma separated)")
            st.text_input("Enter tags (use - for words, , or ; for tags)")
            st.text_area("Attachment description or type")
        
        st.file_uploader("رفع الملفات المرفقة للوثيقة", accept_multiple_files=True)
        
        if st.button("حفظ المستند المؤرشف", use_container_width=True):
            st.success("✅ تم حفظ البيانات وإرشفة الملفات بنجاح!")

# --- لوحة التحكم الرئيسية ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center; color: #333;'>لوحة تحكم نظام الأرشفة</h1>", unsafe_allow_html=True)
    st.write("---")

    # توزيع الكروت في صفين (4 أعمدة لكل صف)
    row1 = st.columns(4)
    row2 = st.columns(4)

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

    with row2[0]:
        st.button("Show All Documents", key="show")
    with row2[1]:
        st.button("Link Documents", key="link")
    with row2[2]:
        st.button("Backup Data", key="backup")
    with row2[3]:
        st.button("Restore Backup", key="restore")

# --- منطق التشغيل ---
if not st.session_state['logged_in']:
    st.markdown("<div style='text-align:center'><h3>تسجيل الدخول</h3></div>", unsafe_allow_html=True)
    user = st.text_input("اسم المستخدم")
    pwd = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if user == "admin" and pwd == "1234":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("البيانات غير صحيحة")
else:
    if st.session_state['page'] == 'dashboard':
        main_dashboard()
    elif st.session_state['page'] == 'add_doc':
        add_document_page()
