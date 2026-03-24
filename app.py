import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
import shutil
from fpdf import FPDF # يحتاج تثبيت مكتبة fpdf

# --- 1. إعدادات وتنسيق ---
st.set_page_config(page_title="نظام الأرشفة المتكامل v3", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #e3e6f0; border-radius: 5px 5px 0 0; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #4e73df !important; color: white !important; }
    .pdf-container { border: 1px solid #ccc; border-radius: 10px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة البيانات ---
DB_FILE = "scientific_office_v3.csv"
ARCHIVE_DIR = "archive_storage"
if not os.path.exists(ARCHIVE_DIR): os.makedirs(ARCHIVE_DIR)

COLUMNS = ["ID NO", "Type", "Document Number", "Document Date", "From", "To", "Subject", 
           "Keywords", "Attachment Description", "File Names", "Linked Documents", 
           "Tags", "User ID", "Last Modified"]

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=COLUMNS)

def save_to_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    # إضافة خط يدعم العربية أو استخدام الخطوط الافتراضية للإنجليزية حالياً
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Document Archive Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    for col in COLUMNS:
        pdf.cell(200, 10, txt=f"{col}: {row[col]}", ln=True, align='L')
    return pdf.output(dest='S').encode('latin-1')

# --- 3. نظام الجلسة والقائمة الجانبية ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    # (كود تسجيل الدخول المختصر للسرعة)
    u = st.sidebar.text_input("User")
    p = st.sidebar.text_input("Pass", type="password")
    if st.sidebar.button("Login"):
        if u == "admin" and p == "123":
            st.session_state.auth, st.session_state.user_id = True, u
            st.rerun()
    st.stop()

df = load_data()
if "page" not in st.session_state: st.session_state.page = "search"

with st.sidebar:
    st.title("📂 القائمة")
    if st.button("📊 الداشبورد"): st.session_state.page = "dash"; st.rerun()
    if st.button("📝 إضافة جديد"): st.session_state.page = "new"; st.rerun()
    if st.button("🔍 الإدارة والبحث"): st.session_state.page = "search"; st.rerun()

# --- 4. صفحة الإدارة والبحث (التعديل والاستعراض) ---
if st.session_state.page == "search":
    st.title("🔍 إدارة وثائق المكتب العلمي")
    q = st.text_input("بحث شامل...")
    res = df[df.apply(lambda r: r.astype(str).str.contains(q, case=False).any(), axis=1)] if q else df
    st.dataframe(res, use_container_width=True)

    if not res.empty:
        st.markdown("---")
        selected_id = st.selectbox("اختر الوثيقة للتحكم (ID NO):", ["---"] + res["ID NO"].tolist())
        
        if selected_id != "---":
            idx = df[df["ID NO"] == selected_id].index[0]
            row = df.loc[idx]
            
            t1, t2, t3 = st.tabs(["👁️ استعراض ومعاينة", "✏️ تعديل كافة البنود", "⚙️ إجراءات"])

            # 1. قسم الاستعراض والمعاينة
            with t1:
                col_info, col_preview = st.columns([1, 1.5])
                with col_info:
                    st.subheader("تفاصيل المستند")
                    st.write(f"**الموضوع:** {row['Subject']}")
                    st.write(f"**من:** {row['From']} -> **إلى:** {row['To']}")
                    
                    # زر تصدير البيانات PDF
                    pdf_data = save_to_pdf(row)
                    st.download_button("📄 تصدير البيانات كـ PDF", pdf_data, file_name=f"Report_{selected_id}.pdf")

                with col_preview:
                    st.subheader("المرفقات والمعاينة")
                    if not pd.isna(row["File Names"]) and row["File Names"] != "":
                        files = [f for f in row["File Names"].split("; ") if f]
                        selected_file = st.selectbox("اختر ملفاً للمعاينة:", files)
                        file_path = os.path.join(ARCHIVE_DIR, f"{selected_id}_{selected_file}")
                        
                        if os.path.exists(file_path):
                            # زر التحميل
                            with open(file_path, "rb") as f:
                                st.download_button(f"📥 تحميل {selected_file}", f, file_name=selected_file)
                            
                            # معاينة PDF إذا كان الملف من نوع PDF
                            if selected_file.lower().endswith('.pdf'):
                                with open(file_path, "rb") as f:
                                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                            else:
                                st.info("المعاينة المباشرة متاحة لملفات PDF فقط. لملفات الصور أو Excel يرجى استخدام زر التحميل.")

            # 2. قسم تعديل كافة البنود
            with t2:
                st.subheader("تحديث بيانات الوثيقة")
                with st.form("edit_all_fields"):
                    c1, c2 = st.columns(2)
                    with c1:
                        e_type = st.selectbox("Type", ["صادر", "وارد", "داخلي"], index=["صادر", "وارد", "داخلي"].index(row["Type"]))
                        e_num = st.text_input("Document Number", value=row["Document Number"])
                        e_date = st.text_input("Document Date", value=row["Document Date"])
                        e_from = st.text_input("From", value=row["From"])
                        e_to = st.text_input("To", value=row["To"])
                    with c2:
                        e_sub = st.text_input("Subject", value=row["Subject"])
                        e_kw = st.text_input("Keywords", value=row["Keywords"])
                        e_link = st.text_input("Linked Documents", value=row["Linked Documents"])
                        e_tags = st.text_input("Tags", value=row["Tags"])
                        e_desc = st.text_area("Description", value=row["Attachment Description"])
                    
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        df.loc[idx, ["Type", "Document Number", "Document Date", "From", "To", "Subject", "Keywords", "Linked Documents", "Tags", "Attachment Description"]] = \
                            [e_type, e_num, e_date, e_from, e_to, e_sub, e_kw, e_link, e_tags, e_desc]
                        df.at[idx, "Last Modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        df.to_csv(DB_FILE, index=False)
                        st.success("تم تحديث كافة البيانات بنجاح!"); st.rerun()

            # 3. قسم الإجراءات (حذف)
            with t3:
                if st.button("🗑️ حذف الوثيقة نهائياً"):
                    # حذف الملفات الفعلية
                    if not pd.isna(row["File Names"]):
                        for f in row["File Names"].split("; "):
                            if f:
                                p = os.path.join(ARCHIVE_DIR, f"{selected_id}_{f}")
                                if os.path.exists(p): os.remove(p)
                    df = df.drop(idx)
                    df.to_csv(DB_FILE, index=False)
                    st.success("تم الحذف!"); st.rerun()

# --- 5. إضافة جديد (مختصر) ---
elif st.session_state.page == "new":
    st.title("📝 إضافة وثيقة")
    # (نفس كود الإضافة السابق في الردود السابقة...)
    # تأكد من استخدام f.write(up.getbuffer()) لحفظ الملفات في ARCHIVE_DIR
