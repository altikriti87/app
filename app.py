import streamlit as st

# إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# تصميم CSS مخصص لجعل الأزرار مطابقة للصور التي أرفقتها من حيث الألوان والترتيب
st.markdown("""
    <style>
    /* تنسيق الأزرار لتصبح بطاقات ملونة */
    div.stButton > button {
        height: 100px;
        width: 100%;
        border-radius: 10px;
        border: none;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        transition: 0.3s;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 10px;
    }

    /* تأثير تمرير الماوس */
    div.stButton > button:hover {
        transform: scale(1.02);
        opacity: 0.9;
    }

    /* الألوان المخصصة لكل بطاقة بناءً على الترتيب في صورك */
    /* الصف الأول */
    div.stButton > button[key="Add Document"] { background-color: #28a745 !important; }      /* أخضر */
    div.stButton > button[key="Search"] { background-color: #007bff !important; }            /* أزرق */
    div.stButton > button[key="Edit Document"] { background-color: #fd7e14 !important; }      /* برتقالي */
    div.stButton > button[key="Delete Document"] { background-color: #dc3545 !important; }    /* أحمر */
    
    /* الصف الثاني */
    div.stButton > button[key="Link Documents"] { background-color: #6f42c1 !important; }     /* أرجواني */
    div.stButton > button[key="Backup Data"] { background-color: #17a2b8 !important; }        /* سماوي */
    div.stButton > button[key="Restore Backup"] { background-color: #ffc107 !important; color: #333 !important; } /* أصفر */
    
    /* الصف الثالث */
    div.stButton > button[key="Show All Documents"] { background-color: #6c757d !important; } /* رمادي */

    /* تنسيق العنوان */
    .main-title {
        text-align: center;
        color: #333;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

def main_dashboard():
    st.markdown("<h1 class='main-title'>نظام الأرشفة الإلكتروني</h1>", unsafe_allow_html=True)
    
    # --- الصف الأول (4 بطاقات) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("Add Document", key="Add Document")
    with col2:
        st.button("Search", key="Search")
    with col3:
        st.button("Edit Document", key="Edit Document")
    with col4:
        st.button("Delete Document", key="Delete Document")

    st.write("") # مسافة بسيطة بين الصفوف

    # --- الصف الثاني (3 بطاقات) ---
    # نستخدم توزيع [1, 1, 1] لتوسيطهم أو جعلهم متساوين
    col5, col6, col7 = st.columns(3)
    with col5:
        st.button("Link Documents", key="Link Documents")
    with col6:
        st.button("Backup Data", key="Backup Data")
    with col7:
        st.button("Restore Backup", key="Restore Backup")

    st.write("") # مسافة بسيطة

    # --- الصف الثالث (بطاقة واحدة كبيرة في المنتصف) ---
    # نستخدم تقسيم أعمدة لجعل البطاقة الأخيرة في المنتصف تماماً كما في الصورة
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.button("Show All Documents", key="Show All Documents")

# التحقق من حالة الدخول
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    # واجهة تسجيل دخول بسيطة
    st.markdown("<h2 style='text-align: center;'>تسجيل الدخول</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        user = st.text_input("اسم المستخدم")
        passw = st.text_input("كلمة المرور", type="password")
        if st.button("دخول", key="login"):
            if user == "admin" and passw == "1234":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("البيانات غير صحيحة")
else:
    main_dashboard()
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['auth'] = False
        st.rerun()
