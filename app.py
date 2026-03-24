import streamlit as st

# إعدادات الصفحة الأساسية لجعلها عريضة واحترافية
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# تصميم CSS مخصص لجعل أزرار Streamlit تبدو كبطاقات ملونة كبيرة
st.markdown("""
    <style>
    /* تنسيق الحاوية الرئيسية */
    .main {
        background-color: #f8f9fa;
    }
    
    /* تنسيق الأزرار لتصبح بطاقات */
    div.stButton > button {
        height: 150px;
        width: 100%;
        border-radius: 15px;
        border: none;
        color: white !important;
        font-size: 22px !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px;
    }

    /* تأثير عند تمرير الماوس فوق البطاقة */
    div.stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        opacity: 0.9;
    }

    /* تخصيص الألوان لكل بطاقة بناءً على مفتاحها (Key) */
    div.stButton > button[key="Add Document"] { background-color: #28a745 !important; }      /* أخضر */
    div.stButton > button[key="Search"] { background-color: #007bff !important; }            /* أزرق */
    div.stButton > button[key="Edit Document"] { background-color: #fd7e14 !important; }      /* برتقالي */
    div.stButton > button[key="Delete Document"] { background-color: #dc3545 !important; }    /* أحمر */
    div.stButton > button[key="Show All Documents"] { background-color: #6c757d !important; } /* رمادي */
    div.stButton > button[key="Link Documents"] { background-color: #6f42c1 !important; }     /* أرجواني */
    div.stButton > button[key="Backup Data"] { background-color: #17a2b8 !important; }        /* سماوي */
    div.stButton > button[key="Restore Backup"] { background-color: #ffc107 !important; color: #333 !important; } /* أصفر */

    /* تنسيق صفحة تسجيل الدخول */
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- منطق تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>تسجيل الدخول</h2>", unsafe_allow_html=True)
        user = st.text_input("اسم المستخدم")
        pw = st.text_input("كلمة المرور", type="password")
        if st.button("دخول للنظام", key="login_btn"):
            if user == "admin" and pw == "1234": # يمكنك تغييرها لاحقاً
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

# --- منطق لوحة التحكم (Dashboard) ---
def main_dashboard():
    # الهيدر العلوي
    st.markdown("<h1 style='text-align: center; color: #333;'>نظام الأرشفة الإلكتروني</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>لوحة التحكم الرئيسية</p>", unsafe_allow_html=True)
    st.write("---")

    # الصف الأول من البطاقات
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Add Document", key="Add Document"):
            st.session_state.page = "add"
    with col2:
        if st.button("Search", key="Search"):
            st.session_state.page = "search"
    with col3:
        if st.button("Edit Document", key="Edit Document"):
            st.session_state.page = "edit"
    with col4:
        if st.button("Delete Document", key="Delete Document"):
            st.session_state.page = "delete"

    # الصف الثاني من البطاقات
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        if st.button("Show All Documents", key="Show All Documents"):
            st.session_state.page = "show_all"
    with col6:
        if st.button("Link Documents", key="Link Documents"):
            st.session_state.page = "link"
    with col7:
        if st.button("Backup Data", key="Backup Data"):
            st.session_state.page = "backup"
    with col8:
        if st.button("Restore Backup", key="Restore Backup"):
            st.session_state.page = "restore"

    # عرض حالة الضغط (للتجربة)
    if 'page' in st.session_state:
        st.info(f"أنت الآن في قسم: {st.session_state.page}")

    # زر الخروج في القائمة الجانبية
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- تشغيل التطبيق ---
if not st.session_state['logged_in']:
    login_page()
else:
    main_dashboard()
