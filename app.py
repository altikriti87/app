import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# --- 1. الإعدادات والربط السحابي ---
# جلب بيانات الحساب من Secrets
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    drive_service = build('drive', 'v3', credentials=credentials)
else:
    st.error("لم يتم العثور على إعدادات Secrets. يرجى التأكد من لصق البيانات في إعدادات Streamlit.")

# ضع هنا الرمز (ID) الخاص بمجلد مكتب إشبيلية في جوجل درايف
FOLDER_ID = "ضع_هنا_ID_المجلد_الخاص_بك" 

# --- 2. نظام حماية الدخول ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center;'>🔐 نظام أرشفة مكتب إشبيلية العلمي</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("أدخل كلمة المرور:", type="password")
            if st.button("دخول", use_container_width=True):
                if pwd == st.secrets["password"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ كلمة المرور غير صحيحة")
        return False
    return True

# --- 3. الواجهة الرئيسية للبرنامج ---
if check_password():
    st.sidebar.title("⭐ إدارة مكتب إشبيلية")
    st.sidebar.write("نظام الأرشفة السحابي")
    
    menu = st.sidebar.radio("انتقل إلى:", ["📥 إضافة وثيقة جديدة", "🔍 استعراض الملفات"])

    # --- قسم الإضافة ---
    if menu == "📥 إضافة وثيقة جديدة":
        st.header("📝 أرشفة مستند جديد")
        with st.form("upload_form", clear_on_submit=True):
            doc_name = st.text_input("اسم الوثيقة أو الموضوع")
            doc_type = st.selectbox("نوع المستند", ["وارد", "صادر", "مستند تسجيل", "بريد خارجي"])
            uploaded_file = st.file_uploader("اختر الملف (PDF أو صورة)", type=['pdf', 'png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("رفع إلى Google Drive ✅"):
                if uploaded_file and doc_name:
                    try:
                        # تسمية الملف وتنظيمه
                        file_metadata = {
                            'name': f"{doc_type}_{doc_name}_{datetime.now().strftime('%Y%m%d')}",
                            'parents': [FOLDER_ID]
                        }
                        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.read()), 
                                                 mimetype=uploaded_file.type)
                        
                        # عملية الرفع الفعلية
                        file = drive_service.files().create(body=file_metadata, 
                                                          media_body=media, 
                                                          fields='id').execute()
                        
                        st.success(f"✅ تم الرفع بنجاح إلى درايف!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"خطأ في الاتصال: {e}")
                else:
                    st.warning("يرجى إدخال اسم الوثيقة واختيار ملف.")

    # --- قسم العرض ---
    elif menu == "🔍 استعراض الملفات":
        st.header("📂 الأرشيف السحابي الحالي")
        if st.button("تحديث القائمة 🔄"):
            try:
                results = drive_service.files().list(
                    q=f"'{FOLDER_ID}' in parents and trashed = false",
                    fields="files(id, name, webViewLink, thumbnailLink)"
                ).execute()
                items = results.get('files', [])

                if not items:
                    st.info("المجلد فارغ حالياً.")
                else:
                    for item in items:
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            col1.write(f"📄 {item['name']}")
                            col2.markdown(f"[🔗 فتح]({item['webViewLink']})")
                            st.divider()
            except Exception as e:
                st.error(f"تعذر جلب البيانات: {e}")

# تذييل
st.sidebar.markdown("---")
st.sidebar.caption("مكتب إشبيلية العلمي للدعاية الأدوية - بغداد")
