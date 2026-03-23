import streamlit as st
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="المكتب العلمي - أرشفة تجريبية", layout="wide")

# عنوان البرنامج
st.title("🧪 نظام الأرشفة التجريبي (بدون مكتبات معقدة)")
st.write("هذا الإصدار مخصص لاختبار عمل السيرفر فقط.")

# إنشاء مخزن بيانات مؤقت في الذاكرة
if 'data_archive' not in st.session_state:
    st.session_state.data_archive = []

# --- قسم إدخال البيانات ---
st.header("📥 أرشفة دواء جديد")
with st.form("archive_form"):
    col1, col2 = st.columns(2)
    with col1:
        drug_name = st.text_input("اسم الدواء")
        batch_no = st.text_input("رقم الوجبة (Batch No)")
    with col2:
        folder_name = st.selectbox("المجلد", ["أدوية عامة", "مستندات الوزارة", "عقود"])
        note = st.text_area("ملاحظات إضافية")
    
    submit = st.form_submit_button("حفظ في الأرشيف")

if submit:
    if drug_name:
        entry = {
            "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "اسم الدواء": drug_name,
            "الدفعة": batch_no,
            "المجلد": folder_name,
            "الملاحظات": note
        }
        st.session_state.data_archive.append(entry)
        st.success(f"تمت إضافة {drug_name} بنجاح!")
    else:
        st.error("يرجى كتابة اسم الدواء")

# --- قسم عرض البيانات ---
st.divider()
st.header("🔍 الأرشيف الحالي")
if st.session_state.data_archive:
    df = pd.DataFrame(st.session_state.data_archive)
    st.dataframe(df, use_container_width=True)
    
    # خيار تحميل البيانات كملف Excel بسيط (CSV)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("تحميل الأرشيف كملف Excel", data=csv, file_name="archive_test.csv", mime="text/csv")
else:
    st.info("الأرشيف فارغ حالياً. قم بإضافة بيانات من الأعلى.")
