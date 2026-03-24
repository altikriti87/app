import streamlit as st
import pandas as pd
import os
import io
import shutil
import zipfile
from datetime import datetime

# --- 1. الإعدادات العامة والتنسيق ---
st.set_page_config(page_title="EDMS - نظام الأرشفة والصلاحيات", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    .stButton>button { border-radius: 5px; font-weight: bold; }
    .user-badge { padding: 5px 15px; border-radius: 20px; background-color: #4e73df; color: white; font-size: 0.8rem; }
    .stDataFrame { background-color: white; border-radius: 8px; }
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
        "Administrator": ["view", "add", "edit", "delete", "backup_restore"],
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

# --- 4. تهيئة الملفات ---
ATTACH_DIR = "attachments"
if not os.path.exists(ATTACH_DIR): os.makedirs(ATTACH_DIR)
DB_FILE = "edms_final_db.csv"
COLUMNS = ["الرقم التسلسلي", "رقم المستند", "تاريخ الأرشفة", "الجهة الواردة", "الجهة المصدرة", "الموضوع", "الكلمات المفتاحية", "اسم المرفق"]

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=COLUMNS)

df = load_data()

# --- 5. القائمة الجانبية ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown(f"<span class='user-badge'>{st.session_state.user_role}</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu_options = ["لوحة التحكم"]
    if check_permission("add"): menu_options.append("إدخال وثيقة جديدة")
    if check_permission("backup_restore"): menu_options.append("النسخ الاحتياطي والاسترجاع")
    
    menu = st.radio("القائمة الرئيسية", menu_options)
    
    if st.button("🚪 تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. صفحة لوحة التحكم ---
if menu == "لوحة التحكم":
    st.title("📂 خزانة الملفات")
    search = st.text_input("🔍 ابحث عن أي وثيقة...")
    f_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df
    st.dataframe(f_df, use_container_width=True, hide_index=True)

    if not df.empty:
        st.markdown("---")
        selected_sn = st.selectbox("اختر وثيقة للإدارة:", ["---"] + df["الرقم التسلسلي"].tolist())
        if selected_sn != "---":
            row = df[df["الرقم التسلسلي"] == selected_sn].iloc[0]
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"📍 الموضوع: {row['الموضوع']}")
                if row['اسم المرفق'] != "لا يوجد":
                    path = os.path.join(ATTACH_DIR, row['اسم المرفق'])
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            st.download_button("📥 تحميل المرفق", f, file_name=row['اسم المرفق'])
            with c2:
                if check_permission("delete"):
                    if st.button("🗑️ حذف السجل نهائياً"):
                        df = df[df["الرقم التسلسلي"] != selected_sn]
                        df.to_csv(DB_FILE, index=False)
                        st.success("تم الحذف بنجاح"); st.rerun()

# --- 7. صفحة الإدخال ---
elif menu == "إدخال وثيقة جديدة":
    st.title("➕ أرشفة كتاب جديد")
    with st.container(border=True):
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                doc_no = st.text_input("رقم المستند")
                inc_e = st.text_input("الجهة الواردة")
            with col2:
                out_e = st.text_input("الجهة المصدرة")
                subj = st.text_input("الموضوع")
            
            uploaded_file = st.file_uploader("ارفق الوثيقة")
            if st.form_submit_button("حفظ البيانات"):
                if doc_no and subj:
                    sn = f"EDMS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    fname = f"{sn}_{uploaded_file.name}" if uploaded_file else "لا يوجد"
                    if uploaded_file:
                        with open(os.path.join(ATTACH_DIR, fname), "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    new_row = [sn, doc_no, datetime.now().strftime("%Y/%d/%m"), inc_e, out_e, subj, "", fname]
                    df.loc[len(df)] = new_row
                    df.to_csv(DB_FILE, index=False)
                    st.success(f"✅ تم الحفظ برقم: {sn}")
                    st.rerun()

# --- 8. صفحة النسخ الاحتياطي والاسترجاع (جديد) ---
elif menu == "النسخ الاحتياطي والاسترجاع":
    st.title("💾 إدارة قاعدة البيانات")
    col_back, col_rest = st.columns(2)

    with col_back:
        st.subheader("📤 إنشاء نسخة احتياطية")
        st.write("سيتم ضغط قاعدة البيانات وكافة المرفقات في ملف ZIP واحد.")
        if st.button("توليد ملف Backup"):
            b_name = f"Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            # ضغط المرفقات والـ CSV
            shutil.make_archive(b_name, 'zip', ".", ATTACH_DIR)
            with zipfile.ZipFile(f"{b_name}.zip", 'a') as z:
                if os.path.exists(DB_FILE): z.write(DB_FILE)
            
            with open(f"{b_name}.zip", "rb") as f:
                st.download_button("📥 تحميل النسخة الآن", f, file_name=f"{b_name}.zip")

    with col_rest:
        st.subheader("📥 استرجاع البيانات (Restore)")
        st.error("⚠️ تحذير: الاسترجاع سيقوم بمسح البيانات الحالية واستبدالها بالنسخة المرفوعة.")
        up_zip = st.file_uploader("ارفع ملف الـ ZIP الاحتياطي", type="zip")
        if st.button("بدء الاسترجاع"):
            if up_zip:
                with zipfile.ZipFile(up_zip, 'r') as zr:
                    # فك الضغط واستبدال الملفات
                    zr.extractall(".")
                st.success("✅ تم استرجاع البيانات والمرفقات بنجاح! يرجى تحديث الصفحة.")
                st.rerun()
            else:
                st.warning("يرجى اختيار ملف ZIP أولاً.")
