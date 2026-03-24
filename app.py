import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS مخصص للتحكم في الألوان والقياسات وجعل الكارت قابلاً للضغط
st.markdown("""
<style>
    /* حاوية الكارت */
    .card-container {
        position: relative;
        height: 140px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }

    /* جعل زر Streamlit يغطي الكارت تماماً ويصبح شفافاً */
    .stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 140px; /* نفس قياس الكارت */
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 10;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* تأثير عند تمرير الماوس على الحاوية */
    .card-container:hover {
        transform: translateY(-5px);
        filter: brightness(1.1);
    }
</style>
""", unsafe_allow_html=True)

# إدارة حالة الصفحة
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- صفحة إضافة مستند ---
def add_document_page():
    st.markdown("<h2 style='text-align: center;'>إضافة مستند جديد</h2>", unsafe_allow_html=True)
    if st.button("⬅️ العودة للوحة التحكم", key="back"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    st.write("---")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Document Type", ["كتاب رسمي", "تقرير", "عقد", "أخرى"])
            st.date_input("Enter document date", value=date.today())
            st.text_input("Enter sender")
            st.text_input("Enter receiver")
        with col2:
            st.text_input("Document subject")
            st.text_input("Keywords (comma separated)")
            st.text_input("Enter tags (tag1, tag2)")
            st.text_area("Attachment description")
        
        st.file_uploader("رفع المرفقات", accept_multiple_files=True)
        if st.button("حفظ البيانات", use_container_width=True, type="primary"):
            st.success("تم الحفظ بنجاح!")

# --- لوحة التحكم ---
def main_dashboard():
    st.markdown("<h1 style='text-align: center; color: #333;'>لوحة تحكم نظام الأرشفة</h1>", unsafe_allow_html=True)
    st.write("---")

    # قائمة البيانات (الألوان والأسماء والترتيب)
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

    # عرض البطاقات في شبكة 4x2
    cols = st.columns(4)
    for index, card in enumerate(cards):
        with cols[index % 4]:
            # إنشاء الكارت الملون (HTML) والزر الشفاف (Streamlit) في نفس المكان
            st.markdown(f"""
                <div class="card-container" style="background-color: {card['color']};">
                    {card['name']}
                </div>
            """, unsafe_allow_html=True)
            
            # الزر يوضع برمجياً بعد الـ HTML مباشرة ويتم رفعه فوقه بواسطة CSS
            if st.button("", key=f"btn_{card['id']}"):
                if card['id'] == "add":
                    st.session_state['page'] = 'add_doc'
                    st.rerun()
                else:
                    st.toast(f"تم النقر على {card['name']}")

# --- التشغيل ---
if not st.session_state['logged_in']:
    st.title("تسجيل الدخول")
    if st.button("دخول للنظام (Admin)"):
        st.session_state['logged_in'] = True
        st.rerun()
else:
    if st.session_state['page'] == 'dashboard':
        main_dashboard()
    elif st.session_state['page'] == 'add_doc':
        add_document_page()
