import streamlit as st

# إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# تصميم CSS لمطابقة الصورة تماماً
st.markdown("""
    <style>
    /* تنسيق الحاوية والأزرار */
    div.stButton > button {
        height: 120px;
        width: 100%;
        border-radius: 10px;
        border: none;
        color: white !important;
        font-size: 22px !important;
        font-weight: 800 !important; /* خط سميك جداً */
        transition: 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 10px;
        text-transform: none; /* للحفاظ على حالة الأحرف كما هي */
    }

    /* تأثير عند تمرير الماوس */
    div.stButton > button:hover {
        opacity: 0.85;
        transform: scale(1.01);
    }

    /* الألوان المخصصة لكل زر بناءً على صورتك */
    /* الصف الأول */
    div.stButton > button[key="Add Document"] { background-color: #28a745 !important; }      /* أخضر */
    div.stButton > button[key="Search"] { background-color: #007bff !important; }            /* أزرق */
    div.stButton > button[key="Edit Document"] { background-color: #fd7e14 !important; }      /* برتقالي */
    div.stButton > button[key="Delete Document"] { background-color: #dc3545 !important; }    /* أحمر */
    
    /* الصف الثاني */
    div.stButton > button[key="Show All Documents"] { background-color: #6c757d !important; } /* رمادي */
    div.stButton > button[key="Link Documents"] { background-color: #6f42c1 !important; }     /* أرجواني */
    div.stButton > button[key="Backup Data"] { background-color: #17a2b8 !important; }        /* سماوي */
    div.stButton > button[key="Restore Backup"] { background-color: #ffc107 !important; }      /* أصفر */

    /* إخفاء عناصر ستريمليت الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def main_dashboard():
    st.markdown("<h2 style='text-align: center; color: white; padding: 20px;'>لوحة تحكم النظام</h2>", unsafe_allow_html=True)
    
    # الصف الأول (4 أزرار)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("Add Document", key="Add Document")
    with col2:
        st.button("Search", key="Search")
    with col3:
        st.button("Edit Document", key="Edit Document")
    with col4:
        st.button("Delete Document", key="Delete Document")

    # مسافة بسيطة بين الصفوف
    st.write("")

    # الصف الثاني (4 أزرار)
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.button("Show All Documents", key="Show All Documents")
    with col6:
        st.button("Link Documents", key="Link Documents")
    with col7:
        st.button("Backup Data", key="Backup Data")
    with col8:
        st.button("Restore Backup", key="Restore Backup")

# منطق تسجيل الدخول
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("<br><br><h2 style='text-align: center;'>تسجيل الدخول</h2>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1, 1, 1])
    with login_col:
        user = st.text_input("اسم المستخدم")
        pw = st.text_input("كلمة المرور", type="password")
        if st.button("دخول", key="login_btn"):
            if user == "admin" and pw == "1234":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("البيانات خاطئة")
else:
    main_dashboard()
