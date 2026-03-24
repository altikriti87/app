import streamlit as st
import pandas as pd
import os
import io
import shutil
import zipfile
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق (CSS) لنمط المؤسسات ---
st.set_page_config(
    page_title="EDMS - Correspondence System",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    .stDataFrame { background-color: white; padding: 10px; border-radius: 8px; border: 1px solid #e3e6f0; }
    [data-testid="stHeader"] { background-color: #ffffff; border-bottom: 3px solid #4e73df; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    .data-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-right: 6px solid #4e73df;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .data-card h4 { color: #4e73df; margin-top: 0; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
    .sidebar-title { color: #ffffff; font-weight: bold; font-size: 1.2rem; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام تسجيل الدخول ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
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
                    st.error("❌ البيانات غير صحيحة")
    st.stop()

# --- 3. تهيئة قاعدة البيانات والمجلدات ---
ATTACH_DIR = "attachments"
if not os.path.exists(ATTACH_DIR): os.makedirs(ATTACH_DIR)
DB_FILE = "edms_master_db.csv"

COLUMNS = ["الرقم التسلسلي", "رقم المستند", "تاريخ الأرشفة", "الجهة الواردة (Incoming)", "الجهة المصدرة (Outgoing)", "الموضوع", "الكلمات المفتاحية", "اسم المرفق"]

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=COLUMNS)

if "form_count" not in st.session_state:
    st.session_state.form_count = 0

df = load_data()

# --- 4. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>📂 EDMS - FILE CABINET</div>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("القائمة الرئيسية", ["لوحة التحكم (Dashboard)", "أرشفة صادر/وارد جديد", "النسخ الاحتياطي والاسترجاع"])
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. صفحة لوحة التحكم واستعراض الملفات (Dashboard) ---
if menu == "لوحة التحكم (Dashboard)":
    st.title("📊 خزانة ملفات الصادر والوارد")
    
    # بطاقات إحصائية سريعة
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الوثائق", len(df))
    c2.metric("وثائق اليوم", len(df[df["تاريخ الأرشفة"] == datetime.now().strftime("%Y/%d/%m")]))
    c3.metric("الملفات المرفقة", len(df[df["اسم المرفق"] != "لا يوجد"]))

    st.markdown("---")
    
    # محرك البحث والتصدير
    col_s, col_e = st.columns([3, 1])
    with col_s:
        search_query = st.text_input("🔍 ابحث في الخزانة (رقم، جهة، موضوع، كلمات)...")
    with col_e:
        if not df.empty:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                df.to_excel(wr, index=False, sheet_name='Archive')
            st.download_button("📥 تصدير Excel", buf.getvalue(), "Archive_Export.xlsx")

    # تصفية الجدول
    filtered_df = df[df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)] if search_query else df
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # إدارة السجل المختار
    if not df.empty:
        st.subheader("🛠️ إجراءات على الوثيقة")
        selected_sn = st.selectbox("اختر الرقم التسلسلي لإدارة الوثيقة:", ["---"] + df["الرقم التسلسلي"].tolist())
        
        if selected_sn != "---":
            row = df[df["الرقم التسلسلي"] == selected_sn].iloc[0]
            col_det, col_edit = st.columns([1, 1.5])

            with col_det:
                st.markdown(f"""
                <div class="data-card">
                    <h4>📄 معاينة البيانات</h4>
                    <b>الرقم التسلسلي:</b> {selected_sn}<br>
                    <b>رقم الوثيقة:</b> {row['رقم المستند']}<br>
                    <b>الموضوع:</b> {row['الموضوع']}<br>
                    <b>تاريخ الحفظ:</b> {row['تاريخ الأرشفة']}
                </div>
                """, unsafe_allow_html=True)
                
                if row['اسم المرفق'] != "لا يوجد":
                    fpath = os.path.join(ATTACH_DIR, row['اسم المرفق'])
                    if os.path.exists(fpath):
                        with open(fpath, "rb") as f:
                            st.download_button("📥 تحميل المرفق الأصلي", f, file_name=row['اسم المرفق'])
                
                if st.button("🗑️ حذف السجل نهائياً"):
                    df = df[df["الرقم التسلسلي"] != selected_sn]
                    df.to_csv(DB_FILE, index=False)
                    st.success("تم الحذف بنجاح"); st.rerun()

            with col_edit:
                with st.expander("✏️ تحرير البيانات"):
                    with st.form("edit_form"):
                        e_doc = st.text_input("رقم المستند", row['رقم المستند'])
                        e_sub = st.text_input("الموضوع", row['الموضوع'])
                        e_inc = st.text_input("الجهة الواردة", row['الجهة الواردة (Incoming)'])
                        e_out = st.text_input("الجهة المصدرة", row['الجهة المصدرة (Outgoing)'])
                        e_key = st.text_input("الكلمات المفتاحية", row['الكلمات المفتاحية'])
                        if st.form_submit_button("حفظ التعديلات"):
                            df.loc[df["الرقم التسلسلي"] == selected_sn, ["رقم المستند", "الموضوع", "الجهة الواردة (Incoming)", "الجهة المصدرة (Outgoing)", "الكلمات المفتاحية"]] = [e_doc, e_sub, e_inc, e_out, e_key]
                            df.to_csv(DB_FILE, index=False)
                            st.success("تم التحديث!"); st.rerun()

# --- 6. صفحة إضافة وثيقة جديدة ---
elif menu == "أرشفة صادر/وارد جديد":
    st.title("➕ تسجيل وثيقة جديدة")
    count = st.session_state.form_count
    
    with st.container(border=True):
        with st.form("new_entry_form"):
            c1, c2 = st.columns(2)
            with c1:
                n_doc = st.text_input("رقم المستند (الورقي)", key=f"d_{count}")
                n_inc = st.text_input("الجهة الواردة (Incoming)", key=f"i_{count}")
                n_sub = st.text_input("الموضوع الرئيسي", key=f"s_{count}")
            with c2:
                n_out = st.text_input("الجهة المصدرة (Outgoing)", key=f"o_{count}")
                n_key = st.text_input("الكلمات المفتاحية البحثية", key=f"k_{count}")
                n_file = st.file_uploader("رفع صورة/ملف الوثيقة", key=f"f_{count}")
            
            if st.form_submit_button("حفظ في الأرشيف"):
                if n_doc and n_sub:
                    sn = f"EDMS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    fname = "لا يوجد"
                    if n_file:
                        fname = f"{sn}_{n_file.name}"
                        with open(os.path.join(ATTACH_DIR, fname), "wb") as f: f.write(n_file.getbuffer())
                    
                    new_row = [sn, n_doc, datetime.now().strftime("%Y/%d/%m"), n_inc, n_out, n_sub, n_key, fname]
                    df.loc[len(df)] = new_row
                    df.to_csv(DB_FILE, index=False)
                    st.success(f"✅ تمت الأرشفة بنجاح! رقم القيد: {sn}")
                    st.session_state.form_count += 1
                    st.rerun()
                else:
                    st.warning("⚠️ رقم المستند والموضوع حقول إلزامية")

# --- 7. صفحة النسخ الاحتياطي والاسترجاع ---
elif menu == "النسخ الاحتياطي والاسترجاع":
    st.title("💾 إدارة قاعدة البيانات")
    
    col_b, col_r = st.columns(2)
    
    with col_b:
        st.subheader("📤 تصدير نسخة احتياطية")
        st.info("سيتم ضغط الأرشيف النصي مع كافة المرفقات في ملف واحد.")
        if st.button("إنشاء ملف Backup"):
            b_name = f"EDMS_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.make_archive(b_name, 'zip', ".", "attachments")
            with zipfile.ZipFile(f"{b_name}.zip", 'a') as z:
                if os.path.exists(DB_FILE): z.write(DB_FILE)
            
            with open(f"{b_name}.zip", "rb") as f:
                st.download_button("📥 تحميل النسخة الاحتياطية", f, file_name=f"{b_name}.zip")

    with col_r:
        st.subheader("📥 استرجاع نسخة احتياطية")
        st.error("تنبيه: هذا الإجراء سيمسح البيانات الحالية ويستبدلها بالقديمة!")
        up_zip = st.file_uploader("ارفع ملف الـ ZIP الاحتياطي", type="zip")
        if st.button("بدء الاسترجاع"):
            if up_zip:
                with zipfile.ZipFile(up_zip, 'r') as zr:
                    zr.extractall(".")
                st.success("✅ تم الاسترجاع بنجاح! أعد تحميل الصفحة.")
                st.rerun()
