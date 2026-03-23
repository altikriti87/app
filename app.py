import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# --- 1. إعدادات الاتصال بـ Google Drive لمكتب إشبيلية ---
# استدعاء البيانات السرية من Streamlit Secrets
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    # بناء الخدمة مع دعم المجلدات والمساحات المشتركة لتجنب أخطاء المساحة
    drive_service = build('drive', 'v3', credentials=credentials)
else:
    st.error("⚠️ لم يتم العثور على إعدادات Secrets. تأكد من لصق بيانات JSON في Streamlit.")

# المعرف الخاص بمجلد مكتب إشبيلية (الذي استخرجناه من الرابط)
FOLDER_ID = "1W2CXAqHbZSBl3PUi0EvOan9TgU3oF-DZ" 

# --- 2. نظام حماية الدخول ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center;'>🔐 نظام أرشفة مكتب إشبيلية العلمي</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("أدخل كلمة المرور للدخول:", type="password")
            if st.button("دخول", use_container_width=True):
                # نستخدم كلمة المرور من Secrets أو الافتراضية admin123
                if pwd == st.secrets.get("password", "admin123"):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ كلمة المرور غير صحيحة")
        return False
    return True

# --- 3. الواجهة الرئيسية واستخدام البرنامج ---
if check_password():
    st.sidebar.title("⭐ مكتب إشبيلية العلمي")
    st.sidebar.info("نظام الأرشفة السحابي المباشر")
    
    menu = st.sidebar.radio("القائمة:", ["📥 إضافة وثيقة جديدة", "🔍 استعراض الأرشيف"])

    # --- قسم رفع الملفات ---
    if menu == "📥 إضافة وثيقة جديدة":
        st.header("📝 أرشفة مستند جديد")
        
        with st.form("upload_form", clear_on_submit=True):
            doc_name = st.text_input("اسم الوثيقة أو الموضوع")
            doc_type = st.selectbox("تصنيف المستند", ["وارد", "صادر", "مستند تسجيل دواء", "حسابات", "أخرى"])
            uploaded_file = st.file_uploader("اختر الملف (PDF أو صورة)", type=['pdf', 'png', 'jpg', 'jpeg'])
            
            submit = st.form_submit_button("رفع إلى السحابة ✅")
            
            if submit:
                if uploaded_file is not None and doc_name:
                    try:
                        # تجهيز بيانات الملف (Metadata)
                        file_metadata = {
                            'name': f"{doc_type}_{doc_name}_{datetime.now().strftime('%Y-%m-%d')}",
                            'parents': [FOLDER_ID]
                        }
                        
                        # قراءة الملف كتدفق بيانات (Stream)
                        media = MediaIoBaseUpload(
                            io.BytesIO(uploaded_file.read()), 
                            mimetype=uploaded_file.type,
                            resumable=True
                        )
                        
                        # تنفيذ عملية الرفع (مع تفعيل خيار supportsAllDrives لحل مشكلة المساحة)
                        file = drive_service.files().create(
                            body=file_metadata, 
                            media_body=media, 
                            fields='id',
                            supportsAllDrives=True
                        ).execute()
                        
                        st.success(f"✅ تم الرفع بنجاح! الوثيقة الآن في مجلد Seville Archive.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء الرفع: {e}")
                else:
                    st.warning("يرجى ملء الاسم واختيار ملف أولاً.")

    # --- قسم استعراض الملفات ---
    elif menu == "🔍 استعراض الأرشيف":
        st.header("📂 ملفات الأرشيف الحالية")
        if st.button("تحديث القائمة 🔄"):
            try:
                # جلب الملفات من المجلد مع دعم المساحات المشتركة
                results = drive_service.files().list(
                    q=f"'{FOLDER_ID}' in parents and trashed = false",
                    fields="files(id, name, webViewLink, thumbnailLink)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                items = results.get('files', [])

                if not items:
                    st.info("المجلد فارغ حالياً.")
                else:
                    for item in items:
                        col1, col2 = st.columns([4, 1])
                        col1.write(f"📄 {item['name']}")
                        col2.markdown(f"[🔗 عرض]({item['webViewLink']})")
                        st.divider()
            except Exception as e:
                st.error(f"تعذر جلب البيانات من السحابة: {e}")

# تذييل البرنامج
st.sidebar.markdown("---")
st.sidebar.caption("مكتب إشبيلية العلمي للدعاية الأدوية - بغداد 2026")
