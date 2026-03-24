import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام الأرشفة المطور", layout="wide")

# --- نظام تسجيل الدخول ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 تسجيل الدخول للنظام")
        with st.form("login_form"):
            user = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول"):
                if user == "admin" and password == "admin":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
        return False
    return True

if check_password():
    # إنشاء المجلدات وقاعدة البيانات
    ATTACH_DIR = "attachments"
    if not os.path.exists(ATTACH_DIR): os.makedirs(ATTACH_DIR)
    DB_FILE = "archive_data.csv"

    def load_data():
        if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
        return pd.DataFrame(columns=["الرقم التسلسلي", "رقم المستند", "الجهة الواردة", "الجهة المصدرة", "الموضوع", "الكلمات المفتاحية", "تاريخ الأرشفة", "اسم المرفق"])

    if "form_count" not in st.session_state: st.session_state.form_count = 0

    st.title("📂 نظام الأرشفة الإلكتروني الشامل")
    st.sidebar.button("تسجيل الخروج", on_click=lambda: st.session_state.update({"authenticated": False}))

    # --- القسم 1: إضافة مستند جديد ---
    with st.expander("➕ أرشفة مستند جديد", expanded=False):
        c = st.session_state.form_count
        col1, col2 = st.columns(2)
        with col1:
            doc_no = st.text_input("رقم المستند", key=f"d_{c}")
            inc_e = st.text_input("الجهة الواردة", key=f"i_{c}")
            out_e = st.text_input("الجهة المصدرة", key=f"o_{c}")
        with col2:
            subj = st.text_input("الموضوع", key=f"s_{c}")
            keyw = st.text_input("الكلمات المفتاحية", key=f"k_{c}")
            file = st.file_uploader("المرفق", key=f"f_{c}")

        if st.button("حفظ المستند الجديد"):
            if doc_no and subj:
                sn = f"ARC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                fname = "لا يوجد"
                if file:
                    fname = f"{sn}_{file.name}"
                    with open(os.path.join(ATTACH_DIR, fname), "wb") as f: f.write(file.getbuffer())
                
                df = load_data()
                new_row = [sn, doc_no, inc_e, out_e, subj, keyw, datetime.now().strftime("%Y/%d/%m"), fname]
                df.loc[len(df)] = new_row
                df.to_csv(DB_FILE, index=False)
                st.success("✅ تم الحفظ!"); st.session_state.form_count += 1; st.rerun()

    # --- القسم 2: البحث والعرض ---
    st.markdown("---")
    df = load_data()
    search = st.text_input("🔍 ابحث هنا (بالموضوع أو الرقم أو الكلمات)...")
    filtered_df = df[df.apply(lambda r: r.astype(str).str.contains(search).any(), axis=1)] if search else df
    st.dataframe(filtered_df, use_container_width=True)

    # --- القسم 3: إدارة الوثيقة (تعديل / حذف / عرض) ---
    st.subheader("🛠️ إدارة وثيقة محددة")
    if not df.empty:
        selected_sn = st.selectbox("اختر الرقم التسلسلي للوثيقة للتحكم بها:", ["---"] + df["الرقم التسلسلي"].tolist())
        
        if selected_sn != "---":
            row = df[df["الرقم التسلسلي"] == selected_sn].iloc[0]
            col_a, col_b = st.columns([1, 2])

            with col_a:
                st.info(f"📄 بيانات: {selected_sn}")
                # زر عرض المرفق
                if row['اسم المرفق'] != "لا يوجد":
                    file_path = os.path.join(ATTACH_DIR, row['اسم المرفق'])
                    with open(file_path, "rb") as f:
                        st.download_button("📥 تحميل/عرض المرفق", f, file_name=row['اسم المرفق'])
                
                # زر الحذف
                if st.button("🗑️ حذف هذه الوثيقة نهائياً"):
                    df = df[df["الرقم التسلسلي"] != selected_sn]
                    df.to_csv(DB_FILE, index=False)
                    if row['اسم المرفق'] != "لا يوجد":
                        try: os.remove(os.path.join(ATTACH_DIR, row['اسم المرفق']))
                        except: pass
                    st.warning("تم الحذف!"); st.rerun()

            with col_b:
                with st.form("edit_form"):
                    st.write("✏️ تعديل البيانات:")
                    new_doc_no = st.text_input("رقم المستند", value=row['رقم المستند'])
                    new_subj = st.text_input("الموضوع", value=row['الموضوع'])
                    new_inc = st.text_input("الجهة الواردة", value=row['الجهة الواردة'])
                    new_out = st.text_input("الجهة المصدرة", value=row['الجهة المصدرة'])
                    new_keys = st.text_input("الكلمات المفتاحية", value=row['الكلمات المفتاحية'])
                    
                    if st.form_submit_button("تحديث البيانات"):
                        df.loc[df["الرقم التسلسلي"] == selected_sn, ["رقم المستند", "الموضوع", "الجهة الواردة", "الجهة المصدرة", "الكلمات المفتاحية"]] = [new_doc_no, new_subj, new_inc, new_out, new_keys]
                        df.to_csv(DB_FILE, index=False)
                        st.success("✅ تم التحديث!"); st.rerun()
    else:
        st.write("الأرشيف فارغ حالياً.")
