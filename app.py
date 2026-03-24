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
    df = pd.DataFrame(data)
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# تهيئة الجلسة
if 'archive_data' not in st.session_state:
    st.session_state['archive_data'] = load_data()
if 'menu_option' not in st.session_state:
    st.session_state['menu_option'] = 'الرئيسية'

# --- 2. دالة المعاينة (PDF و الصور) ---
def display_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    elif file_extension in [".jpg", ".jpeg", ".png"]:
        st.image(file_path, use_container_width=True)
    else:
        st.warning("⚠️ هذا النوع من الملفات لا يدعم المعاينة المباشرة، يمكنك تحميله فقط.")

# --- 3. تصميم الواجهة ---
st.set_page_config(page_title="نظام الأرشفة المتكامل", layout="wide")
st.markdown("""
<style>
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; }
    .card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 15px; background-color: #fcfcfc; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .sidebar-title { text-align: center; color: #2E4053; }
</style>
""", unsafe_allow_html=True)

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.markdown("<h2 class='sidebar-title'>📂 أرشيف الوثائق</h2>", unsafe_allow_html=True)
    st.write("---")
    if st.button("🏠 الصفحة الرئيسية"): st.session_state['menu_option'] = 'الرئيسية'
    if st.button("➕ إضافة مستند جديد"): st.session_state['menu_option'] = 'إضافة'
    if st.button("🔍 البحث والإدارة"): st.session_state['menu_option'] = 'بحث'
    if st.button("📊 عرض سجل الأرشيف"): st.session_state['menu_option'] = 'عرض'

# --- 5. منطق الصفحات ---

# أ. الصفحة الرئيسية
if st.session_state['menu_option'] == 'الرئيسية':
    st.title("مرحباً بك في نظام الأرشفة الذكي")
    data = st.session_state['archive_data']
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الوثائق", len(data))
    c2.metric("أرشفة اليوم", sum(1 for d in data if str(d.get('تاريخ_الأرشفة')) == str(date.today())))
    c3.metric("حالة النظام", "متصل")

# ب. إضافة مستند
elif st.session_state['menu_option'] == 'إضافة':
    st.header("➕ أرشفة مستند جديد")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            subject = st.text_input("موضوع المستند")
            doc_type = st.selectbox("نوع المستند", ["كتاب رسمي", "قرار", "تعميم", "عقد", "أخرى"])
            sender = st.text_input("الجهة المرسلة")
        with col2:
            receiver = st.text_input("الجهة المستلمة")
            doc_date = st.date_input("تاريخ المستند", value=date.today())
            tags = st.text_input("الكلمات المفتاحية")
        
        uploaded_files = st.file_uploader("📂 ارفع الوثائق (PDF أو صور)", accept_multiple_files=True)
        
        if st.form_submit_button("حفظ وأرشفة"):
            if subject and sender:
                file_list = []
                if uploaded_files:
                    for f in uploaded_files:
                        f_path = os.path.join(UPLOAD_DIR, f.name)
                        with open(f_path, "wb") as file_save:
                            file_save.write(f.getbuffer())
                        file_list.append(f.name)
                
                new_entry = {
                    "الموضوع": subject, "النوع": doc_type, "المرسل": sender,
                    "المستلم": receiver, "تاريخ_المستند": str(doc_date),
                    "الوسوم": tags, "المرفقات": ";".join(file_list),
                    "تاريخ_الأرشفة": str(date.today())
                }
                st.session_state['archive_data'].append(new_entry)
                save_data(st.session_state['archive_data'])
                st.success("✅ تم حفظ المستند والملفات بنجاح!")
            else:
                st.error("⚠️ يرجى ملء الحقول الأساسية (الموضوع والمرسل)")

# ج. البحث والإدارة (مع زر المعاينة)
elif st.session_state['menu_option'] == 'بحث':
    st.header("🔍 البحث والإدارة")
    query = st.text_input("ابحث عن موضوع، مرسل، أو كلمة دلالية...")
    
    data = st.session_state['archive_data']
    for idx, item in enumerate(data):
        if query.lower() in item['الموضوع'].lower() or query.lower() in item['المرسل'].lower():
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <b>📄 الموضوع:</b> {item['الموضوع']} | <b>🏢 الجهة:</b> {item['المرسل']}<br>
                    <b>📅 التاريخ:</b> {item['تاريخ_المستند']} | <b>📂 الملفات:</b> {item.get('المرفقات', 'لا يوجد')}
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3, c4 = st.columns([1, 1, 1, 3])
                
                # زر المعاينة
                if item.get('المرفقات'):
                    if c1.button("👁️ معاينة", key=f"v_{idx}"):
                        first_file = item['المرفقات'].split(';')[0]
                        display_file(os.path.join(UPLOAD_DIR, first_file))
                
                # زر الحذف
                if c2.button("🗑️ حذف", key=f"d_{idx}"):
                    st.session_state['archive_data'].pop(idx)
                    save_data(st.session_state['archive_data'])
                    st.rerun()

                # زر التعديل
                with c3.expander("✏️ تعديل"):
                    new_subj = st.text_input("تغيير الموضوع", value=item['الموضوع'], key=f"e_{idx}")
                    if st.button("حفظ", key=f"s_{idx}"):
                        st.session_state['archive_data'][idx]['الموضوع'] = new_subj
                        save_data(st.session_state['archive_data'])
                        st.rerun()

# د. عرض سجل الأرشيف
elif st.session_state['menu_option'] == 'عرض':
    st.header("📊 السجل العام")
    if st.session_state['archive_data']:
        df = pd.DataFrame(st.session_state['archive_data'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("الأرشيف فارغ.")
