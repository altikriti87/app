import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# --- 1. الإعدادات ---
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    drive_service = build('drive', 'v3', credentials=credentials)
else:
    st.error("⚠️ إعدادات Secrets غير موجودة!")

# معرف المجلد الجديد (V2)
FOLDER_ID = "1i0ziiky_QsBPXjaM6RexlEOXDTY9Zg1D" 

# --- 2. نظام الدخول ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 دخول نظام أرشفة إشبيلية</h2>", unsafe_allow_html=True)
    pwd = st.text_input("كلمة المرور:", type="password")
    if st.button("دخول"):
        if pwd == st.secrets.get("password", "admin123"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ خطأ!")
else:
    st.sidebar.title("⭐ مكتب إشبيلية")
    menu = st.sidebar.radio("القائمة:", ["📥 إضافة وثيقة", "🔍 استعراض الأرشيف"])

    if menu == "📥 إضافة وثيقة":
        st.header("📝 أرشفة وثيقة جديدة")
        with st.form("upload_form", clear_on_submit=True):
            doc_name = st.text_input("عنوان الوثيقة")
            doc_type = st.selectbox("التصنيف", ["وارد", "صادر", "تسجيل دواء", "حسابات", "أخرى"])
            uploaded_file = st.file_uploader("اختر الملف", type=['pdf', 'png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("رفع إلى Google Drive ✅"):
                if uploaded_file and doc_name:
                    try:
                        # تجهيز بيانات الملف
                        file_metadata = {
                            'name': f"{doc_type}_{doc_name}_{datetime.now().strftime('%Y-%m-%d')}",
                            'parents': [FOLDER_ID]
                        }
                        
                        # تحويل الملف لتدفق بيانات مع تحديد نوع الميم
                        media = MediaIoBaseUpload(
                            io.BytesIO(uploaded_file.read()), 
                            mimetype=uploaded_file.type,
                            resumable=True # هذا الخيار يقلل من مشاكل القيود
                        )

                        # تنفيذ الرفع مع دعم المساحات المشتركة
                        file = drive_service.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id',
                            supportsAllDrives=True 
                        ).execute()
                        
                        st.success("✅ تم الرفع بنجاح لمجلد إشبيلية!")
                        st.balloons()
                    except Exception as e:
                        if "storageQuotaExceeded" in str(e):
                            st.error("⚠️ جوجل لا تزال ترفض المساحة. يرجى مراجعة إعداد 'أيقونة الترس' في المجلد.")
                        else:
                            st.error(f"❌ فشل: {e}")

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
                st.error(f"حدث خطأ: {e}")
