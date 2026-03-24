import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام الأرشفة المحمي", layout="wide")

# --- نظام تسجيل الدخول ---
def check_password():
    """تحقق من صحة بيانات الدخول"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 تسجيل الدخول للنظام")
        with st.form("login_form"):
            user = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            submit = st.form_submit_button("دخول")
            
            if submit:
                if user == "admin" and password == "admin":
                    st.session_state.authenticated = True
                    st.rerun() # إعادة تشغيل لعرض النظام
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
        return False
    return True

# --- إذا تم تسجيل الدخول بنجاح، اعرض النظام ---
if check_password():
    # زر خروج في القائمة الجانبية
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

    # --- بداية كود نظام الأرشفة ---
    if not os.path.exists("attachments"):
        os.makedirs("attachments")

    DB_FILE = "archive_data.csv"

    def load_data():
        if os.path.exists(DB_FILE):
            return pd.read_csv(DB_FILE)
        else:
            return pd.DataFrame(columns=[
                "الرقم التسلسلي", "رقم المستند", "الجهة الواردة", 
                "الجهة المصدرة", "الموضوع", "الكلمات المفتاحية", 
                "تاريخ الأرشفة", "اسم المرفق"
            ])

    df = load_data()

    st.title("📂 نظام الأرشفة الإلكتروني - لوحة التحكم")
    st.markdown(f"**مرحباً بك: admin** | التاريخ الحالي: {datetime.now().strftime('%Y/%d/%m')}")
    st.markdown("---")

    # واجهة المدخلات
    with st.expander("➕ أرشفة مستند جديد", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            doc_number = st.text_input("رقم المستند")
            incoming_entity = st.text_input("الجهة الواردة")
            outgoing_entity = st.text_input("الجهة المصدرة")
        with col2:
            subject = st.text_input("الموضوع")
            keywords = st.text_input("الكلمات المفتاحية (مثال: فواتير، أدوية)")
            uploaded_file = st.file_uploader("ارفق المستند (PDF/Images)")

        if st.button("حفظ المستند"):
            if doc_number and subject:
                timestamp = datetime.now().strftime("%Y%d%m%H%M%S")
                serial_number = f"ARC-{timestamp}"
                
                file_name = "لا يوجد"
                if uploaded_file is not None:
                    file_name = f"{serial_number}_{uploaded_file.name}"
                    with open(os.path.join("attachments", file_name), "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                new_entry = {
                    "الرقم التسلسلي": serial_number,
                    "رقم المستند": doc_number,
                    "الجهة الواردة": incoming_entity,
                    "الجهة المصدرة": outgoing_entity,
                    "الموضوع": subject,
                    "الكلمات المفتاحية": keywords,
                    "تاريخ الأرشفة": datetime.now().strftime("%Y/%d/%m"),
                    "اسم المرفق": file_name
                }
                
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success(f"✅ تم الحفظ بنجاح! الرقم التسلسلي: {serial_number}")
                st.rerun()
            else:
                st.warning("⚠️ يرجى إدخال البيانات الأساسية")

    # البحث والعرض
    st.markdown("---")
    search_query = st.text_input("🔍 بحث سريع (بالموضوع، الرقم، أو الكلمات المفتاحية)")
    
    if search_query:
        mask = df.apply(lambda r: r.astype(str).str.contains(search_query).any(), axis=1)
        st.dataframe(df[mask], use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
