import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# --- 1. الإعدادات والربط السحابي (مكتب إشبيلية) ---
# التأكد من وجود بيانات الحساب في Secrets
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    # بناء خدمة Google Drive مع دعم المجلدات المشتركة
    drive_service = build('drive', 'v3', credentials=credentials)
else:
    st.error("⚠️ لم يتم العثور على إعدادات Secrets. يرجى لصق بيانات JSON في إعدادات Streamlit.")

# معرف المجلد الجديد الذي أنشأته (Seville_Archive_V2)
FOLDER_ID = "1i0ziiky_QsBPXjaM6RexlEOXDTY9Zg1D" 

# --- 2. نظام التحقق من الدخول ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 نظام أرشفة مكتب إشبيلية العلمي</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("كلمة المرور:", type="password")
        if st.button("دخول", use_container_width=True):
            if pwd == st.secrets.get("password", "admin123"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة")
else:
    # --- 3. واجهة البرنامج الرئيسية ---
    st.sidebar.title("⭐ مكتب إشبيلية")
    st.sidebar.write("نظام الأرشفة الإلكتروني")
    menu = st.sidebar.radio("القائمة:", ["📥 إضافة وثيقة جديدة", "🔍 استعراض الأرشيف"])

    # --- قسم رفع الملفات ---
    if menu == "📥 إضافة وثيقة جديدة":
        st.header("📝 أرشفة مستند جديد")
        with st.form("upload_form", clear_on_submit=True):
            doc_name = st.text_input("عنوان الوثيقة")
            doc_type = st.selectbox("التصنيف", ["وارد", "صادر", "تسجيل دواء", "حسابات", "أخرى"])
            uploaded_file = st.file_uploader("اختر الملف", type=['pdf', 'png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("رفع إلى Google Drive ✅"):
                if uploaded_file and doc_name:
                    try:
                        file_metadata = {
                            'name': f"{doc_type}_{doc_name}_{datetime.now().strftime('%Y-%m-%d')}",
                            'parents': [FOLDER_ID]
                        }
                        
                        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.read()), 
                                                 mimetype=uploaded_file.type)

                        # الحل النهائي: الرفع مع دعم جميع أنواع المجلدات
                        file = drive_service.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id',
                            supportsAllDrives=True 
                        ).execute()
                        
                        st.success("✅ تم الرفع بنجاح لمجلد إشبيلية الجديد!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ فشل الرفع: {e}")

    # --- قسم استعراض الملفات ---
    elif menu == "🔍 استعراض الأرشيف":
        st.header("📂 المستندات الحالية")
        if st.button("تحديث القائمة 🔄"):
            try:
                results = drive_service.files().list(
                    q=f"'{FOLDER_ID}' in parents and trashed = false",
                    fields="files(id, name, webViewLink)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                items = results.get('files', [])
                for item in items:
                    col1, col2 = st.columns([4, 1])
                    col1.write(f"📄 {item['name']}")
                    col2.markdown(f"[🔗 عرض]({item['webViewLink']})")
                    st.divider()
            except Exception as e:
                st.error(f"تعذر جلب البيانات: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("إدارة مكتب إشبيلية العلمي - 2026")
