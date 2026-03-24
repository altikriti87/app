import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام الأرشفة المحمي", layout="wide")

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
    # إنشاء المجلدات وقاعدة البيانات
    if not os.path.exists("attachments"): os.makedirs("attachments")
    DB_FILE = "archive_data.csv"

    def load_data():
        if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
        return pd.DataFrame(columns=["الرقم التسلسلي", "رقم المستند", "الجهة الواردة", "الجهة المصدرة", "الموضوع", "الكلمات المفتاحية", "تاريخ الأرشفة", "اسم المرفق"])

    # --- الحل لمشكلة تفريغ الحقول ---
    # نستخدم "عداد" لتغيير مفاتيح الحقول عند كل عملية حفظ ناجحة
    if "form_count" not in st.session_state:
        st.session_state.form_count = 0

    st.title("📂 نظام الأرشفة الإلكتروني")
    st.markdown(f"**التاريخ:** {datetime.now().strftime('%Y/%d/%m')}")

    # واجهة المدخلات - المفاتيح تتغير مع كل حفظ (تفريغ تلقائي)
    with st.expander("➕ أرشفة مستند جديد", expanded=True):
        count = st.session_state.form_count
        col1, col2 = st.columns(2)
        
        with col1:
            doc_number = st.text_input("رقم المستند", key=f"doc_{count}")
            incoming_entity = st.text_input("الجهة الواردة", key=f"inc_{count}")
            outgoing_entity = st.text_input("الجهة المصدرة", key=f"out_{count}")
        with col2:
            subject = st.text_input("الموضوع", key=f"sub_{count}")
            keywords = st.text_input("الكلمات المفتاحية", key=f"key_{count}")
            uploaded_file = st.file_uploader("ارفق المستند (PDF/Images)", key=f"file_{count}")

        if st.button("حفظ المستند وإفراغ الحقول"):
            if doc_number and subject:
                # توليد الرقم التسلسلي
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                serial_number = f"ARC-{timestamp}"
                
                # حفظ الملف
                file_name = "لا يوجد"
                if uploaded_file is not None:
                    file_name = f"{serial_number}_{uploaded_file.name}"
                    with open(os.path.join("attachments", file_name), "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # إضافة البيانات للـ DataFrame
                df = load_data()
                new_entry = {
                    "الرقم التسلسلي": serial_number, "رقم المستند": doc_number,
                    "الجهة الواردة": incoming_entity, "الجهة المصدرة": outgoing_entity,
                    "الموضوع": subject, "الكلمات المفتاحية": keywords,
                    "تاريخ الأرشفة": datetime.now().strftime("%Y/%d/%m"),
                    "اسم المرفق": file_name
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                
                st.success(f"✅ تم الحفظ بنجاح بالرقم: {serial_number}")
                
                # --- السحر هنا ---
                # بزيادة العداد، ستتغير الـ keys في الإعادة القادمة فيظهر النموذج فارغاً تماماً
                st.session_state.form_count += 1
                st.rerun()
            else:
                st.warning("⚠️ يرجى إدخال رقم المستند والموضوع")

    # عرض البيانات
    st.markdown("---")
    df_view = load_data()
    search_query = st.text_input("🔍 بحث في الأرشيف")
    if search_query:
        mask = df_view.apply(lambda r: r.astype(str).str.contains(search_query).any(), axis=1)
        st.dataframe(df_view[mask], use_container_width=True)
    else:
        st.dataframe(df_view, use_container_width=True)
