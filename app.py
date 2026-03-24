import streamlit as st
import pandas as pd
import os
import io
import shutil
import zipfile
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق الجمالي ---
st.set_page_config(
    page_title="EDMS Professional Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق CSS مخصص للبطاقات والقائمة الجانبية
st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    /* تنسيق البطاقات الإحصائية */
    .st-emotion-cache-1r6slb0 { border-radius: 10px; }
    .card-container {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 25px;
    }
    .card {
        flex: 1;
        padding: 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .blue-card { background: linear-gradient(135deg, #4e73df 0%, #224abe 100%); }
    .red-card { background: linear-gradient(135deg, #e74a3b 0%, #be2617 100%); }
    .yellow-card { background: linear-gradient(135deg, #f6c23e 0%, #dda20a 100%); color: #3a3b45; }
    
    .card h3 { margin: 0; font-size: 1.2rem; opacity: 0.9; }
    .card h2 { margin: 10px 0 0 0; font-size: 2.5rem; font-weight: bold; }
    
    /* تنسيق الأزرار الجانبية */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        font-weight: bold;
        text-align: right;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #4e73df;
        color: white;
        transform: translateX(-5px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات والمستخدمين ---
DB_FILE = "edms_main_database.csv"
ATTACH_DIR = "attachments"
if not os.path.exists(ATTACH_DIR): os.makedirs(ATTACH_DIR)

# بيانات المستخدمين الافتراضية
USERS = {
    "admin": {"password": "123", "role": "Administrator"},
    "staff": {"password": "456", "role": "Editor"}
}

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["الرقم التسلسلي", "رقم المستند", "التاريخ", "الموضوع", "الحالة", "المرفق"])

# --- 3. نظام الحماية وتسجيل الدخول ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        with st.container(border=True):
            st.title("🔐 تسجيل الدخول")
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.button("دخول"):
                if u in USERS and USERS[u]["password"] == p:
                    st.session_state.authenticated = True
                    st.session_state.user = u
                    st.session_state.role = USERS[u]["role"]
                    st.session_state.page = "dashboard" # الصفحة الافتراضية
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
    st.stop()

df = load_data()

# --- 4. القائمة الجانبية (الأزرار المطلوبة) ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    st.markdown(f"**الرتبة:** {st.session_state.role}")
    st.markdown("---")
    
    # توزيع الأزرار الجانبية
    if st.button("📊 لوحة المؤشرات (Dashboard)"):
        st.session_state.page = "dashboard"
        st.rerun()
        
    if st.button("📝 إنشاء وثيقة جديدة"):
        st.session_state.page = "new_doc"
        st.rerun()
        
    if st.button("🔍 البحث عن وثيقة"):
        st.session_state.page = "search"
        st.rerun()
        
    if st.button("⚙️ إعدادات المستخدمين والنسخ"):
        st.session_state.page = "settings"
        st.rerun()
        
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. محتوى الصفحات بناءً على الاختيار ---

# أ. لوحة المؤشرات (Dashboard)
if st.session_state.page == "dashboard":
    st.title("🚀 لوحة المؤشرات")
    
    # الحسابات للبطاقات
    total_docs = len(df)
    pending_docs = len(df[df["الحالة"] == "غير منجز"])
    current_users = len(USERS)

    # عرض البطاقات الملونة
    st.markdown(f"""
    <div class="card-container">
        <div class="card blue-card">
            <h3>إجمالي الوثائق المرفوعة</h3>
            <h2>{total_docs}</h2>
        </div>
        <div class="card red-card">
            <h3>وثائق غير منجزة</h3>
            <h2>{pending_docs}</h2>
        </div>
        <div class="card yellow-card">
            <h3>المستخدمين النشطين</h3>
            <h2>{current_users}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📑 آخر الوثائق المضافة")
    st.dataframe(df.tail(10), use_container_width=True, hide_index=True)

# ب. إنشاء وثيقة جديدة
elif st.session_state.page == "new_doc":
    st.title("📝 إدخال وثيقة جديدة للأرشيف")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            doc_no = st.text_input("رقم المستند الأصلي")
            subj = st.text_input("الموضوع / العنوان")
        with c2:
            status = st.selectbox("حالة المعالجة", ["منجز", "غير منجز"])
            up_file = st.file_uploader("ارفق نسخة إلكترونية (Image/PDF)")
        
        if st.form_submit_button("حفظ المستند"):
            if doc_no and subj:
                sn = f"EDMS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                fname = f"{sn}_{up_file.name}" if up_file else "لا يوجد"
                if up_file:
                    with open(os.path.join(ATTACH_DIR, fname), "wb") as f:
                        f.write(up_file.getbuffer())
                
                # إضافة السجل
                new_row = [sn, doc_no, datetime.now().strftime("%Y/%d/%m"), subj, status, fname]
                df.loc[len(df)] = new_row
                df.to_csv(DB_FILE, index=False)
                st.success(f"✅ تم الحفظ بنجاح برقم قيد: {sn}")
            else:
                st.warning("⚠️ يرجى ملء الحقول الأساسية")

# ج. البحث عن وثيقة
elif st.session_state.page == "search":
    st.title("🔍 محرك البحث في الأرشيف")
    search_query = st.text_input("ادخل أي معلومة للبحث (رقم، موضوع، تاريخ)...")
    
    if search_query:
        results = df[df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]
    else:
        results = df
        
    st.dataframe(results, use_container_width=True, hide_index=True)
    
    if not results.empty:
        st.markdown("---")
        selected = st.selectbox("اختر وثيقة لعرض المرفق أو الحذف:", ["---"] + results["الرقم التسلسلي"].tolist())
        if selected != "---":
            row_data = df[df["الرقم التسلسلي"] == selected].iloc[0]
            if row_data["المرفق"] != "لا يوجد":
                path = os.path.join(ATTACH_DIR, row_data["المرفق"])
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        st.download_button("📥 تحميل المرفق", f, file_name=row_data["المرفق"])
            
            if st.session_state.role == "Administrator":
                if st.button("🗑️ حذف هذا السجل نهائياً"):
                    df = df[df["الرقم التسلسلي"] != selected]
                    df.to_csv(DB_FILE, index=False)
                    st.error("تم حذف السجل"); st.rerun()

# د. إعدادات المستخدمين والنسخ
elif st.session_state.page == "settings":
    st.title("⚙️ الإعدادات والنسخ الاحتياطي")
    
    tab1, tab2 = st.tabs(["👥 إدارة المستخدمين", "💾 النسخ الاحتياطي"])
    
    with tab1:
        st.write("المستخدمين الحاليين وصلاحياتهم:")
        st.json(USERS)
        st.info("لتغيير المستخدمين، يرجى تعديل كود المصدر (Dict: USERS) حالياً.")
        
    with tab2:
        st.subheader("تصدير واستيراد البيانات")
        c_b, c_r = st.columns(2)
        with c_b:
            if st.button("📤 إنشاء نسخة احتياطية ZIP"):
                b_name = f"EDMS_Backup_{datetime.now().strftime('%Y%m%d')}"
                shutil.make_archive(b_name, 'zip', ".", ATTACH_DIR)
                with zipfile.ZipFile(f"{b_name}.zip", 'a') as z:
                    if os.path.exists(DB_FILE): z.write(DB_FILE)
                with open(f"{b_name}.zip", "rb") as f:
                    st.download_button("تحميل النسخة", f, file_name=f"{b_name}.zip")
        
        with c_r:
            up_zip = st.file_uploader("استرجاع من نسخة احتياطية", type="zip")
            if st.button("📥 بدء الاسترجاع"):
                if up_zip:
                    with zipfile.ZipFile(up_zip, 'r') as zr:
                        zr.extractall(".")
                    st.success("تم استرجاع البيانات بنجاح!"); st.rerun()
