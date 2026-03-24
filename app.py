import streamlit as st

# إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

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

# 2. الواجهة الرئيسية
def main_dashboard():
    st.markdown("<h1 style='text-align: center; color: #333;'>لوحة تحكم نظام الأرشفة</h1>", unsafe_allow_html=True)
    st.write("---")

    # قائمة البطاقات مع الألوان المحددة
    cards = [
        {"name": "Add Document", "color": "#28a745"},      # أخضر
        {"name": "Search", "color": "#007bff"},            # أزرق
        {"name": "Edit Document", "color": "#fd7e14"},      # برتقالي
        {"name": "Delete Document", "color": "#dc3545"},    # أحمر
        {"name": "Show All Documents", "color": "#6c757d"}, # رمادي
        {"name": "Link Documents", "color": "#6f42c1"},     # أرجواني
        {"name": "Backup Data", "color": "#17a2b8"},        # سماوي
        {"name": "Restore Backup", "color": "#ffc107"}      # أصفر
    ]

    # عرض البطاقات في شبكة
    cols = st.columns(4)
    for index, card in enumerate(cards):
        with cols[index % 4]:
            # تصميم البطاقة بدون أزرار "فتح"
            card_design = f"""
            <div style="
                background-color: {card['color']};
                padding: 40px 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                margin-bottom: 20px;
                font-size: 20px;
                font-weight: bold;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                border: none;
            ">
                {card['name']}
            </div>
            """
            st.markdown(card_design, unsafe_allow_html=True)

# منطق التشغيل
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    main_dashboard()
