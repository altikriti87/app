import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide", initial_sidebar_state="collapsed")

# 1. دالة التحقق من تسجيل الدخول
def login():
    st.markdown("<h2 style='text-align: center;'>تسجيل الدخول للنظام</h2>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            if st.button("دخول", use_container_width=True):
                if username == "admin" and password == "1234": # يمكنك تغييرها لاحقاً
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("خطأ في البيانات، حاول مرة أخرى")

# 2. الواجهة الرئيسية (Dashboard)
def main_dashboard():
    st.markdown("<h1 style='text-align: center; color: #333;'>لوحة تحكم نظام الأرشفة</h1>", unsafe_allow_html=True)
    st.write("---")

    # تعريف البطاقات وألوانها
    cards = [
        {"name": "Add Document", "color": "#28a745", "icon": "➕"},
        {"name": "Search", "color": "#007bff", "icon": "🔍"},
        {"name": "Edit Document", "color": "#fd7e14", "icon": "📝"},
        {"name": "Delete Document", "color": "#dc3545", "icon": "🗑️"},
        {"name": "Show All Documents", "color": "#6c757d", "icon": "📋"},
        {"name": "Link Documents", "color": "#6f42c1", "icon": "🔗"},
        {"name": "Backup Data", "color": "#17a2b8", "icon": "💾"},
        {"name": "Restore Backup", "color": "#ffc107", "icon": "🔄"}
    ]

    # عرض البطاقات في شبكة (Grid)
    cols = st.columns(4)
    for index, card in enumerate(cards):
        with cols[index % 4]:
            # كود CSS لتصميم البطاقة
            card_html = f"""
            <div style="
                background-color: {card['color']};
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                color: white;
                margin-bottom: 20px;
                cursor: pointer;
                box-shadow: 2px 4px 10px rgba(0,0,0,0.1);
                transition: 0.3s;
                height: 150px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            ">
                <div style="font-size: 30px;">{card['icon']}</div>
                <div style="font-size: 18px; font-weight: bold; margin-top: 10px;">{card['name']}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"فتح {card['name']}", key=card['name'], use_container_width=True):
                st.info(f"تم الانتقال إلى صفحة: {card['name']}")

    # زر تسجيل الخروج في الجانب
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()

# 3. منطق تشغيل التطبيق
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    main_dashboard()
