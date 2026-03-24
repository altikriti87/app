import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام الأرشفة المحمي", layout="wide")

# --- دالة لتفريغ الحقول ---
def reset_form():
    st.session_state["doc_number"] = ""
    st.session_state["incoming_entity"] = ""
    st.session_state["outgoing_entity"] = ""
    st.session_state["subject"] = ""
    st.session_state["keywords"] = ""
    # ملاحظة: حقل رفع الملفات لا يمكن تفريغه برمجياً بسهولة في Streamlit حالياً، 
    # لكن سيتم تجاهله في عملية الحفظ القادمة.

# --- نظام تسجيل الدخول ---
def check_password():
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
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
        return False
    return True

if check_password():
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

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

    st.title("📂 نظام الأرشفة الإلكتروني")
    st.markdown(f"**التاريخ:** {datetime.now().strftime('%Y/%d/%m')}")
    st.markdown("---")

    # واجهة المدخلات مع استخدام session_state للتفريغ
    with st.expander("➕ أرشفة مستند جديد", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            doc_number = st.text_input("رقم المستند", key="doc_number")
            incoming_entity = st.text_input("الجهة الواردة", key="incoming_entity")
            outgoing_entity = st.text_input("الجهة المصدرة", key="outgoing_entity")
        with col2:
            subject = st.text_input("الموضوع", key="subject")
            keywords = st.text_input("الكلمات المفتاحية", key="keywords")
            uploaded_file = st.file_uploader("ارفق المستند (PDF/Images)")

        if st.button("حفظ المستند وإفراغ الحقول"):
            if doc_number and subject:
                # توليد الرقم التسلسلي
                timestamp = datetime.now().strftime("%Y%d%m%H%M%S")
                serial_number = f"ARC-{timestamp}"
                
                # حفظ الملف
                file_name = "لا يوجد"
                if uploaded_file is not None:
                    file_name = f"{serial_number}_{uploaded_file.name}"
                    with open(os.path.join("attachments", file_name), "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # إضافة البيانات
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
                
                st.success(f"✅ تم الحفظ بنجاح بالرقم: {serial_number}")
                
                # تنفيذ دالة تفريغ الحقول
                reset_form()
                # إعادة تشغيل التطبيق لتحديث الواجهة بالحقول الفارغة
                st.rerun()
            else:
                st.warning("⚠️ يرجى إدخال رقم المستند والموضوع على الأقل")

    # قسم البحث والعرض
    st.markdown("---")
    search_query = st.text_input("🔍 بحث في الأرشيف")
    if search_query:
        mask = df.apply(lambda r: r.astype(str).str.contains(search_query).any(), axis=1)
        st.dataframe(df[mask], use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
