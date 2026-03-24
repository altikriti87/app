import streamlit as st
import pandas as pd
import os
import io
import shutil
import zipfile
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق الاحترافي ---
st.set_page_config(
    page_title="EDMS - نظام إدارة الوثائق والصلاحيات",
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
        padding: 5px 12px;
        border-radius: 20px;
        background-color: #4e73df;
        color: white;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. قاعدة بيانات المستخدمين (Username: Password, Role) ---
USERS = {
    "admin": {"password": "123", "role": "Administrator"}, # كامل الصلاحيات
    "editor": {"password": "456", "role": "Editor"},       # إضافة وتعديل فقط
    "viewer": {"password": "789", "role": "Viewer"}        # عرض وبحث فقط
}

def can_access(action):
    role = st.session_state.get("user_role", "Viewer")
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
        st.write("")
        with st.container(border=True):
            st.title("🔐 تسجيل الدخول")
            u_input = st.text_input("اسم المستخدم")
            p_input = st.text_input("كلمة المرور", type="password")
            if st.button("دخول للنظام"):
                if u_input in USERS and USERS[u_input]["password"] == p_input:
                    st.session_state.authenticated = True
                    st.session_state.username = u_input
                    st.session_state.user_role = USERS[u_input]["role"]
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    st.stop()

# --- 4. إدارة الملفات والبيانات ---
ATTACH_DIR = "attachments"
if not os.path.exists(ATTACH_DIR): os.makedirs(ATTACH_DIR)
DB_FILE = "edms_secure_archive.csv"
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
    
    menu_options = ["لوحة التحكم (Dashboard)"]
    if can_access("add"): menu_options.append("إضافة وثيقة جديدة")
    if can_access("backup"): menu_options.append("النسخ الاحتياطي والاسترجاع")
    
    menu = st.radio("القائمة الرئيسية", menu_options)
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. صفحة لوحة التحكم (عرض / بحث / حذف / تعديل) ---
if menu == "لوحة التحكم (Dashboard)":
    st.title("📂 خزانة ملفات الصادر والوارد")
    
    # محرك البحث
    search = st.text_input("🔍 ابحث عن أي وثيقة (موضوع، رقم، جهة)...")
    f_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df
    
    st.dataframe(f_df, use_container_width=True, hide_index=True)

    if not df.empty:
        st.markdown("---")
        st.subheader("🛠️ إدارة الوثيقة المختارة")
        selected_sn = st.selectbox("اختر الرقم التسلسلي للإدارة:", ["---"] + df["الرقم التسلسلي"].tolist())
        
        if selected_sn != "---":
            row = df[df["الرقم التسلسلي"] == selected_sn].iloc[0]
            c1, c2 = st.columns([1, 1.5])

            with c1:
                st.markdown(f"""<div class="data-card"><h4>📄 تفاصيل الوثيقة</h4>
                <b>الرقم:</b> {selected_sn}<br><b>الموضوع:</b> {row['الموضوع']}<br>
                <b>التاريخ:</b> {row['تاريخ الأرشفة']}</div>""", unsafe_allow_html=True)
                
                # تحميل المرفق
                if row['اسم المرفق'] != "لا يوجد":
                    path = os.path.join(ATTACH_DIR, row['اسم المرفق'])
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            st.download_button("📥 تحميل المرفق", f, file_name=row['اسم المرفق'])
                
                # الحذف (فقط للمسؤول)
                if can_access("delete"):
                    if st.button("🗑️ حذف السجل نهائياً"):
                        df = df[df["الرقم التسلسلي"] != selected_sn]
                        df.to_csv(DB_FILE, index=False)
                        st.success("تم الحذف بنجاح"); st.rerun()
                else:
                    st.warning("🔒 ليس لديك صلاحية الحذف")

            with c2:
                # التعديل (للمسؤول والمحرر)
                if can_access("edit"):
                    with st.expander("✏️ تعديل بيانات الوثيقة"):
                        with st.form("edit_f"):
                            new_doc = st.text_input("رقم المستند", row['رقم المستند'])
                            new_sub = st.text_input("الموضوع", row['الموضوع'])
                            new_inc = st.text_input("الجهة الواردة", row['الجهة الواردة'])
                            new_out = st.text_input("الجهة المصدرة", row['الجهة المصدرة'])
                            if st.form_submit_button("حفظ التغييرات"):
                                df.loc[df["الرقم التسلسلي"] == selected_sn, ["رقم المستند", "الموضوع", "الجهة الواردة", "الجهة المصدرة"]] = [new_doc, new_sub, new_inc, new_out]
                                df.to_csv(DB_FILE, index=False)
                                st.success("✅ تم التحديث"); st.rerun()
                else:
                    st.info("ℹ️ عرض التفاصيل فقط (لا تملك صلاحية التعديل)")

# --- 7. صفحة الإضافة (للمسؤول والمحرر) ---
elif menu == "إضافة وثيقة جديدة":
    st.title("➕ تسجيل وثيقة صادر/وارد")
    fc = st.session_state.form_count
    with st.form("add_f"):
        col_a, col_b = st.columns(2)
        with col_a:
            doc_no = st.text_input("رقم المستند الورقي", key=f"d_{fc}")
            inc_e = st.text_input("الجهة الواردة", key=f"i_{fc}")
        with col_b:
            out_e = st.text_input("الجهة المصدرة", key=f"o_{fc}")
            subj = st.text_input("الموضوع", key=f"s_{fc}")
        
        up_file = st.file_uploader("رفع صورة/ملف الوثيقة", key=f"f_{fc}")
        
        if st.form_submit_button("إتمام الأرشفة"):
            if doc_no and subj:
                sn = f"EDMS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                fname = f"{sn}_{up_file.name}" if up_file else "لا يوجد"
                if up_file:
                    with open(os.path.join(ATTACH_DIR, fname), "wb") as f: f.write(up_file.getbuffer())
                
                new_row = [sn, doc_no, datetime.now().strftime("%Y/%d/%m"), inc_e, out_e, subj, "", fname]
                df.loc[len(df)] = new_row
                df.to_csv(DB_FILE, index=False)
                st.success(f"✅ تمت الأرشفة برقم: {sn}")
                st.session_state.form_count += 1
                st.rerun()
            else:
                st.error("⚠️ رقم المستند والموضوع مطلوبان")

# --- 8. صفحة النسخ الاحتياطي (للمسؤول فقط) ---
elif menu == "النسخ الاحتياطي والاسترجاع":
    st.title("💾 إدارة قاعدة البيانات")
    if can_access("backup"):
        c_back, c_rest = st.columns(2)
        with c_back:
            st.subheader("📤 تصدير نسخة احتياطية")
            if st.button("إنشاء Backup (.zip)"):
                b_name = f"EDMS_Backup_{datetime.now().strftime('%Y%m%d')}"
                shutil.make_archive(b_name, 'zip', ".", ATTACH_DIR)
                with zipfile.ZipFile(f"{b_name}.zip", 'a') as z:
                    if os.path.exists(DB_FILE): z.write(DB_FILE)
                with open(f"{b_name}.zip", "rb") as f:
                    st.download_button("📥 تحميل النسخة", f, file_name=f"{b_name}.zip")
        
        with c_rest:
            st.subheader("📥 استرجاع نسخة")
            up_zip = st.file_uploader("ارفع ملف الـ ZIP", type="zip")
            if st.button("بدء الاسترجاع"):
                if up_zip:
                    with zipfile.ZipFile(up_zip, 'r') as z: z.extractall(".")
                    st.success("✅ تم الاسترجاع! أعد تحميل الصفحة."); st.rerun()
    else:
        st.error("🔒 عذراً، الوصول لهذه الصفحة مقتصر على مدير النظام فقط.")
