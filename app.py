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

# ضع هنا الـ ID الجديد للمجلد الجديد الذي أنشأته للتو
FOLDER_ID = "ضع_الرقم_التعريفي_الجديد_هنا" 

# --- 2. التحقق من الدخول ---
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
            doc_name = st.text_input("اسم الوثيقة")
            doc_type = st.selectbox("التصنيف", ["وارد", "صادر", "تسجيل", "أخرى"])
            uploaded_file = st.file_uploader("اختر الملف", type=['pdf', 'png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("رفع ✅"):
                if uploaded_file and doc_name:
                    try:
                        file_metadata = {
                            'name': f"{doc_type}_{doc_name}_{datetime.now().strftime('%Y-%m-%d')}",
                            'parents': [FOLDER_ID]
                        }
                        
                        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.read()), 
                                                 mimetype=uploaded_file.type)

                        # إرسال الطلب مع دعم المساحات المشتركة بشكل إلزامي
                        file = drive_service.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id',
                            supportsAllDrives=True  # هذا السطر ضروري جداً
                        ).execute()
                        
                        st.success("✅ تم الرفع بنجاح!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ فشل الرفع: {e}")

    elif menu == "🔍 استعراض الأرشيف":
        st.header("📂 الملفات الحالية")
        if st.button("تحديث 🔄"):
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
            except Exception as e:
                st.error(f"فشل جلب الملفات: {e}")
