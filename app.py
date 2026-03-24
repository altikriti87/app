import streamlit as st
from datetime import date

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الأرشفة الإلكتروني", layout="wide")

# 2. تصميم الأزرار الجانبية باستخدام CSS
st.markdown("""
<style>
    /* تنسيق أزرار القائمة الجانبية */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
        color: #31333F;
        border: 1px solid #dcdde1;
        text-align: right;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    /* تغيير لون الزر عند المرور عليه */
    .stButton > button:hover {
        border-color: #28a745;
        color: #28a745;
    }
    /* تنسيق خاص لزر الخروج أو الأزرار المهمة */
    .stButton > button[key="logout"] {
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# 3. إدارة الحالة (Navigation State)
if 'menu_option' not in st.session_state:
    st.session_state['menu_option'] = 'الرئيسية'

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3845/3845868.png", width=80) # أيقونة اختيارية
    st.title("القائمة الرئيسية")
    st.write("---")
    
    # الأزرار الجانبية
    if st.button("🏠 الصفحة الرئيسية", use_container_width=True):
        st.session_state['menu_option'] = 'الرئيسية'
    
    if st.button("➕ إضافة مستند جديد", use_container_width=True):
        st.session_state['menu_option'] = 'إضافة'
    
    if st.button("🔍 البحث عن مستند", use_container_width=True):
        st.session_state['menu_option'] = 'بحث'
        
    if st.button("📝 تعديل مستند", use_container_width=True):
        st.session_state['menu_option'] = 'تعديل'
        
    if st.button("📊 عرض الكل", use_container_width=True):
        st.session_state['menu_option'] = 'عرض'
        
    st.write("---")
    if st.button("🚪 تسجيل الخروج", key="logout", use_container_width=True):
        st.info("تم تسجيل الخروج")

# --- محتوى الصفحة الرئيسي ---

# 1. واجهة الرئيسية
if st.session_state['menu_option'] == 'الرئيسية':
    st.title("مرحباً بك في نظام الأرشفة")
    st.info("اختر أحد الخيارات من القائمة الجانبية للبدء")
    
    # إحصائيات سريعة
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المستندات", "1,250")
    col2.metric("مستندات اليوم", "14")
    col3.metric("المساحة المستخدمة", "1.2 GB")

# 2. واجهة إضافة مستند
elif st.session_state['menu_option'] == 'إضافة':
    st.header("إضافة مستند جديد")
    st.write("يرجى تعبئة البيانات التالية بدقة:")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            doc_type = st.selectbox("Document Type", ["كتاب رسمي", "تعميم", "قرار", "تقرير"])
            doc_date = st.date_input("Enter document date", value=date.today())
            sender = st.text_input("Enter sender")
            receiver = st.text_input("Enter receiver")
        
        with col2:
            subject = st.text_input("Document subject")
            keywords = st.text_input("Keywords (comma separated)")
            tags = st.text_input("Enter tags (use - for words, , or ; for tags)")
            attachment_desc = st.text_area("Attachment description or type")
            
        uploaded_files = st.file_uploader("رفع المرفقات للوثيقة", accept_multiple_files=True)
        
        if st.button("حفظ المستند في الأرشيف", type="primary"):
            if subject:
                st.success(f"✅ تم حفظ المستند: {subject} بنجاح")
            else:
                st.warning("يرجى إدخال عنوان المستند على الأقل")

# 3. واجهات تجريبية للبقية
elif st.session_state['menu_option'] == 'بحث':
    st.header("🔍 البحث في الأرشيف")
    st.text_input("ادخل كلمة البحث أو رقم المستند...")
