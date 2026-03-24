import streamlit as st
import pandas as pd
import os
import io
import shutil
import zipfile
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="EDMS - نظام الأرشفة المتكامل", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    .user-badge { padding: 5px 15px; border-radius: 20px; background-color: #4e73df; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة المستخدمين ---
USERS = {
    "admin": {"password": "123", "role": "Administrator"},
    "staff": {"password": "456", "role": "Editor"},
    "user": {"password": "789", "role": "Viewer"}
}

def check_permission(action):
    role = st.session_state.get("user_role", "Viewer")
    perms = {
        "Administrator": ["view", "add", "edit", "delete", "backup"],
        "Editor": ["view", "add", "edit"],
        "Viewer": ["view"]
    }
    return action in perms.get(role, [])

# --- 3. نظام تسجيل الدخول ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            st.title("🔐 تسجيل الدخول")
            u_input = st.text_input("اسم المستخدم")
            p_input = st.text_input("كلمة المرور", type="password")
            if st.button("دخول"):
                if u_input in USERS and USERS[u_input]["password"] == p_input:
                    st.session_state.authenticated = True
                    st.session_state.username = u_input
                    st.session_state.user_role = USERS[u_input]["role"]
                    st.rerun()
                else:
                    st.error("❌ بيانات خاطئة")
    st.stop()

# --- 4. تهيئة الملفات وقاعدة البيانات ---
ATTACH_DIR = "attachments"
if not os.path.exists(ATTACH_DIR): os.makedirs(ATTACH_DIR)
DB_FILE = "edms_final_db.csv"
COLUMNS = ["الرقم التسلسلي", "رقم المستند", "تاريخ الأرشفة", "الجهة الواردة", "الجهة المصدرة", "الموضوع", "الكلمات المفتاحية", "اسم المرفق"]

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=COLUMNS)

# استخدام مفتاح فريد لكل عملية إدخال لضمان تصفير الحقول
if "submission_id" not in st.session_state:
    st.session_state.submission_id = 0

df = load_data()

# --- 5. القائمة الجانبية ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown(f"<span class='user-badge'>{st.session_state.user_role}</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu_options = ["لوحة التحكم"]
    if check_permission("add"): menu_options.append("إدخال وثيقة جديدة")
    if check_permission("backup"): menu_options.append("النسخ الاحتياطي")
    
    menu = st.radio("القائمة", menu_options)
    
    if st.button("🚪 خروج"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. صفحة لوحة التحكم (البحث والإدارة) ---
if menu == "لوحة التحكم":
    st.title("📂 خزانة الملفات")
    search = st.text_input("🔍 ابحث هنا...")
    f_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df
    st.dataframe(f_df, use_container_width=True, hide_index=True)

    if not df.empty and check_permission("view"):
        st.markdown("---")
        selected_sn = st.selectbox("اختر رقم الوثيقة للإدارة:", ["---"] + df["الرقم التسلسلي"].tolist())
        if selected_sn != "---":
            row = df[df["الرقم التسلسلي"] == selected_sn].iloc[0]
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"الموضوع: {row['الموضوع']}")
                if row['اسم المرفق'] != "لا يوجد":
                    path = os.path.join(ATTACH_DIR, row['اسم المرفق'])
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            st.download_button("📥 تحميل الملف", f, file_name=row['اسم المرفق'])
            with c2:
                if check_permission("delete"):
                    if st.button("🗑️ حذف السجل"):
                        df = df[df["الرقم التسلسلي"] != selected_sn]
                        df.to_csv(DB_FILE, index=False)
                        st.success("تم الحذف"); st.rerun()

# --- 7. صفحة الإدخال (تم إصلاح مشكلة عدم الإدخال) ---
elif menu == "إدخال وثيقة جديدة":
    st.title("➕ أرشفة كتاب جديد")
    
    # استخدام حاوية لضمان استقرار النموذج
    with st.container(border=True):
        # مفتاح فريد لضمان تصفير الحقول بعد كل عملية حفظ ناجحة
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                doc_no = st.text_input("رقم المستند الورقي")
                inc_e = st.text_input("الجهة الواردة")
            with col2:
                out_e = st.text_input("الجهة المصدرة")
                subj = st.text_input("الموضوع")
            
            keyw = st.text_area("الكلمات المفتاحية")
            uploaded_file = st.file_uploader("ارفق ملف الوثيقة")
            
            submit_btn = st.form_submit_button("إتمام الحفظ في الأرشيف")
            
            if submit_btn:
                if doc_no and subj:
                    try:
                        # توليد رقم تسلسلي
                        sn = f"EDMS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        fname = "لا يوجد"
                        
                        # معالجة الملف
                        if uploaded_file:
                            fname = f"{sn}_{uploaded_file.name}"
                            with open(os.path.join(ATTACH_DIR, fname), "wb") as f:
                                f.write(uploaded_file.getbuffer())
                        
                        # إضافة البيانات
                        new_data = [sn, doc_no, datetime.now().strftime("%Y/%d/%m"), inc_e, out_e, subj, keyw, fname]
                        df.loc[len(df)] = new_data
                        df.to_csv(DB_FILE, index=False)
                        
                        st.success(f"✅ تم حفظ الوثيقة بنجاح! رقم القيد: {sn}")
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")
                else:
                    st.warning("⚠️ يرجى ملء رقم المستند والموضوع على الأقل.")

# --- 8. صفحة النسخ الاحتياطي ---
elif menu == "النسخ الاحتياطي":
    st.title("💾 الإدارة")
    if st.button("إنشاء نسخة احتياطية"):
        shutil.make_archive("full_backup", 'zip', ".", ATTACH_DIR)
        with open("full_backup.zip", "rb") as f:
            st.download_button("📥 تحميل النسخة", f, file_name="backup.zip")
