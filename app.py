import streamlit as st
import pandas as pd
import os
import base64
from datetime import date

# --- 1. إعدادات النظام والمجلدات ---
DB_FILE = "archive_db.csv"
UPLOAD_DIR = "uploaded_documents"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE).to_dict('records')
    return []

def save_data(data):
    if data:
        df = pd.DataFrame(data)
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    else:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

# تهيئة الجلسة
if 'archive_data' not in st.session_state:
    st.session_state['archive_data'] = load_data()
if 'menu_option' not in st.session_state:
    st.session_state['menu_option'] = 'الرئيسية'

# --- 2. دالة المعاينة ---
def display_file(file_name):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        st.error("File not found!")
        return
    
    file_extension = os.path.splitext(file_name)[1].lower()
    if file_extension == ".pdf":
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    elif file_extension in [".jpg", ".jpeg", ".png"]:
        st.image(file_path)
    else:
        st.warning("Preview not available for this file type.")

# --- 3. تصميم الواجهة ---
st.set_page_config(page_title="نظام الأرشفة المطور", layout="wide")
st.markdown("""
<style>
    .stButton > button { width: 100%; border-radius: 5px; }
    .header-style { text-align: center; color: #1E3A5F; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>📂 القائمة</h2>", unsafe_allow_html=True)
    if st.button("🏠 الرئيسية"): st.session_state['menu_option'] = 'الرئيسية'
    if st.button("➕ إضافة مستند"): st.session_state['menu_option'] = 'إضافة'
    if st.button("🔍 البحث والإدارة"): st.session_state['menu_option'] = 'بحث'
    if st.button("📊 سجل الأرشيف"): st.session_state['menu_option'] = 'عرض'

# --- 5. منطق الصفحات ---

if st.session_state['menu_option'] == 'الرئيسية':
    st.markdown("<h1 class='header-style'>نظام الأرشفة الإلكتروني</h1>", unsafe_allow_html=True)
    st.metric("إجمالي الوثائق", len(st.session_state['archive_data']))

elif st.session_state['menu_option'] == 'إضافة':
    st.header("إضافة مستند جديد")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            subject = st.text_input("الموضوع")
            doc_type = st.selectbox("النوع", ["كتاب رسمي", "قرار", "تعميم"])
            sender = st.text_input("المرسل")
        with c2:
            receiver = st.text_input("المستلم")
            doc_date = st.date_input("التاريخ")
            tags = st.text_input("الوسوم")
        uploaded_files = st.file_uploader("رفع ملفات", accept_multiple_files=True)
        if st.form_submit_button("حفظ"):
            files = []
            for f in uploaded_files:
                with open(os.path.join(UPLOAD_DIR, f.name), "wb") as fs:
                    fs.write(f.getbuffer())
                files.append(f.name)
            entry = {"ID": len(st.session_state['archive_data'])+1, "الموضوع": subject, "النوع": doc_type, "المرسل": sender, "المستلم": receiver, "التاريخ": str(doc_date), "الوسوم": tags, "المرفقات": "; ".join(files)}
            st.session_state['archive_data'].append(entry)
            save_data(st.session_state['archive_data'])
            st.success("Saved!")

elif st.session_state['menu_option'] == 'بحث':
    st.header("🔍 البحث والإدارة")
    if st.session_state['archive_data']:
        df = pd.DataFrame(st.session_state['archive_data'])
        search = st.text_input("ابحث في أي حقل (موضوع، مرسل، نوع...):")
        
        if search:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
        
        # عرض الجدول
        st.write("### تفاصيل الوثائق:")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.write("### إجراءات سريعة على المستند المختار:")
        
        # اختيار مستند من القائمة المنسدلة بناءً على نتائج البحث للقيام بإجراءات
        if not df.empty:
            target_id = st.selectbox("اختر رقم المستند (ID) للمعالجة:", df["ID"].tolist())
            idx = next(i for i, item in enumerate(st.session_state['archive_data']) if item["ID"] == target_id)
            
            col_preview, col_edit, col_del = st.columns(3)
            
            with col_preview:
                if st.button("👁️ معاينة المرفق الأول"):
                    files = st.session_state['archive_data'][idx]['المرفقات'].split("; ")
                    if files[0]: display_file(files[0])
            
            with col_edit:
                with st.popover("✏️ تعديل البيانات"):
                    new_sub = st.text_input("تعديل الموضوع", value=st.session_state['archive_data'][idx]['الموضوع'])
                    if st.button("تحديث"):
                        st.session_state['archive_data'][idx]['الموضوع'] = new_sub
                        save_data(st.session_state['archive_data'])
                        st.rerun()

            with col_del:
                if st.button("🗑️ حذف المستند النهائي", type="primary"):
                    st.session_state['archive_data'].pop(idx)
                    save_data(st.session_state['archive_data'])
                    st.rerun()
    else:
        st.info("No data yet.")

elif st.session_state['menu_option'] == 'عرض':
    st.header("📊 السجل الكامل")
    if st.session_state['archive_data']:
        st.table(pd.DataFrame(st.session_state['archive_data']))
