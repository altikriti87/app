import streamlit as st
import pandas as pd
import os
from datetime import datetime
import shutil
import zipfile
from PIL import Image

# --- 1. الإعدادات العامة والتنسيق (CSS) ---
st.set_page_config(page_title="نظام الأرشفة المتقدم - EDMS", page_icon="📂", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    /* تنسيق ترحيب المستخدم */
    .user-header {
        display: flex; align-items: center; background-color: white; padding: 15px 25px;
        border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 25px;
        border-right: 6px solid #4e73df;
    }
    .user-img { width: 65px; height: 65px; border-radius: 50%; object-fit: cover; margin-left: 20px; border: 2px solid #4e73df; }
    .user-text h2 { margin: 0; color: #2e59d9; font-size: 1.4rem; }
    .user-text p { margin: 0; color: #858796; font-size: 0.85rem; }

    /* تنسيق البطاقات الإحصائية */
    .dashboard-cards { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 30px; }
    .card { flex: 1; padding: 20px; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .blue-card { background: linear-gradient(135deg, #4e73df 0%, #224abe 100%); }
    .red-card { background: linear-gradient(135deg, #e74a3b 0%, #be2617 100%); }
    .yellow-card { background: linear-gradient(135deg, #f6c23e 0%, #dda20a 100%); color: #3a3b45; }
    
    .card h3 { margin: 0; font-size: 0.95rem; opacity: 0.9; }
    .card h2 { margin: 8px 0 0 0; font-size: 2rem; font-weight: bold; }

    /* أزرار القائمة الجانبية */
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; 
        text-align: right; transition: 0.3s; border: 1px solid #e3e6f0;
    }
    .stButton>button:hover { background-color: #4e73df !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة المجلدات وقاعدة البيانات ---
DB_FILE = "edms_scientific_office.csv"
USER_IMG_DIR = "user_profiles"
ARCHIVE_DIR = "archive_storage"

for folder in [USER_IMG_DIR, ARCHIVE_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

# المكونات الـ 14 المطلوبة للوثيقة
COLUMNS = [
    "ID NO", "Type", "Document Number", "Document Date", "From", "To", 
    "Subject", "Keywords", "Attachment Description", "File Names", 
    "Linked Documents", "Tags", "User ID", "Last Modified"
]

USERS = {
    "admin": {"pw": "123", "name": "مدير المكتب العلمي", "role": "Administrator", "img": "admin.png"},
    "staff": {"pw": "456", "name": "محرر الوثائق", "role": "Editor", "img": "staff.png"}
}

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=COLUMNS)

# --- 3. نظام الحماية وتسجيل الدخول ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        with st.container(border=True):
            st.title("🔐 بوابة الدخول")
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.button("تسجيل الدخول"):
                if u in USERS and USERS[u]["pw"] == p:
                    st.session_state.auth = True
                    st.session_state.user_id = u
                    st.session_state.page = "dash"
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة")
    st.stop()

df = load_data()
user_info = USERS[st.session_state.user_id]

# --- 4. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/716/716784.png", width=70)
    st.title("نظام الأرشفة الذكي")
    st.markdown("---")
    if st.button("📊 لوحة المؤشرات (Dashboard)"): st.session_state.page = "dash"; st.rerun()
    if st.button("📝 إنشاء وثيقة جديدة"): st.session_state.page = "new"; st.rerun()
    if st.button("🔍 البحث المتقدم"): st.session_state.page = "search"; st.rerun()
    if st.button("⚙️ الإعدادات والنسخ"): st.session_state.page = "settings"; st.rerun()
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

# --- 5. محتوى الصفحات ---

# أ. لوحة المؤشرات (Dashboard)
if st.session_state.page == "dash":
    # عرض صورة المستخدم واسمه
    img_path = os.path.join(USER_IMG_DIR, f"{st.session_state.user_id}.png")
    avatar = img_path if os.path.exists(img_path) else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    
    st.markdown(f"""
    <div class="user-header">
        <img src="{avatar}" class="user-img">
        <div class="user-text">
            <h2>مرحباً، {user_info['name']}</h2>
            <p>أنت الآن تدير النظام بصلاحية: <b>{user_info['role']}</b></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # البطاقات الإحصائية الثلاث
    total_docs = len(df)
    urgent_docs = len(df[df["Tags"].str.contains("عاجل|هام", na=False)])
    active_users = len(USERS)

    st.markdown(f"""
    <div class="dashboard-cards">
        <div class="card blue-card">
            <h3>إجمالي الوثائق المرفوعة</h3>
            <h2>{total_docs}</h2>
        </div>
        <div class="card red-card">
            <h3>وثائق هامة / عاجلة</h3>
            <h2>{urgent_docs}</h2>
        </div>
        <div class="card yellow-card">
            <h3>المستخدمين في النظام</h3>
            <h2>{active_users}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📑 آخر الوثائق المضافة حديثاً")
    st.dataframe(df.tail(10), use_container_width=True, hide_index=True)

# ب. إنشاء وثيقة جديدة (بناءً على المكونات الـ 14)
elif st.session_state.page == "new":
    st.title("📝 تسجيل وثيقة جديدة")
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            f_type = st.selectbox("Type (نوع الوثيقة)", ["صادر", "وارد", "مذكرة داخلية", "تقرير علمي"])
            f_doc_num = st.text_input("Document Number (رقم الكتاب)")
            f_doc_date = st.date_input("Document Date (تاريخ الكتاب)")
            f_from = st.text_input("From (الجهة المرسلة)")
            f_to = st.text_input("To (الجهة المستلمة)")
            f_subject = st.text_input("Subject (الموضوع)")
        
        with col2:
            f_keywords = st.text_input("Keywords (كلمات مفتاحية)")
            f_linked = st.text_input("Linked Documents (وثائق مرتبطة)")
            f_tags = st.multiselect("Tags (الوسوم)", ["هام", "عاجل", "سري", "قيد المراجعة", "منجز"])
            f_desc = st.text_area("Attachment Description (وصف المرفقات)")
        
        f_upload = st.file_uploader("File Names (رفع الملفات المرفقة)", accept_multiple_files=True)
        
        if st.form_submit_button("إتمام الأرشفة"):
            if f_doc_num and f_subject:
                # 1. إنشاء ID NO تلقائي
                id_no = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # 2. معالجة الملفات المرفوعة
                file_list = []
                if f_upload:
                    for up_file in f_upload:
                        saved_name = f"{id_no}_{up_file.name}"
                        with open(os.path.join(ARCHIVE_DIR, saved_name), "wb") as f:
                            f.write(up_file.getbuffer())
                        file_list.append(up_file.name)
                
                # 3. تجميع البيانات
                new_data = [
                    id_no, f_type, f_doc_num, str(f_doc_date), f_from, f_to,
                    f_subject, f_keywords, f_desc, "; ".join(file_list),
                    f_linked, ", ".join(f_tags), st.session_state.user_id, 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
                
                # 4. الحفظ
                df.loc[len(df)] = new_data
                df.to_csv(DB_FILE, index=False)
                st.success(f"✅ تم حفظ الوثيقة بنجاح! رقم القيد الفريد: {id_no}")
            else:
                st.error("⚠️ يرجى ملء رقم المستند والموضوع كحد أدنى.")

# ج. البحث المتقدم
elif st.session_state.page == "search":
    st.title("🔍 البحث في الأرشيف")
    q = st.text_input("ابحث عن طريق الرقم، الموضوع، الكلمات المفتاحية، أو الجهة...")
    
    if q:
        res = df[df.apply(lambda r: r.astype(str).str.contains(q, case=False).any(), axis=1)]
    else:
        res = df
        
    st.dataframe(res, use_container_width=True, hide_index=True)

# د. الإعدادات
elif st.session_state.page == "settings":
    st.title("⚙️ الإعدادات")
    st.subheader("👤 تحديث الصورة الشخصية")
    new_pic = st.file_uploader("اختر صورة شخصية (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if st.button("تأكيد تحديث الصورة"):
        if new_pic:
            img_ext = new_pic.name.split('.')[-1]
            save_path = os.path.join(USER_IMG_DIR, f"{st.session_state.user_id}.png")
            with open(save_path, "wb") as f:
                f.write(new_pic.getbuffer())
            st.success("تم تحديث الصورة الشخصية بنجاح!"); st.rerun()

    st.markdown("---")
    st.subheader("💾 النسخ الاحتياطي")
    if st.button("📤 تصدير أرشيف كامل (.zip)"):
        shutil.make_archive("Full_Backup", 'zip', ARCHIVE_DIR)
        with open("Full_Backup.zip", "rb") as f:
            st.download_button("تحميل الملف الآن", f, file_name=f"Backup_{datetime.now().strftime('%Y%m%d')}.zip")
