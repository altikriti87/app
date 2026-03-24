import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
import shutil
from PIL import Image
from fpdf import FPDF

# --- 1. إعدادات الهوية البصرية (CSS) ---
st.set_page_config(page_title="نظام الأرشفة المطور v4", layout="wide", page_icon="📂")

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
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة المجلدات وقاعدة البيانات ---
DB_FILE = "scientific_archive_final.csv"
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

def export_to_pdf(row):
    # استخدام fpdf2 لمعالجة البيانات بشكل أفضل
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt="Document Information Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=10)
    
    for col in COLUMNS:
        # لتجنب خطأ UnicodeEncodeError، نقوم بتنظيف النص عند التصدير فقط
        # النص الأصلي سيبقى بالعربي في جدول البيانات
        val = str(row[col]).encode('ascii', 'ignore').decode('ascii')
        pdf.multi_cell(0, 8, txt=f"{col}: {val if val else 'N/A'}", border=0)
        pdf.ln(2)
    
    return pdf.output()

# --- 3. نظام تسجيل الدخول ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            st.title("🔐 دخول النظام")
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.button("دخول"):
                if u in USERS and USERS[u]["pw"] == p:
                    st.session_state.auth, st.session_state.user_id = True, u
                    st.session_state.page = "dash"
                    st.rerun()
                else: st.error("بيانات غير صحيحة")
    st.stop()

df = load_data()
user_info = USERS[st.session_state.user_id]

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.title("📂 أرشفة المكتب العلمي")
    st.markdown("---")
    if st.button("📊 لوحة المؤشرات"): st.session_state.page = "dash"; st.rerun()
    if st.button("📝 إنشاء وثيقة جديدة"): st.session_state.page = "new"; st.rerun()
    if st.button("🔍 البحث والإدارة"): st.session_state.page = "search"; st.rerun()
    if st.button("⚙️ الإعدادات"): st.session_state.page = "settings"; st.rerun()
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج"): st.session_state.auth = False; st.rerun()

# --- 5. صفحات النظام ---

# أ. الداشبورد
if st.session_state.page == "dash":
    img_path = os.path.join(USER_IMG_DIR, f"{st.session_state.user_id}.png")
    avatar = img_path if os.path.exists(img_path) else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    st.markdown(f'<div class="user-header"><img src="{avatar}" class="user-img"><div class="user-text"><h2>أهلاً بك، {user_info["name"]}</h2><p>الصلاحية: {user_info["role"]}</p></div></div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="card blue-card"><h3>إجمالي الوثائق</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card red-card"><h3>وثائق عاجلة</h3><h2>{len(df[df["Tags"].str.contains("عاجل|هام", na=False)])}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card yellow-card"><h3>المستخدمين</h3><h2>{len(USERS)}</h2></div>', unsafe_allow_html=True)
    st.subheader("📑 آخر النشاطات")
    st.dataframe(df.tail(10), use_container_width=True, hide_index=True)

