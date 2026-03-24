import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS جبري للألوان والقياسات (استهداف مباشر للمكونات)
st.markdown("""
<style>
    /* تنسيق الحاوية لضمان الترتيب */
    [data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }

    /* التنسيق الموحد لجميع الأزرار ككروت */
    div.stButton > button {
        width: 100% !important;
        height: 140px !important;import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS لإخفاء أزرار ستريم ليت وجعلها شفافة فوق الكروت
st.markdown("""
<style>
    /* إخفاء نص وحدود أزرار ستريم ليت */
    .stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100% !important;
        height: 140px !important;
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10;
        cursor: pointer;
    }
    /* تحسين شكل الحاوية */
    [data-testid="column"] {
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# إدارة التنقل
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

# --- دالة رسم الكارت الملون ---
def draw_card(name, color):
    st.markdown(f"""
        <div style="
            background-color: {color};
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
        ">
            {name}
        </div>
    """, unsafe_allow_html=True)

# --- صفحة الإضافة ---
def add_document_page():
    st.markdown("<h2 style='text-align: center;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة", key="back"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    st.divider()
    with st.container():
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
        if st.button("حفظ البيانات", key="save", use_container_width=True):
            st.success("تم الحفظ!")

# --- لوحة التحكم الرئيسية ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>نظام الأرشفة الإلكتروني</h1>", unsafe_allow_html=True)
    st.write("---")

    # الصف الأول
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        draw_card("Add Document", "#28a745")
        if st.button("", key="btn_add"):
            st.session_state['page'] = 'add_doc'
            st.rerun()
    with c2:
        draw_card("Search", "#007bff")
        st.button("", key="btn_search")
    with c3:
        draw_card("Edit Document", "#fd7e14")
        st.button("", key="btn_edit")
    with c4:
        draw_card("Delete Document", "#dc3545")
        st.button("", key="btn_delete")

    # الصف الثاني
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        draw_card("Show All Documents", "#6c757d")
        st.button("", key="btn_show")
    with c6:
        draw_card("Link Documents", "#6f42c1")
        st.button("", key="btn_link")
    with c7:
        draw_card("Backup Data", "#17a2b8")
        st.button("", key="btn_backup")
    with c8:
        draw_card("Restore Backup", "#ffc107")
        st.button("", key="btn_restore")

# التشغيل
if st.session_state['page'] == 'dashboard':
    main_dashboard()
elif st.session_state['page'] == 'add_doc':
    add_document_page()
        border-radius: 15px !important;
        border: none !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
        margin: 0px !important;
    }

    /* تلوين الأزرار بدقة باستخدام مفتاح الـ Key */
    button[key="add"] { background: #28a745 !important; }    /* أخضر */
    button[key="search"] { background: #007bff !important; } /* أزرق */
    button[key="edit"] { background: #fd7e14 !important; }   /* برتقالي */
    button[key="delete"] { background: #dc3545 !important; } /* أحمر */
    button[key="show"] { background: #6c757d !important; }   /* رمادي */
    button[key="link"] { background: #6f42c1 !important; }   /* أرجواني */
    button[key="backup"] { background: #17a2b8 !important; } /* سماوي */
    button[key="restore"] { background: #ffc107 !important; }/* أصفر */

    /* تأثير المرور (Hover) */
    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        filter: brightness(1.1) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# إدارة التنقل بين الصفحات
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

# --- صفحة إضافة مستند ---
def add_document_page():
    st.markdown("<h2 style='text-align: center; color: #28a745;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة للوحة التحكم", key="back_btn"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    st.write("---")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار"])
            st.date_input("Enter document date", value=date.today())
            st.text_input("Enter sender")
            st.text_input("Enter receiver")
        with col2:
            st.text_input("Document subject")
            st.text_input("Keywords (comma separated)")
            st.text_input("Enter tags")
            st.text_area("Attachment description")
        
        st.file_uploader("رفع المرفقات", accept_multiple_files=True)
        if st.button("حفظ المستند المؤرشف", key="save_doc", use_container_width=True):
            st.success("✅ تم الحفظ بنجاح!")

# --- لوحة التحكم الرئيسية ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>نظام الأرشفة الإلكتروني</h1>", unsafe_allow_html=True)
    st.write("---")

    # الصف الأول - 4 أعمدة
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Add Document", key="add"):
            st.session_state['page'] = 'add_doc'
            st.rerun()
    with c2: st.button("Search", key="search")
    with c3: st.button("Edit Document", key="edit")
    with c4: st.button("Delete Document", key="delete")

    # الصف الثاني - 4 أعمدة
    c5, c6, c7, c8 = st.columns(4)
    with c5: st.button("Show All", key="show")
    with c6: st.button("Link Documents", key="link")
    with c7: st.button("Backup Data", key="backup")
    with c8: st.button("Restore Backup", key="restore")

# التشغيل النهائي
if st.session_state['page'] == 'dashboard':
    main_dashboard()
elif st.session_state['page'] == 'add_doc':
    add_document_page()
