import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق الظاهري (CSS) ---
st.set_page_config(
    page_title="EDMS - نظام إدارة الوثائق",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تنسيق مخصص ليطابق ألوان الأنظمة المؤسسية (رمادي، أزرق داكن، أبيض)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stDataFrame { background-color: white; padding: 10px; border-radius: 5px; }
    [data-testid="stHeader"] { background-color: #ffffff; border-bottom: 2px solid #4e73df; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: bold; }
    /* تنسيق بطاقة عرض البيانات */
    .data-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border-right: 5px solid #4e73df;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .data-card h4 { color: #4e73df; margin-top: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام تسجيل الدخول ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        st.write("")
        with st.container(border=True):
            st.title("🔐 تسجيل الدخول")
            user = st.text_input("اسم المستخدم")
            pw = st.text_input("كلمة المرور", type="password")
            if st.button("دخول للنظام"):
                if user == "admin" and pw == "admin":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
    st.stop()

# --- 3. إدارة الملفات وقاعدة البيانات ---
ATTACH_DIR = "attachments"
if not os.path.exists(ATTACH_DIR): os.makedirs(ATTACH_DIR)
DB_FILE = "edms_archive.csv"

# الحقول الأساسية للنظام
COLUMNS = ["الرقم التسلسلي", "رقم المستند", "تاريخ الأرشفة", "الجهة الواردة (Incoming)", "الجهة المصدرة (Outgoing)", "الموضوع", "الكلمات المفتاحية", "اسم المرفق"]

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=COLUMNS)

# لإفراغ الحقول بعد الحفظ
if "form_count" not in st.session_state:
    st.session_state.form_count = 0

# --- 4. الهيكل الرئيسي (Header) ---
st.title("📂 EDMS - Correspondence File Cabinet")
st.write(f"المستخدم الحالي: **admin** | التاريخ: {datetime.now().strftime('%Y/%d/%m')}")

with st.sidebar:
    st.header("⚙️ الإعدادات")
    if st.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. استعراض الأرشيف (قائمة الوثائق) ---
df = load_data()

st.markdown("---")
col_search, col_export = st.columns([3, 1])
with col_search:
    search_query = st.text_input("🔍 بحث سريع في خزانة الملفات (Search File Cabinet)...")
with col_export:
    if not df.empty:
        # تصدير للإكسل
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Archive')
        st.download_button(label="📥 تصدير الكل إلى Excel", data=output.getvalue(), file_name="archive_export.xlsx")

# تصفية البيانات بناءً على البحث
if search_query:
    display_df = df[df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]
else:
    display_df = df

st.dataframe(display_df, use_container_width=True, hide_index=True)

# --- 6. إدارة وثيقة محددة (عرض وتعديل) ---
if not df.empty:
    st.markdown("---")
    st.subheader("🛠️ إدارة وتحرير وثيقة مختارة")
    selected_sn = st.selectbox("اختر الرقم التسلسلي للبدء:", ["---"] + df["الرقم التسلسلي"].tolist())

    if selected_sn != "---":
        row = df[df["الرقم التسلسلي"] == selected_sn].iloc[0]
        c_details, c_edit = st.columns([1, 1.5])

        with c_details:
            st.markdown(f"""
            <div class="data-card">
                <h4>📄 تفاصيل المستند</h4>
                <b>رقم السجل:</b> {selected_sn}<br>
                <b>رقم الوثيقة:</b> {row['رقم المستند']}<br>
                <b>الموضوع:</b> {row['الموضوع']}<br>
                <b>الوارد من:</b> {row['الجهة الواردة (Incoming)']}<br>
                <b>الصادر إلى:</b> {row['الجهة المصدرة (Outgoing)']}<br>
            </div>
            """, unsafe_allow_html=True)
            
            # أزرار الإجراءات
            if row['اسم المرفق'] != "لا يوجد":
                file_path = os.path.join(ATTACH_DIR, row['اسم المرفق'])
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        st.download_button("📥 تحميل/فتح المرفق", f, file_name=row['اسم المرفق'])
            
            if st.button("🗑️ حذف السجل نهائياً"):
                df = df[df["الرقم التسلسلي"] != selected_sn]
                df.to_csv(DB_FILE, index=False)
                st.success("تم الحذف!"); st.rerun()

        with c_edit:
            with st.expander("✏️ تعديل بيانات السجل"):
                with st.form("edit_entry"):
                    new_doc = st.text_input("تعديل رقم المستند", value=row['رقم المستند'])
                    new_sub = st.text_input("تعديل الموضوع", value=row['الموضوع'])
                    new_inc = st.text_input("تعديل الجهة الواردة", value=row['الجهة الواردة (Incoming)'])
                    new_out = st.text_input("تعديل الجهة المصدرة", value=row['الجهة المصدرة (Outgoing)'])
                    new_key = st.text_input("تعديل الكلمات المفتاحية", value=row['الكلمات المفتاحية'])
                    
                    if st.form_submit_button("تحديث البيانات"):
                        df.loc[df["الرقم التسلسلي"] == selected_sn, ["رقم المستند", "الموضوع", "الجهة الواردة (Incoming)", "الجهة المصدرة (Outgoing)", "الكلمات المفتاحية"]] = [new_doc, new_sub, new_inc, new_out, new_key]
                        df.to_csv(DB_FILE, index=False)
                        st.success("✅ تم التحديث بنجاح"); st.rerun()

# --- 7. إضافة وثيقة جديدة (صادر / وارد) ---
st.markdown("---")
with st.expander("➕ إضافة وثيقة جديدة للأرشيف", expanded=False):
    fc = st.session_state.form_count
    with st.form("new_archive_form"):
        col1, col2 = st.columns(2)
        with col1:
            in_doc_no = st.text_input("رقم المستند", key=f"d_{fc}")
            in_inc = st.text_input("الجهة الواردة (Incoming)", key=f"i_{fc}")
            in_sub = st.text_input("الموضوع", key=f"s_{fc}")
        with col2:
            in_out = st.text_input("الجهة المصدرة (Outgoing)", key=f"o_{fc}")
            in_key = st.text_input("الكلمات المفتاحية", key=f"k_{fc}")
            in_file = st.file_uploader("رفع المرفق", key=f"f_{fc}")

        if st.form_submit_button("إرسال للأرشفة"):
            if in_doc_no and in_sub:
                sn = f"EDMS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                fname = "لا يوجد"
                if in_file:
                    fname = f"{sn}_{in_file.name}"
                    with open(os.path.join(ATTACH_DIR, fname), "wb") as f: f.write(in_file.getbuffer())
                
                new_row = [sn, in_doc_no, datetime.now().strftime("%Y/%d/%m"), in_inc, in_out, in_sub, in_key, fname]
                df.loc[len(df)] = new_row
                df.to_csv(DB_FILE, index=False)
                
                st.success(f"✅ تمت الأرشفة بنجاح! السجل: {sn}")
                st.session_state.form_count += 1
                st.rerun()
            else:
                st.warning("⚠️ يرجى ملء الحقول الإلزامية")
