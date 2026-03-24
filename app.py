import streamlit as st
import pandas as pd
import os
import io
import shutil
import zipfile
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="EDMS - نظام إدارة الصلاحيات", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    [data-testid="stHeader"] { border-bottom: 3px solid #4e73df; }
    .stButton>button { border-radius: 5px; font-weight: bold; }
    .user-tag { padding: 5px 10px; border-radius: 15px; background: #4e73df; color: white; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تعريف المستخدمين وصلاحياتهم ---
# ملاحظة: في الأنظمة الضخمة تُخزن هذه في قاعدة بيانات مشفرة
USERS = {
    "admin": {"password": "123", "role": "Administrator"},
    "staff": {"password": "456", "role": "Editor"},
    "viewer": {"password": "789", "role": "Viewer"}
}

# دالة للتحقق من الصلاحية
def can_action(action):
    role = st.session_state.user_role
    permissions = {
        "Administrator": ["view", "add", "edit", "delete", "backup"],
        "Editor": ["view", "add", "edit"],
        "Viewer": ["view"]
    }
    return action in permissions.get(role, [])

# --- 3. نظام تسجيل الدخول ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            st.title("🔐 تسجيل الدخول")
            user_input = st.text_input("اسم المستخدم")
            pw_input = st.text_input("كلمة المرور", type="password")
            if st.button("دخول"):
                if user_input in USERS and USERS[user_input]["password"] == pw_input:
                    st.session_state.authenticated = True
                    st.session_state.username = user_input
                    st.session_state.user_role = USERS[user_input]["role"]
                    st.rerun()
                else:
                    st.error("❌ بيانات غير صحيحة")
    st.stop()

# --- 4. تهيئة البيانات ---
ATTACH_DIR = "attachments"
if not os.path.exists(ATTACH_DIR): os.makedirs(ATTACH_DIR)
DB_FILE = "edms_secure_db.csv"
COLUMNS = ["الرقم التسلسلي", "رقم المستند", "تاريخ الأرشفة", "الجهة الواردة", "الجهة المصدرة", "الموضوع", "الكلمات المفتاحية", "اسم المرفق"]

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=COLUMNS)

df = load_data()

# --- 5. القائمة الجانبية وحالة المستخدم ---
with st.sidebar:
    st.markdown(f"👤 المستخدم: **{st.session_state.username}**")
    st.markdown(f"<span class='user-tag'>{st.session_state.user_role}</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    options = ["لوحة التحكم"]
    if can_action("add"): options.append("إضافة وثيقة")
    if can_action("backup"): options.append("النظام والنسخ الاحتياطي")
    
    menu = st.radio("القائمة الرئيسية", options)
    
    if st.button("🚪 خروج"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. صفحة لوحة التحكم (عرض وبحث) ---
if menu == "لوحة التحكم":
    st.title("📂 خزانة الملفات")
    
    search = st.text_input("🔎 ابحث في الأرشيف...")
    filtered_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    if not df.empty:
        selected_sn = st.selectbox("اختر وثيقة للإدارة:", ["---"] + df["الرقم التسلسلي"].tolist())
        if selected_sn != "---":
            row = df[df["الرقم التسلسلي"] == selected_sn].iloc[0]
            col_view, col_manage = st.columns(2)
            
            with col_view:
                st.info(f"تفاصيل المستند: {row['الموضوع']}")
                if row['اسم المرفق'] != "لا يوجد":
                    fpath = os.path.join(ATTACH_DIR, row['اسم المرفق'])
                    if os.path.exists(fpath):
                        with open(fpath, "rb") as f:
                            st.download_button("📥 تحميل المرفق", f, file_name=row['اسم المرفق'])
            
            with col_manage:
                # التحقق من صلاحية الحذف
                if can_action("delete"):
                    if st.button("🗑️ حذف السجل نهائياً"):
                        df = df[df["الرقم التسلسلي"] != selected_sn]
                        df.to_csv(DB_FILE, index=False)
                        st.success("تم الحذف"); st.rerun()
                else:
                    st.warning("🔒 ليس لديك صلاحية الحذف")

                # التحقق من صلاحية التعديل
                if can_action("edit"):
                    with st.expander("✏️ تعديل البيانات"):
                        with st.form("edit_form"):
                            new_sub = st.text_input("الموضوع", row['الموضوع'])
                            if st.form_submit_button("تحديث"):
                                df.loc[df["الرقم التسلسلي"] == selected_sn, "الموضوع"] = new_sub
                                df.to_csv(DB_FILE, index=False)
                                st.success("تم التحديث"); st.rerun()

# --- 7. صفحة الإضافة (للمخولين فقط) ---
elif menu == "إضافة وثيقة":
    st.title("➕ تسجيل صادر/وارد جديد")
    with st.form("add_form"):
        doc_no = st.text_input("رقم المستند")
        subj = st.text_input("الموضوع")
        file = st.file_uploader("المرفق")
        if st.form_submit_button("حفظ"):
            sn = f"EDMS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            fname = f"{sn}_{file.name}" if file else "لا يوجد"
            if file:
                with open(os.path.join(ATTACH_DIR, fname), "wb") as f: f.write(file.getbuffer())
            
            new_row = [sn, doc_no, datetime.now().strftime("%Y/%d/%m"), "", "", subj, "", fname]
            df.loc[len(df)] = new_row
            df.to_csv(DB_FILE, index=False)
            st.success("تمت الأرشفة!"); st.rerun()

# --- 8. صفحة النسخ الاحتياطي (للأدمن فقط) ---
elif menu == "النظام والنسخ الاحتياطي":
    if can_action("backup"):
        st.title("💾 إدارة النظام")
        # كود النسخ الاحتياطي والاسترجاع (كما في الرد السابق)
        if st.button("إنشاء نسخة احتياطية (.zip)"):
            shutil.make_archive("backup", 'zip', ".", ATTACH_DIR)
            st.success("تم تجهيز النسخة!")
    else:
        st.error("🔒 عذراً، هذه الصفحة مخصصة لمدير النظام فقط.")
