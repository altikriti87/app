import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق الظاهري (CSS) ---
st.set_page_config(
    page_title="OTAS - نظام الأرشفة الذكي",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق مخصص ليطابق ألوان وتصميم الـ Admin Dashboards
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    [data-testid="stSidebar"] { background-color: #1e2d3b; border-right: 1px solid #e0e0e0; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stMetric { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 4px solid #007bff; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; border-radius: 5px; height: 3em; }
    .stDataFrame { background-color: white; border-radius: 8px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام التحقق من الهوية (Login) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("") # فراغ علوي
        st.write("")
        with st.container(border=True):
            st.title("🔐 OTAS Login")
            user = st.text_input("اسم المستخدم (Username)")
            pw = st.text_input("كلمة المرور (Password)", type="password")
            if st.button("دخول للنظام"):
                if user == "admin" and pw == "admin":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ خطأ في اسم المستخدم أو كلمة المرور")
    st.stop()

# --- 3. إدارة الملفات وقاعدة البيانات ---
ATTACH_DIR = "attachments"
if not os.path.exists(ATTACH_DIR): os.makedirs(ATTACH_DIR)
DB_FILE = "archive_data.csv"

def load_data():
    if os.path.exists(DB_FILE): 
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["الرقم التسلسلي", "رقم المستند", "الجهة الواردة", "الجهة المصدرة", "الموضوع", "الكلمات المفتاحية", "تاريخ الأرشفة", "اسم المرفق"])

# متغير لتغيير مفاتيح الإدخال وتفريغها بعد الحفظ
if "form_count" not in st.session_state:
    st.session_state.form_count = 0

# --- 4. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("### 🏢 المكتب العلمي لشبيبة")
    st.markdown("---")
    menu = st.radio(
        "القائمة الرئيسية",
        ["لوحة التحكم (Dashboard)", "استعراض الأرشيف", "إضافة مستند جديد", "تصدير البيانات"],
        index=0
    )
    st.markdown("---")
    if st.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

# استدعاء البيانات
df = load_data()

# --- 5. صفحة لوحة التحكم (Dashboard) ---
if menu == "لوحة التحكم (Dashboard)":
    st.title("📊 Admin Dashboard")
    st.write(f"مرحباً بك، **Admin** | تاريخ اليوم: {datetime.now().strftime('%Y/%d/%m')}")
    
    # بطاقات الإحصائيات مثل الصورة
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("إجمالي الأرشيف", len(df))
    with col2: st.metric("جهات واردة", df["الجهة الواردة"].nunique())
    with col3: st.metric("جهات مصدرة", df["الجهة المصدرة"].nunique())
    with col4: st.metric("مرفقات مخزنة", len(df[df["اسم المرفق"] != "لا يوجد"]))
    
    st.markdown("---")
    st.subheader("📝 آخر 5 وثائق تمت أرشفتها")
    if not df.empty:
        st.table(df.tail(5)[["الرقم التسلسلي", "رقم المستند", "الموضوع", "تاريخ الأرشفة"]])
    else:
        st.info("لا توجد بيانات حالياً.")

# --- 6. صفحة استعراض الأرشيف (إدارة وتعديل وحذف) ---
elif menu == "استعراض الأرشيف":
    st.title("📂 قائمة الأرشيف - Management")
    
    search = st.text_input("🔍 ابحث في الأرشيف (بالموضوع، الرقم، أو الكلمات المفتاحية):")
    if search:
        filtered_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    else:
        filtered_df = df
        
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("🛠️ خيارات الإدارة")
    if not df.empty:
        selected_sn = st.selectbox("اختر الرقم التسلسلي للوثيقة للتحكم بها:", ["---"] + df["الرقم التسلسلي"].tolist())
        
        if selected_sn != "---":
            row = df[df["الرقم التسلسلي"] == selected_sn].iloc[0]
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.info(f"📍 الوثيقة المختارة: {selected_sn}")
                # زر عرض المرفق
                if row['اسم المرفق'] != "لا يوجد":
                    file_path = os.path.join(ATTACH_DIR, row['اسم المرفق'])
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button("📥 تحميل المرفق", f, file_name=row['اسم المرفق'])
                
                # زر الحذف
                if st.button("🗑️ حذف الوثيقة نهائياً"):
                    new_df = df[df["الرقم التسلسلي"] != selected_sn]
                    new_df.to_csv(DB_FILE, index=False)
                    if row['اسم المرفق'] != "لا يوجد":
                        try: os.remove(os.path.join(ATTACH_DIR, row['اسم المرفق']))
                        except: pass
                    st.warning("تم حذف الوثيقة!"); st.rerun()

            with c2:
                with st.form("edit_form"):
                    st.write("✏️ تعديل بيانات الوثيقة:")
                    en_doc_no = st.text_input("رقم المستند الجديد", value=row['رقم المستند'])
                    en_subj = st.text_input("الموضوع الجديد", value=row['الموضوع'])
                    en_inc = st.text_input("الجهة الواردة الجديدة", value=row['الجهة الواردة'])
                    en_out = st.text_input("الجهة المصدرة الجديدة", value=row['الجهة المصدرة'])
                    en_keys = st.text_input("الكلمات المفتاحية الجديدة", value=row['الكلمات المفتاحية'])
                    
                    if st.form_submit_button("تحديث السجل"):
                        df.loc[df["الرقم التسلسلي"] == selected_sn, ["رقم المستند", "الموضوع", "الجهة الواردة", "الجهة المصدرة", "الكلمات المفتاحية"]] = [en_doc_no, en_subj, en_inc, en_out, en_keys]
                        df.to_csv(DB_FILE, index=False)
                        st.success("تم التحديث بنجاح!"); st.rerun()

# --- 7. صفحة إضافة مستند جديد (تفريغ تلقائي) ---
elif menu == "إضافة مستند جديد":
    st.title("➕ أرشفة مستند جديد")
    fc = st.session_state.form_count
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            doc_no = st.text_input("رقم المستند (على الورقة)", key=f"doc_{fc}")
            inc_e = st.text_input("الجهة الواردة", key=f"inc_{fc}")
            out_e = st.text_input("الجهة المصدرة", key=f"out_{fc}")
        with col2:
            subj = st.text_input("الموضوع الرئيسي", key=f"sub_{fc}")
            keyw = st.text_input("الكلمات المفتاحية (لفصلها استخدم فاصلة)", key=f"key_{fc}")
            file = st.file_uploader("ارفق الوثيقة (PDF/Images)", key=f"file_{fc}")

        if st.button("حفظ الأرشفة وتفريغ الحقول"):
            if doc_no and subj:
                sn = f"ARC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                fname = "لا يوجد"
                if file:
                    fname = f"{sn}_{file.name}"
                    with open(os.path.join(ATTACH_DIR, fname), "wb") as f: f.write(file.getbuffer())
                
                new_row = [sn, doc_no, inc_e, out_e, subj, keyw, datetime.now().strftime("%Y/%d/%m"), fname]
                df.loc[len(df)] = new_row
                df.to_csv(DB_FILE, index=False)
                
                st.success(f"✅ تم الحفظ! الرقم التسلسلي: {sn}")
                st.session_state.form_count += 1
                st.rerun()
            else:
                st.warning("⚠️ يرجى تعبئة الحقول الأساسية (رقم المستند والموضوع)")

# --- 8. صفحة تصدير البيانات (Excel) ---
elif menu == "تصدير البيانات":
    st.title("📤 تصدير قاعدة البيانات")
    st.write("يمكنك تحميل الأرشيف بالكامل كملف Excel للعمل عليه خارجياً.")
    if not df.empty:
        # تحويل البيانات لملف بافر
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Archive')
        
        st.download_button(
            label="📥 تحميل ملف Excel",
            data=buffer.getvalue(),
            file_name=f"Archive_Export_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.info("لا توجد بيانات لتصديرها.")
