import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات المسارات ---
EXCEL_FILE = "archive.xlsx"
ARCHIVE_FOLDER = "archive_files"

# إنشاء المجلدات إذا لم تكن موجودة
if not os.path.exists(ARCHIVE_FOLDER):
    os.makedirs(ARCHIVE_FOLDER)

# --- وظائف قاعدة البيانات ---
def load_data():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            "ID NO", "النوع", "رقم الوثيقة", "التاريخ", 
            "من", "إلى", "الموضوع", "الكلمات المفتاحية", "الملفات"
        ])
        df.to_excel(EXCEL_FILE, index=False)
        return df
    return pd.read_excel(EXCEL_FILE)

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

# --- نظام الحماية ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center;'>🔐 نظام أرشفة مكتب إشبيلية العلمي</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("أدخل كلمة المرور للدخول:", type="password")
            if st.button("تسجيل الدخول", use_container_width=True):
                if pwd == "admin123":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ كلمة المرور غير صحيحة")
        return False
    return True

# --- واجهة البرنامج ---
if check_password():
    st.sidebar.title("⭐ مكتب إشبيلية العلمي")
    st.sidebar.info("نظام الأرشفة الإلكترونية - الإصدار 1.0")
    
    menu = st.sidebar.radio("انتقل إلى:", ["🔍 البحث والأرشيف", "📥 إضافة وثيقة جديدة", "📊 إحصائيات"])

    df = load_data()

    # --- القسم الأول: البحث وعرض البيانات ---
    if menu == "🔍 البحث والأرشيف":
        st.header("🔍 البحث في الأرشيف")
        search_q = st.text_input("ابحث بالاسم، الرقم، أو الموضوع:")
        
        if search_q:
            results = df[df.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)]
        else:
            results = df

        st.write(f"عدد الوثائق الموجودة: {len(results)}")
        
        for index, row in results.sort_index(ascending=False).iterrows():
            with st.expander(f"📄 {row['النوع']} - رقم: {row['رقم الوثيقة']} ({row['الموضوع']})"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**تاريخ الوثيقة:** {row['التاريخ']}")
                    st.write(f"**من:** {row['من']}")
                with c2:
                    st.write(f"**إلى:** {row['إلى']}")
                    st.write(f"**الكلمات المفتاحية:** {row['الكلمات المفتاحية']}")
                
                # إدارة الملفات المرفقة
                if pd.notna(row['الملفات']) and row['الملفات'] != "":
                    st.write("---")
                    st.write("📎 **المرفقات:**")
                    files = str(row['الملفات']).split(";")
                    for f_name in files:
                        f_path = os.path.join(ARCHIVE_FOLDER, f_name)
                        if os.path.exists(f_path):
                            with open(f_path, "rb") as f:
                                st.download_button(f"📥 تحميل {f_name}", f, file_name=f_name, key=f"{index}_{f_name}")

    # --- القسم الثاني: إضافة بيانات جديدة ---
    elif menu == "📥 إضافة وثيقة جديدة":
        st.header("📝 أرشفة وثيقة جديدة")
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                doc_type = st.selectbox("نوع الوثيقة", ["وارد", "صادر", "مستند داخلي"])
                doc_num = st.text_input("رقم الوثيقة الرسمي")
                doc_date = st.date_input("تاريخ الوثيقة")
            with col2:
                doc_from = st.text_input("جهة الإرسال (من)")
                doc_to = st.text_input("جهة الاستلام (إلى)")
                subject = st.text_input("موضوع الوثيقة")
            
            keywords = st.text_area("كلمات مفتاحية للبحث (مثال: اسم الدواء، الشركة)")
            uploaded_files = st.file_uploader("ارفق الوثائق (صور أو PDF)", accept_multiple_files=True)
            
            if st.form_submit_button("حفظ في الأرشيف ✅"):
                if doc_num and subject:
                    # حفظ الملفات المرفوعة
                    file_names_list = []
                    for uploaded_file in uploaded_files:
                        # إضافة طابع زمني لاسم الملف لمنع التكرار
                        unique_name = f"{datetime.now().strftime('%H%M%S')}_{uploaded_file.name}"
                        with open(os.path.join(ARCHIVE_FOLDER, unique_name), "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_names_list.append(unique_name)
                    
                    # إضافة السجل الجديد للاكسل
                    new_entry = {
                        "ID NO": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "النوع": doc_type,
                        "رقم الوثيقة": doc_num,
                        "التاريخ": doc_date.strftime("%Y-%m-%d"),
                        "من": doc_from,
                        "إلى": doc_to,
                        "الموضوع": subject,
                        "الكلمات المفتاحية": keywords,
                        "الملفات": ";".join(file_names_list)
                    }
                    
                    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                    save_data(df)
                    st.success(f"تمت أرشفة الوثيقة رقم {doc_num} بنجاح!")
                else:
                    st.error("يرجى إكمال البيانات الأساسية (الرقم والموضوع)")

    # --- القسم الثالث: إحصائيات سريعة ---
    elif menu == "📊 إحصائيات":
        st.header("📈 ملخص الأرشيف")
        if not df.empty:
            st.metric("إجمالي الوثائق المؤرشفة", len(df))
            st.write("توزيع الوثائق حسب النوع:")
            st.bar_chart(df["النوع"].value_count())
        else:
            st.info("الأرشيف فارغ حالياً.")

# تذييل الصفحة للمكتب
st.sidebar.markdown("---")
st.sidebar.caption("مكتب إشبيلية العلمي للدعاية الأدوية - بغداد")