# ب. إنشاء وثيقة جديدة
elif st.session_state.page == "new":
    st.title("📝 إنشاء سجل أرشفة جديد")
    with st.form("new_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            f_type = st.selectbox("Type", ["صادر", "وارد", "داخلي"])
            f_num = st.text_input("Document Number")
            f_date = st.date_input("Document Date")
            f_from = st.text_input("From")
            f_to = st.text_input("To")
        with col2:
            f_sub = st.text_input("Subject")
            f_kw = st.text_input("Keywords")
            f_link = st.text_input("Linked Documents")
            f_tags = st.multiselect("Tags", ["عاجل", "سري", "هام", "منجز"])
            f_desc = st.text_area("Attachment Description")
        f_up = st.file_uploader("File Names (رفع المرفقات)", accept_multiple_files=True)
        
        if st.form_submit_button("حفظ الوثيقة"):
            if f_num and f_sub:
                id_no = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                f_str = ""
                if f_up:
                    for f in f_up:
                        with open(os.path.join(ARCHIVE_DIR, f"{id_no}_{f.name}"), "wb") as file:
                            file.write(f.getbuffer())
                        f_str += f.name + "; "
                new_row = [id_no, f_type, f_num, str(f_date), f_from, f_to, f_sub, f_kw, f_desc, f_str, f_link, ", ".join(f_tags), st.session_state.user_id, datetime.now().strftime("%Y-%m-%d %H:%M")]
                df.loc[len(df)] = new_row
                df.to_csv(DB_FILE, index=False)
                st.success(f"تم الحفظ بنجاح! رقم القيد: {id_no}")
            else: st.error("يرجى ملء الحقول الأساسية")

# ج. البحث والإدارة (تعديل، حذف، استعراض)
elif st.session_state.page == "search":
    st.title("🔍 إدارة الأرشيف")
    q = st.text_input("بحث سريع في كافة الحقول...")
    res = df[df.apply(lambda r: r.astype(str).str.contains(q, case=False).any(), axis=1)] if q else df
    st.dataframe(res, use_container_width=True, hide_index=True)

    if not res.empty:
        st.markdown("---")
        sel_id = st.selectbox("اختر الوثيقة للتحكم (ID NO):", ["---"] + res["ID NO"].tolist())
        if sel_id != "---":
            idx = df[df["ID NO"] == sel_id].index[0]
            row = df.loc[idx]
            t1, t2, t3 = st.tabs(["📄 استعراض ومعاينة", "✏️ تعديل شامل", "🗑️ إجراءات الحذف"])
            
            with t1:
                ci, cp = st.columns([1, 1.5])
                with ci:
                    st.info(f"الموضوع: {row['Subject']}")
                    try:
                        pdf_bytes = export_to_pdf(row)
                        st.download_button("📄 تحميل تقرير البيانات (PDF)", pdf_bytes, file_name=f"Report_{sel_id}.pdf")
                    except: st.error("خطأ في تصدير التقرير")
                with cp:
                    if not pd.isna(row["File Names"]) and row["File Names"] != "":
                        files = [f for f in row["File Names"].split("; ") if f]
                        s_file = st.selectbox("اختر ملفاً للمعاينة:", files)
                        f_path = os.path.join(ARCHIVE_DIR, f"{sel_id}_{s_file}")
                        if os.path.exists(f_path):
                            with open(f_path, "rb") as f: st.download_button(f"📥 تحميل {s_file}", f, file_name=s_file)
                            if s_file.lower().endswith('.pdf'):
                                with open(f_path, "rb") as f:
                                    b64 = base64.b64encode(f.read()).decode('utf-8')
                                st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="500"></iframe>', unsafe_allow_html=True)
            
            with t2:
                with st.form("edit_full_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        e_type = st.selectbox("Type", ["صادر", "وارد", "داخلي"], index=["صادر", "وارد", "داخلي"].index(row["Type"]))
                        e_num = st.text_input("Document Number", value=row["Document Number"])
                        e_date = st.text_input("Document Date", value=row["Document Date"])
                        e_from = st.text_input("From", value=row["From"])
                        e_to = st.text_input("To", value=row["To"])
                        e_sub = st.text_input("Subject", value=row["Subject"])
                    with c2:
                        e_kw = st.text_input("Keywords", value=row["Keywords"])
                        e_link = st.text_input("Linked Documents", value=row["Linked Documents"])
                        e_tags = st.text_input("Tags", value=row["Tags"])
                        e_desc = st.text_area("Attachment Description", value=row["Attachment Description"])
                    if st.form_submit_button("💾 تحديث كافة البيانات"):
                        df.loc[idx, ["Type", "Document Number", "Document Date", "From", "To", "Subject", "Keywords", "Linked Documents", "Tags", "Attachment Description"]] = [e_type, e_num, e_date, e_from, e_to, e_sub, e_kw, e_link, e_tags, e_desc]
                        df.at[idx, "Last Modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        df.to_csv(DB_FILE, index=False); st.success("تم التحديث!"); st.rerun()

            with t3:
                if st.button("🚨 حذف السجل والملفات نهائياً"):
                    if not pd.isna(row["File Names"]):
                        for f in row["File Names"].split("; "):
                            if f:
                                p = os.path.join(ARCHIVE_DIR, f"{sel_id}_{f}")
                                if os.path.exists(p): os.remove(p)
                    df = df.drop(idx); df.to_csv(DB_FILE, index=False); st.success("تم الحذف"); st.rerun()

# د. الإعدادات
elif st.session_state.page == "settings":
    st.title("⚙️ الإعدادات الشخصية")
    new_pic = st.file_uploader("رفع صورة شخصية جديدة", type=["png", "jpg"])
    if st.button("حفظ الصورة"):
        if new_pic:
            with open(os.path.join(USER_IMG_DIR, f"{st.session_state.user_id}.png"), "wb") as f:
                f.write(new_pic.getbuffer())
            st.success("تم التحديث بنجاح!"); st.rerun()
