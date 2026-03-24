import streamlit as st
import pandas as pd
import os
from datetime import datetime
import shutil
import zipfile

# --- 1. الإعدادات العامة والتنسيق (CSS) ---
st.set_page_config(page_title="نظام الأرشفة المتكامل", page_icon="📂", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    .user-header {
        display: flex; align-items: center; background-color: white; padding: 15px 25px;
        border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 25px;
        border-right: 6px solid #4e73df;
    }
    .user-img { width: 65px; height: 65px; border-radius: 50%; object-fit: cover; margin-left: 20px; border: 2px solid #4e73df; }
    .dashboard-cards { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 30px; }
    .card { flex: 1; padding: 20px; border-radius: 12px; color: white; text-align: center; }
    .blue-card { background: linear-gradient(135deg, #4e73df 0%, #224abe 100%); }
    .red-card { background: linear-gradient(135deg, #e74a3b 0%, #be2617 100%); }
    .yellow-card { background: linear-gradient(135deg, #f6c23e 0%, #dda20a 100%); color: #3a3b45; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة المجلدات والبيانات ---
DB_FILE = "scientific_office_v2.csv"
USER_IMG_DIR = "user_profiles"
ARCHIVE_DIR = "archive_storage"

for folder in [USER_IMG_DIR, ARCHIVE_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

COLUMNS = [
    "ID NO", "Type", "Document Number", "Document Date", "From", "To", 
    "Subject", "Keywords", "Attachment Description", "File Names", 
    "Linked Documents", "Tags", "User ID", "Last Modified"
]

USERS = {
    "admin": {"pw": "123", "name": "مدير المكتب العلمي", "role": "Administrator"},
    "staff": {"pw": "456", "name": "محرر الوثائق", "role": "Editor"}
}

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=COLUMNS)

# --- 3. نظام تسجيل الدخول ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            st.title("🔐 دخول النظام")
            u = st.text_input("المستخدم")
            p = st.text_input("الكلمة", type="password")
            if st.button("دخول"):
                if u in USERS and USERS[u]["pw"] == p:
                    st.session_state.auth, st.session_state.user_id = True, u
                    st.session_state.page = "dash"
                    st.rerun()
    st.stop()

df = load_data()
user_info = USERS[st.session_state.user_id]

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.title("📂 الأرشفة الإلكترونية")
    if st.button("📊 لوحة المؤشرات"): st.session_state.page = "dash"; st.rerun()
    if st.button("📝 إنشاء وثيقة جديدة"): st.session_state.page = "new"; st.rerun()
    if st.button("🔍 البحث والإدارة"): st.session_state.page = "search"; st.rerun()
    if st.button("⚙️ الإعدادات"): st.session_state.page = "settings"; st.rerun()
    st.markdown("---")
    if st.button("🚪 خروج"): st.session_state.auth = False; st.rerun()

# --- 5. محتوى الصفحات ---

# أ. لوحة المؤشرات
if st.session_state.page == "dash":
    img_p = os.path.join(USER_IMG_DIR, f"{st.session_state.user_id}.png")
    avatar = img_p if os.path.exists(img_p) else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    st.markdown(f'<div class="user-header"><img src="{avatar}" class="user-img"><div class="user-text"><h2>أهلاً، {user_info["name"]}</h2><p>الصلاحية: {user_info["role"]}</p></div></div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="card blue-card"><h3>إجمالي الوثائق</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card red-card"><h3>وثائق عاجلة</h3><h2>{len(df[df["Tags"].str.contains("عاجل", na=False)])}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card yellow-card"><h3>المستخدمين</h3><h2>{len(USERS)}</h2></div>', unsafe_allow_html=True)
    st.dataframe(df.tail(5), use_container_width=True)

# ب. إنشاء وثيقة جديدة
elif st.session_state.page == "new":
    st.title("📝 تسجيل وثيقة")
    with st.form("new_f", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            t = st.selectbox("Type", ["صادر", "وارد", "داخلي"])
            dn = st.text_input("Document Number")
            dd = st.date_input("Document Date")
            fr = st.text_input("From")
            to = st.text_input("To")
        with c2:
            sub = st.text_input("Subject")
            kw = st.text_input("Keywords")
            ld = st.text_input("Linked Documents")
            tg = st.multiselect("Tags", ["عاجل", "سري", "منجز"])
            ad = st.text_area("Description")
        up = st.file_uploader("Files", accept_multiple_files=True)
        
        if st.form_submit_button("حفظ"):
            id_no = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            f_names = ""
            if up:
                for f in up:
                    with open(os.path.join(ARCHIVE_DIR, f"{id_no}_{f.name}"), "wb") as file: file.write(f.getbuffer())
                    f_names += f.name + "; "
            new_r = [id_no, t, dn, str(dd), fr, to, sub, kw, ad, f_names, ld, ", ".join(tg), st.session_state.user_id, datetime.now().strftime("%Y-%m-%d %H:%M")]
            df.loc[len(df)] = new_r
            df.to_csv(DB_FILE, index=False)
            st.success("تم الحفظ!"); st.rerun()

# ج. البحث، التعديل، الحذف، والاستعراض (الإدارة الكاملة)
elif st.session_state.page == "search":
    st.title("🔍 إدارة الأرشيف")
    q = st.text_input("ابحث هنا...")
    res = df[df.apply(lambda r: r.astype(str).str.contains(q, case=False).any(), axis=1)] if q else df
    st.dataframe(res, use_container_width=True, hide_index=True)

    if not res.empty:
        st.markdown("---")
        selected_id = st.selectbox("اختر ID NO للتحكم بالوثيقة:", ["---"] + res["ID NO"].tolist())
        
        if selected_id != "---":
            idx = df[df["ID NO"] == selected_id].index[0]
            row = df.loc[idx]
            
            tab_view, tab_edit, tab_delete = st.tabs(["📄 استعراض المرفقات", "✏️ تعديل البيانات", "🗑️ حذف السجل"])
            
            with tab_view:
                st.subheader("الملفات المرفقة لهذه الوثيقة:")
                if pd.isna(row["File Names"]) or row["File Names"] == "":
                    st.warning("لا توجد ملفات مرفقة.")
                else:
                    files = row["File Names"].split("; ")
                    for f_name in files:
                        if f_name:
                            full_p = os.path.join(ARCHIVE_DIR, f"{selected_id}_{f_name}")
                            if os.path.exists(full_p):
                                with open(full_p, "rb") as f:
                                    st.download_button(f"📥 تحميل: {f_name}", f, file_name=f_name, key=f_name)
                            else: st.error(f"الملف {f_name} غير موجود في السيرفر.")

            with tab_edit:
                with st.form("edit_f"):
                    e_sub = st.text_input("Subject", value=row["Subject"])
                    e_to = st.text_input("To", value=row["To"])
                    e_tags = st.text_input("Tags (فصل بفاصلة)", value=row["Tags"])
                    if st.form_submit_button("تحديث البيانات"):
                        df.at[idx, "Subject"] = e_sub
                        df.at[idx, "To"] = e_to
                        df.at[idx, "Tags"] = e_tags
                        df.at[idx, "Last Modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        df.to_csv(DB_FILE, index=False)
                        st.success("تم التعديل!"); st.rerun()

            with tab_delete:
                st.warning("هل أنت متأكد من حذف هذا السجل وجميع ملفاته المرفقة؟")
                if st.button("نعم، احذف نهائياً"):
                    # حذف الملفات من المجلد أولاً
                    if not pd.isna(row["File Names"]):
                        for f_name in row["File Names"].split("; "):
                            if f_name:
                                p = os.path.join(ARCHIVE_DIR, f"{selected_id}_{f_name}")
                                if os.path.exists(p): os.remove(p)
                    # حذف السجل من DataFrame
                    df = df.drop(idx)
                    df.to_csv(DB_FILE, index=False)
                    st.success("تم الحذف بنجاح!"); st.rerun()

# د. الإعدادات
elif st.session_state.page == "settings":
    st.title("⚙️ الإعدادات")
    up_p = st.file_uploader("تحديث صورتك الشخصية", type="png")
    if st.button("حفظ الصورة"):
        if up_p:
            with open(os.path.join(USER_IMG_DIR, f"{st.session_state.user_id}.png"), "wb") as f: f.write(up_p.getbuffer())
            st.success("تم التحديث!"); st.rerun()
