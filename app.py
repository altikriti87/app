import streamlit as st
import pandas as pd
import os
import io
import shutil
import zipfile
from datetime import datetime

# --- 1. إعدادات الهوية البصرية (CSS) ---
st.set_page_config(
    page_title="نظام الأرشفة الإلكتروني - EDMS",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    [data-testid="stHeader"] { background-color: #ffffff; border-bottom: 3px solid #4e73df; }
    .stButton>button { border-radius: 5px; font-weight: bold; }
    .data-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-right: 6px solid #4e73df;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .user-badge {
        padding: 4px 12px;
        border-radius: 15px;
        background-color: #4e73df;
        color: white;
        font-size: 0.8rem;
    }
    .stDataFrame { background-color: white; border-radius: 8px; border: 1px solid #e3e6f0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة المستخدمين والصلاحيات ---
# الأدوار: Administrator (كامل)، Editor (إضافة/تعديل)، Viewer (عرض فقط)
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
        st.write("")
        with st.container(border=True):
            st.title("🔐 دخول النظام")
            u_input = st.text_input("اسم المستخدم")
            p_input = st.text_input("كلمة المرور", type="password")
            if st.button("تسجيل الدخول"):
                if u_input in USERS and USERS[u_input]["password"] == p_input:
                    st.session_state.authenticated = True
                    st.session_state.username = u_input
                    st.session_state.user_role = USERS[u_input]["role"]
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
    st.stop()

# --- 4. تهيئة قاعدة البيانات والملفات ---
ATTACH_DIR = "attachments"
if not os.path.exists(ATTACH_DIR): os.makedirs(ATTACH_DIR)
DB_FILE = "edms_professional_db.csv"
COLUMNS = ["الرقم التسلسلي", "رقم المستند", "تاريخ الأرشفة", "الجهة الواردة", "الجهة المصدرة", "الموضوع", "الكلمات المفتاحية", "اسم المرفق"]

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=COLUMNS)

if "form_count" not in st.session_state: st.session_state.form_count = 0
df = load_data()

# --- 5. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown(f"<span class='user-badge'>{st.session_state.user_role}</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu_options = ["لوحة التحكم (البحث والعرض)"]
    if check_permission("add"): menu_options.append("إدخال وثيقة جديدة")
    if check_permission("backup"): menu_options.append("إدارة النسخ الاحتياطي")
    
    menu = st.radio("القائمة الرئيسية", menu_options)
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. صفحة لوحة التحكم (الخزانة) ---
if menu == "لوحة التحكم (البحث والعرض)":
    st.title("📂 خزانة ملفات الصادر والوارد")
    
    # البحث المتقدم
    search = st.text_input("🔍 ابحث في الأرشيف (بالموضوع، الرقم، أو الجهة)...")
    f_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df
    
    st.dataframe(f_df, use_container_width=True, hide_index=True)

    if not df.empty:
        st.markdown("---")
        st.subheader("🛠️ إدارة المستند المختار")
        selected_sn = st.selectbox("حدد الرقم التسلسلي للمستند:", ["---"] + df["الرقم التسلسلي"].tolist())
        
        if selected_sn != "---":
            row = df[df["الرقم التسلسلي"] == selected_sn].iloc[0]
            c_info, c_actions = st.columns([1.5, 1])

            with c_info:
                st.markdown(f"""<div class="data-card"><h4>📋 تفاصيل القيد</h4>
                <b>رقم التسجيل:</b> {selected_sn}<br>
                <b>رقم الكتاب:</b> {row['رقم المستند']}<br>
                <b>الموضوع:</b> {row['الموضوع']}<br>
                <b>تاريخ الأرشفة:</b> {row['تاريخ الأرشفة']}</div>""", unsafe_allow_html=True)

            with c_actions:
                # 1. تحميل المرفق
                if row['اسم المرفق'] != "لا يوجد":
                    path = os.path.join(ATTACH_DIR, row['اسم المرفق'])
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            st.download_button("📥 فتح/تحميل المرفق", f, file_name=row['اسم المرفق'])
                
                # 2. التعديل (Editor/Admin)
                if check_permission("edit"):
                    with st.expander("✏️ تعديل البيانات"):
                        with st.form("edit_f"):
                            e_doc = st.text_input("رقم المستند", row['رقم المستند'])
                            e_sub = st.text_input("الموضوع", row['الموضوع'])
                            e_inc = st.text_input("الجهة الواردة", row['الجهة الواردة'])
                            e_out = st.text_input("الجهة المصدرة", row['الجهة المصدرة'])
                            if st.form_submit_button("تحديث السجل"):
                                df.loc[df["الرقم التسلسلي"] == selected_sn, ["رقم المستند", "الموضوع", "الجهة الواردة", "الجهة المصدرة"]] = [e_doc, e_sub, e_inc, e_out]
                                df.to_csv(DB_FILE, index=False)
                                st.success("✅ تم التحديث"); st.rerun()
                
                # 3. الحذف (Administrator فقط)
                if check_permission("delete"):
                    if st.button("🗑️ حذف نهائي من النظام"):
                        df = df[df["الرقم التسلسلي"] != selected_sn]
                        df.to_csv(DB_FILE, index=False)
                        st.warning("تم حذف السجل!"); st.rerun()

# --- 7. صفحة إدخال وثيقة جديدة ---
elif menu == "إدخال وثيقة جديدة":
    st.title("➕ أرشفة وثيقة جديدة")
    fc = st.session_state.form_count
    with st.container(border=True):
        with st.form("add_doc_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                n_doc = st.text_input("رقم المستند (الرقم المكتوب)", key=f"nd_{fc}")
                n_inc = st.text_input("الجهة الواردة (Incoming)", key=f"ni_{fc}")
                n_sub = st.text_input("الموضوع", key=f"ns_{fc}")
            with col_b:
                n_out = st.text_input("الجهة المصدرة (Outgoing)", key=f"no_{fc}")
                n_key = st.text_input("الكلمات المفتاحية", key=f"nk_{fc}")
                n_file = st.file_uploader("رفع المرفق (PDF/Image)", key=f"nf_{fc}")
            
            if st.form_submit_button("حفظ الأرشفة"):
                if n_doc and n_sub:
                    sn = f"EDMS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    fname = f"{sn}_{n_file.name}" if n_file else "لا يوجد"
                    if n_file:
                        with open(os.path.join(ATTACH_DIR, fname), "wb") as f: f.write(n_file.getbuffer())
                    
                    new_row = [sn, n_doc, datetime.now().strftime("%Y/%d/%m"), n_inc, n_out, n_sub, n_key, fname]
                    df.loc[len(df)] = new_row
                    df.to_csv(DB_FILE, index=False)
                    st.success(f"✅ تمت الأرشفة بنجاح! رقم القيد: {sn}")
                    st.session_state.form_count += 1
                    st.rerun()
                else:
                    st.error("⚠️ يرجى تعبئة الحقول الأساسية")

# --- 8. صفحة النسخ الاحتياطي (Admin) ---
elif menu == "إدارة النسخ الاحتياطي":
    st.title("💾 إدارة قاعدة البيانات")
    if check_permission("backup"):
        c_export, c_import = st.columns(2)
        with c_export:
            st.subheader("📤 تصدير نسخة احتياطية")
            if st.button("توليد ملف Backup (.zip)"):
                b_name = f"Backup_EDMS_{datetime.now().strftime('%Y%m%d')}"
                shutil.make_archive(b_name, 'zip', ".", ATTACH_DIR)
                with zipfile.ZipFile(f"{b_name}.zip", 'a') as z:
                    if os.path.exists(DB_FILE): z.write(DB_FILE)
                with open(f"{b_name}.zip", "rb") as f:
                    st.download_button("📥 تحميل النسخة الآن", f, file_name=f"{b_name}.zip")
        
        with c_import:
            st.subheader("📥 استرجاع من نسخة")
            up_zip = st.file_uploader("ارفع ملف الـ ZIP الاحتياطي", type="zip")
            if st.button("تأكيد الاسترجاع"):
                if up_zip:
                    with zipfile.ZipFile(up_zip, 'r') as zr: zr.extractall(".")
                    st.success("✅ تم الاسترجاع! يرجى تحديث الصفحة."); st.rerun()
    else:
        st.error("🔒 عذراً، الوصول لهذه الصفحة للمسؤول فقط.")
