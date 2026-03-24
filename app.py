import streamlit as st

# إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide")

# تنظيف التنسيقات الافتراضية للأزرار لجعلها تبدو كبطاقات ملونة
st.markdown("""
    <style>
    div.stButton > button {
        height: 120px;
        width: 100%;
        border-radius: 15px;
        border: none;
        color: white;
        font-size: 20px;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* تأثير عند تمرير الماوس */
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        color: white;
    }
    /* ألوان مخصصة لكل زر بناءً على الترتيب */
    div.stButton > button[key="Add Document"] { background-color: #28a745; }
    div.stButton > button[key="Search"] { background-color: #007bff; }
    div.stButton > button[key="Edit Document"] { background-color: #fd7e14; }
    div.stButton > button[key="Delete Document"] { background-color: #dc3545; }
    div.stButton > button[key="Show All Documents"] { background-color: #6c757d; }
    div.stButton > button[key="Link Documents"] { background-color: #6f42c1; }
    div.stButton > button[key="Backup Data"] { background-color: #17a2b8; }
    div.stButton > button[key="Restore Backup"] { background-color: #ffc107; color: #333; }
    </style>
    """, unsafe_allow_html=True)

def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>لوحة التحكم الرئيسية</h1>", unsafe_allow_html=True)
    st.write("---")

    # تقسيم الشاشة إلى 4 أعمدة
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Add Document", key="Add Document"):
            st.success("تم الضغط على إضافة مستند")
            
    with col2:
        if st.button("Search", key="Search"):
            st.info("جاري فتح محرك البحث")

    with col3:
        if st.button("Edit Document", key="Edit Document"):
            st.warning("تم فتح التعديل")

    with col4:
        if st.button("Delete Document", key="Delete Document"):
            st.error("حذف مستند")

    # الصف الثاني
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        if st.button("Show All Documents", key="Show All Documents"):
            st.write("عرض الكل")

    with col6:
        if st.button("Link Documents", key="Link Documents"):
            st.write("ربط المستندات")

    with col7:
        if st.button("Backup Data", key="Backup Data"):
            st.write("نسخ احتياطي")

    with col8:
        if st.button("Restore Backup", key="Restore Backup"):
            st.write("استعادة النسخة")

# تشغيل النظام
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = True # مفعل مؤقتاً للتجربة

main_dashboard()
