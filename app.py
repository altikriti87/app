import streamlit as st
import pandas as pd
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة المطور", layout="wide")

# 2. تهيئة البيانات
if 'archive_data' not in st.session_state:
    st.session_state['archive_data'] = []

if 'menu_option' not in st.session_state:
    st.session_state['menu_option'] = 'الرئيسية'

# 3. دالة لحذف مستند
def delete_document(index):
    st.session_state['archive_data'].pop(index)
    st.rerun()

# 4. دالة لتحديث مستند (بشكل مبسط)
def update_document(index, new_data):
    st.session_state['archive_data'][index] = new_data
    st.success("تم تحديث البيانات بنجاح")

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("🗄️ الأرشفة الإلكترونية")
    if st.button("🏠 الرئيسية"): st.session_state['menu_option'] = 'الرئيسية'
    if st.button("➕ إضافة مستند"): st.session_state['menu_option'] = 'إضافة'
    if st.button("🔍 البحث والإدارة"): st.session_state['menu_option'] = 'بحث'
    if st.button("📊 عرض الكل"): st.session_state['menu_option'] = 'عرض'

# --- المحتوى الرئيسي ---

# صفحة الإضافة (كما هي مع تعديل بسيط)
if st.session_state['menu_option'] == 'إضافة':
    st.header("➕ إضافة مستند جديد")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            subject = st.text_input("الموضوع")
            doc_type = st.selectbox("النوع", ["كتاب رسمي", "قرار", "تعميم"])
        with col2:
            sender = st.text_input("المرسل")
            doc_date = st.date_input("التاريخ", value=date.today())
        
        uploaded_files = st.file_uploader("رفع الوثائق", accept_multiple_files=True)
        if st.form_submit_button("حفظ"):
            file_names = [f.name for f in uploaded_files] if uploaded_files else []
            entry = {
                "الموضوع": subject, "النوع": doc_type, "المرسل": sender,
                "التاريخ": str(doc_date), "المرفقات": file_names
            }
            st.session_state['archive_data'].append(entry)
            st.success("تم الحفظ")

# صفحة البحث والإدارة (الميزات الجديدة هنا)
elif st.session_state['menu_option'] == 'بحث':
    st.header("🔍 البحث والإدارة (تعديل / حذف / عرض)")
    
    search_query = st.text_input("ابحث عن موضوع أو مرسل...")
    
    if st.session_state['archive_data']:
        # فلترة البيانات بناءً على البحث
        for idx, item in enumerate(st.session_state['archive_data']):
            if search_query.lower() in item['الموضوع'].lower() or search_query.lower() in item['المرسل'].lower():
                
                # إنشاء حاوية لكل مستند (Bordered Container)
                with st.container(border=True):
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.subheader(f"📄 {item['الموضوع']}")
                        st.write(f"**المرسل:** {item['المرسل']} | **التاريخ:** {item['التاريخ']} | **النوع:** {item['النوع']}")
                        
                        # عرض المرفقات
                        if item['المرفقات']:
                            st.write(f"📂 **المرفقات ({len(item['المرفقات'])}):** {', '.join(item['المرفقات'])}")
                        else:
                            st.write("📂 **المرفقات:** لا توجد")

                    with col_actions:
                        # أزرار العمليات
                        if st.button("🗑️ حذف", key=f"del_{idx}"):
                            delete_document(idx)
                        
                        # التعديل (فتح نافذة منبثقة بسيطة)
                        with st.expander("✏️ تعديل"):
                            new_subj = st.text_input("الموضوع الجديد", value=item['الموضوع'], key=f"edit_sub_{idx}")
                            new_send = st.text_input("المرسل الجديد", value=item['المرسل'], key=f"edit_send_{idx}")
                            if st.button("حفظ التغييرات", key=f"save_{idx}"):
                                item['الموضوع'] = new_subj
                                item['المرسل'] = new_send
                                st.rerun()

    else:
        st.info("لا توجد بيانات حالياً.")

# صفحة عرض الكل
elif st.session_state['menu_option'] == 'عرض':
    st.header("📊 سجل الأرشفة")
    if st.session_state['archive_data']:
        st.table(st.session_state['archive_data'])
