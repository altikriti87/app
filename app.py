import streamlit as st
import pandas as pd
import os
from datetime import datetime
import shutil
import zipfile

# --- 1. إعدادات الهوية البصرية والتنسيق (CSS) ---
st.set_page_config(page_title="EDMS - Dashboard", page_icon="📂", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    /* تنسيق قسم الترحيب وصورة المستخدم */
    .user-header {
        display: flex;
        align-items: center;
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        border-right: 5px solid #4e73df;
    }
    .user-img {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        object-fit: cover;
        margin-left: 20px;
        border: 2px solid #4e73df;
    }
    .user-info-text h2 { margin: 0; color: #2e59d9; font-size: 1.5rem; }
    .user-info-text p { margin: 0; color: #858796; font-size: 0.9rem; }

    /* تنسيق البطاقات الملونة (Cards) */
    .dashboard-cards {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 30px;
    }
    .card {
        flex: 1;
        padding: 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .blue-card { background: linear-gradient(135deg, #4e73df 0%, #224abe 100%); }
    .red-card { background: linear-gradient(135deg, #e74a3b 0%, #be2617 100%); }
    .yellow-card { background: linear-gradient(135deg, #f6c23e 0%, #dda20a 100%); color: #3a3b45; }
    
    .card h3 { margin: 0; font-size: 1rem; opacity: 0.9; }
    .card h2 { margin: 10px 0 0 0; font-size: 2.2rem; font-weight: bold; }

    /* تنسيق الأزرار الجانبية */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
        transition: 0.3s;
        border: 1px solid #e3e6f0;
        text-align: right;
    }
    .stButton>button:hover {
        background-color: #4e73df !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة البيانات والمجلدات ---
DB_FILE = "edms_master_db.csv"
USER_IMG_DIR = "user_profiles"
ATTACH_DIR = "docs_archive"

for folder in [USER_IMG_DIR, ATTACH_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

# بيانات المستخدمين (يمكنك إضافة صورهم في مجلد user_profiles)
USERS = {
    "admin": {"pw": "123", "name": "مدير النظام", "role": "Administrator", "img": "admin.png"},
    "staff": {"pw": "456", "name": "محرر المكتب", "role": "Editor", "img": "staff.png"}
}

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "رقم المستند", "التاريخ", "الموضوع", "الحالة", "المرفق"])

# --- 3. نظام تسجيل الدخول ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        with st.container(border=True):
            st.title("🔐 تسجيل الدخول")
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.button("دخول للنظام"):
                if u in USERS and USERS[u]["pw"] == p:
                    st.session_state.auth = True
                    st.session_state.user_key = u
                    st.session_state.page = "dash"
                    st.rerun()
                else:
                    st.error("بيانات خاطئة!")
    st.stop()

df = load_data()
user_data = USERS[st.session_state.user_key]

# --- 4. القائمة الجانبية (Navigation) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/716/716784.png", width=80)
    st.title("نظام الأرشفة")
    st.markdown("---")
    
    # أزرار التنقل المطلوبة
    if st.button("📝 إنشاء وثيقة جديدة"): st.session_state.page = "new"; st.rerun()
    if st.button("🔍 البحث عن وثيقة"): st.session_state.page = "search"; st.rerun()
    if st.button("⚙️ إعدادات المستخدمين"): st.session_state.page = "settings"; st.rerun()
    if st.button("📊 لوحة المؤشرات"): st.session_state.page = "dash"; st.rerun()
    
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

# --- 5. محتوى الصفحات ---

# أ. لوحة المؤشرات (Dashboard)
if st.session_state.page == "dash":
    # قسم الترحيب مع الصورة
    user_img_path = os.path.join(USER_IMG_DIR, user_data['img'])
    avatar = user_img_path if os.path.exists(user_img_path) else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    
    st.markdown(f"""
    <div class="user-header">
        <img src="{avatar}" class="user-img">
        <div class="user-info-text">
            <h2>أهلاً بك، {user_data['name']}</h2>
            <p>لديك كامل الصلاحيات كـ {user_data['role']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # البطاقات الملونة (إحصائيات)
    total = len(df)
    pending = len(df[df["الحالة"] == "غير منجز"])
    users_count = len(USERS)

    st.markdown(f"""
    <div class="dashboard-cards">
        <div class="card blue-card">
            <h3>إجمالي الوثائق</h3>
            <h2>{total}</h2>
        </div>
        <div class="card red-card">
            <h3>وثائق غير منجزة</h3>
            <h2>{pending}</h2>
        </div>
        <div class="card yellow-card">
            <h3>المستخدمين النشطين</h3>
            <h2>{users_count}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📑 آخر النشاطات")
    st.dataframe(df.tail(10), use_container_width=True, hide_index=True)

# ب. إنشاء وثيقة جديدة
elif st.session_state.page == "new":
    st.title("📝 إدراج وثيقة جديدة")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            d_no = st.text_input("رقم المستند")
            d_sub = st.text_input("الموضوع")
        with c2:
            d_stat = st.selectbox("حالة الإنجاز", ["منجز", "غير منجز"])
            d_file = st.file_uploader("رفع المرفق")
        
        if st.form_submit_button("حفظ في الأرشيف"):
            if d_no and d_sub:
                id_val = f"ID-{datetime.now().strftime('%m%d%H%M%S')}"
                fname = f"{id_val}_{d_file.name}" if d_file else "لا يوجد"
                if d_file:
                    with open(os.path.join(ATTACH_DIR, fname), "wb") as f: f.write(d_file.getbuffer())
                
                new_row = [id_val, d_no, datetime.now().strftime("%Y/%m/%d"), d_sub, d_stat, fname]
                df.loc[len(df)] = new_row
                df.to_csv(DB_FILE, index=False)
                st.success("تمت الأرشفة بنجاح!")
            else:
                st.warning("يرجى ملء البيانات الأساسية")

# ج. البحث عن وثيقة
elif st.session_state.page == "search":
    st.title("🔍 محرك البحث")
    query = st.text_input("ابحث بالرقم أو الموضوع...")
    if query:
        res = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]
    else:
        res = df
    st.dataframe(res, use_container_width=True, hide_index=True)

# د. إعدادات المستخدمين والنسخ الاحتياطي
elif st.session_state.page == "settings":
    st.title("⚙️ الإعدادات والنسخ الاحتياطي")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("👤 الملف الشخصي")
        st.write(f"الاسم: {user_data['name']}")
        st.write(f"الصلاحية: {user_data['role']}")
        new_img = st.file_uploader("تحديث صورتك الشخصية", type=["png", "jpg"])
        if st.button("حفظ الصورة الجديدة"):
            if new_img:
                with open(os.path.join(USER_IMG_DIR, f"{st.session_state.user_key}.png"), "wb") as f:
                    f.write(new_img.getbuffer())
                st.success("تم التحديث! سيظهر عند التحديث القادم."); st.rerun()

    with col_b:
        st.subheader("💾 إدارة البيانات")
        if st.button("📤 تصدير نسخة احتياطية (.zip)"):
            shutil.make_archive("backup", 'zip', ".", ATTACH_DIR)
            with open("backup.zip", "rb") as f:
                st.download_button("تحميل النسخة", f, file_name="Archive_Backup.zip")
