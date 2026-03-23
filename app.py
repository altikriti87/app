import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# --- 1. الإعدادات والربط السحابي مع Google Drive ---
# جلب بيانات الحساب من Streamlit Secrets
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    drive_service = build('drive', 'v3', credentials=credentials)
else:
    st.error("⚠️ لم يتم العثور على إعدادات Secrets. يرجى التأكد من لصق بيانات JSON في إعدادات التطبيق على موقع Streamlit.")

# المعرف الخاص بمجلد مكتب إشبيلية (تم تحديثه بناءً على الرابط الذي أرسلته)
FOLDER_ID = "1W2CXAqHbZSBl3PUi0EvOan9TgU3oF-DZ" 

# --- 2. نظام التحقق من كلمة المرور ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center;'>🔐 نظام أرشفة مكتب إشبيلية العلمي</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("أدخل كلمة المرور للدخول:", type="password")
            if st.button("دخول", use_container_width=True):
                # يتم جلب كلمة المرور من Secrets لزيادة الأمان
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
    st.sidebar.info("نظام الأرشفة الإلكتروني - بغداد")
    
    menu = st.sidebar.radio("القائمة الرئيسية:", ["📥 إضافة مستند جديد", "🔍 استعراض الأرشيف"])

    # --- قسم رفع الملفات ---
    if menu == "📥 إضافة مستند جديد":
        st.header("📝 أرشفة وثيقة جديدة")
        
        with st.form("upload_form", clear_on_submit=True):
            doc_name = st.text_input("عنوان الوثيقة (مثلاً: فاتورة ذخر، كتاب تسجيل)")
            doc_type = st.selectbox("تصنيف الوثيقة", ["وارد", "صادر", "تسجيل دواء", "حسابات", "أخرى"])
            uploaded_file = st.file_uploader("اختر الملف (PDF أو صورة)", type=['pdf', 'png', 'jpg', 'jpeg'])
            
            submit = st.form_submit_button("إرسال إلى Google Drive ✅")
            
            if submit:
                if uploaded_file is not None and doc_name:
                    try:
                        # تجهيز اسم الملف وتاريخه
                        file_metadata = {
                            'name': f"{doc_type}_{doc_name}_{datetime.now().strftime('%Y-%m-%d')}",
                            'parents': [FOLDER_ID]
                        }
                        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.read()), 
                                                 mimetype=uploaded_file.type)
                        
                        # عملية الرفع إلى جوجل درايف
                        file = drive_service.files().create(body=file_metadata, 
                                                          media_body=media, 
                                                          fields='id').execute()
                        
                        st.success(f"✅ تم حفظ الوثيقة بنجاح في السحابة!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ فشل الرفع. تأكد من عمل Share للمجلد مع إيميل الحساب. الخطأ: {e}")
                else:
                    st.warning("يرجى كتابة عنوان الوثيقة واختيار ملف أولاً.")

    # --- قسم استعراض الملفات ---
    elif menu == "🔍 استعراض الأرشيف":
        st.header("📂 الملفات المؤرشفة حالياً")
        if st.button("تحديث القائمة 🔄"):
            try:
                # جلب قائمة الملفات من المجلد المحدد
                results = drive_service.files().list(
                    q=f"'{FOLDER_ID}' in parents and trashed = false",
                    fields="files(id, name, webViewLink, iconLink)"
                ).execute()
                items = results.get('files', [])

                if not items:
                    st.info("لا توجد ملفات مؤرشفة في هذا المجلد حتى الآن.")
                else:
                    for item in items:
                        col1, col2 = st.columns([4, 1])
                        col1.write(f"📄 {item['name']}")
                        col2.markdown(f"[🔗 عرض]({item['webViewLink']})")
                        st.divider()
            except Exception as e:
                st.error(f"تعذر جلب القائمة: {e}")

# تذييل الصفحة
st.sidebar.markdown("---")
st.sidebar.caption("مكتب إشبيلية العلمي للدعاية الأدوية - 2026")
