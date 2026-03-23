import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# --- 1. إعدادات الربط السحابي (Google Drive) ---
# جلب البيانات من Secrets في Streamlit
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    # بناء الخدمة مع دعم المجلدات والمساحات المشتركة
    drive_service = build('drive', 'v3', credentials=credentials)
else:
    st.error("⚠️ لم يتم العثور على إعدادات Secrets. تأكد من ضبطها في موقع Streamlit.")

# المعرف الخاص بمجلد مكتب إشبيلية (الذي استخرجناه سابقاً)
FOLDER_ID = "1W2CXAqHbZSBl3PUi0EvOan9TgU3oF-DZ" 

# --- 2. نظام التحقق من الدخول ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center;'>🔐 نظام أرشفة مكتب إشبيلية</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("أدخل كلمة المرور:", type="password")
            if st.button("دخول", use_container_width=True):
                # نستخدم admin123 ككلمة مرور افتراضية أو من Secrets
                if pwd == st.secrets.get("password", "admin123"):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ كلمة المرور غير صحيحة")
        return False
    return True

# --- 3. واجهة البرنامج الرئيسية ---
if check_password():
    st.sidebar.title("⭐ مكتب إشبيلية العلمي")
    st.sidebar.write("نظام الأرشفة السحابي")
    
    menu = st.sidebar.radio("القائمة:", ["📥 إضافة وثيقة جديدة", "🔍 استعراض الأرشيف"])

    # --- قسم رفع المستندات ---
    if menu == "📥 إضافة وثيقة جديدة":
        st.header("📝 أرشفة وثيقة جديدة")
        
        with st.form("upload_form", clear_on_submit=True):
            doc_name = st.text_input("عنوان الوثيقة (مثلاً: فاتورة، كتاب رسمي)")
            doc_type = st.selectbox("نوع الوثيقة", ["وارد", "صادر", "تسجيل دواء", "حسابات", "أخرى"])
            uploaded_file = st.file_uploader("اختر الملف (PDF أو صورة)", type=['pdf', 'png', 'jpg', 'jpeg'])
            
            submit = st.form_submit_button("رفع إلى Google Drive ✅")
            
            if submit:
                if uploaded_file is not None and doc_name:
                    try:
                        # إعداد بيانات الملف وتسميته بالتاريخ
                        file_metadata = {
                            'name': f"{doc_type}_{doc_name}_{datetime.now().strftime('%Y-%m-%d')}",
                            'parents': [FOLDER_ID]
                        }
                        
                        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.read()), 
                                                 mimetype=uploaded_file.type)
                        
                        # التنفيذ مع خاصية supportsAllDrives لحل مشكلة المساحة (Quota)
                        file = drive_service.files().create(
                            body=file_metadata, 
                            media_body=media, 
                            fields='id',
                            supportsAllDrives=True  # هذا السطر يحل مشكلة الـ 403 Storage Quota
                        ).execute()
                        
                        st.success(f"✅ تم الرفع بنجاح! تم الحفظ في مجلد مكتب إشبيلية.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ فشل الرفع: {e}")
                else:
                    st.warning("يرجى ملء الاسم واختيار ملف.")

    # --- قسم عرض المستندات ---
    elif menu == "🔍 استعراض الأرشيف":
        st.header("📂 الوثائق المؤرشفة")
        if st.button("تحديث القائمة 🔄"):
            try:
                # جلب الملفات مع دعم المساحات المشتركة
                results = drive_service.files().list(
                    q=f"'{FOLDER_ID}' in parents and trashed = false",
                    fields="files(id, name, webViewLink)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                items = results.get('files', [])

                if not items:
                    st.info("لا توجد ملفات في المجلد حالياً.")
                else:
                    for item in items:
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            col1.write(f"📄 {item['name']}")
                            col2.markdown(f"[🔗 عرض]({item['webViewLink']})")
                            st.divider()
            except Exception as e:
                st.error(f"تعذر جلب البيانات: {e}")

# تذييل الصفحة
st.sidebar.markdown("---")
st.sidebar.caption("مكتب إشبيلية العلمي للدعاية الأدوية - بغداد 2026")
