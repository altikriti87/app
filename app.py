import streamlit as st

# إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# كود CSS القوي لإجبار الأزرار على أخذ شكل البطاقات الملونة بالكامل
st.markdown("""
    <style>
    /* تنسيق الحاوية الأساسية */
    .stApp {
        background-color: #0e1117; /* لون خلفية داكن ليتناسب مع الصورة */
    }

    /* تنسيق الزر ليصبح بطاقة ملونة عريضة */
    div.stButton > button {
        height: 120px !important;
        width: 100% !important;
        border-radius: 12px !important;
        border: none !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
        transition: 0.3s !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        margin-bottom: 10px !important;
    }

    /* تأثير عند تمرير الماوس */
    div.stButton > button:hover {
        transform: scale(1.02) !important;
        opacity: 0.9 !important;
    }

    /* فرض الألوان بناءً على المفتاح الخاص بكل زر (Key) */
    
    /* الصف الأول */
    div.stButton > button[key="Add Document"] { background-color: #28a745 !important; }      /* أخضر */
    div.stButton > button[key="Search"] { background-color: #007bff !important; }            /* أزرق */
    div.stButton > button[key="Edit Document"] { background-color: #fd7e14 !important; }      /* برتقالي */
    div.stButton > button[key="Delete Document"] { background-color: #dc3545 !important; }    /* أحمر */
    
    /* الصف الثاني */
    div.stButton > button[key="Show All Documents"] { background-color: #6c757d !important; } /* رمادي */
    div.stButton > button[key="Link Documents"] { background-color: #6f42c1 !important; }     /* أرجواني */
    div.stButton > button[key="Backup Data"] { background-color: #17a2b8 !important; }        /* سماوي */
    div.stButton > button[key="Restore Backup"] { background-color: #ffc107 !important; color: #212529 !important; } /* أصفر مع نص داكن وضوح */

    /* إخفاء القوائم العلوية */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def main():
    st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 30px;'>نظام الأرشفة الإلكتروني</h2>", unsafe_allow_html=True)
    
    # بناء الشبكة (Grid) كما في الصورة المطلوبة تماماً
    
    # الصف الأول (4 بطاقات ملونة)
    row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
    with row1_col1:
        st.button("Add Document", key="Add Document")
    with row1_col2:
        st.button("Search", key="Search")
    with row1_col3:
        st.button("Edit Document", key="Edit Document")
    with row1_col4:
        st.button("Delete Document", key="Delete Document")

    st.markdown("<br>", unsafe_allow_html=True) # مسافة بين الصفوف

    # الصف الثاني (4 بطاقات ملونة)
    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
    with row2_col1:
        st.button("Show All Documents", key="Show All Documents")
    with row2_col2:
        st.button("Link Documents", key="Link Documents")
    with row2_col3:
        st.button("Backup Data", key="Backup Data")
    with row2_col4:
        st.button("Restore Backup", key="Restore Backup")

if __name__ == "__main__":
    main()
