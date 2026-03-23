import os
import sys
import datetime
import hashlib
import cv2
import streamlit as st
import pandas as pd
import numpy as np
import easyocr
from PIL import Image
from io import BytesIO
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# --- 1. إعداد قاعدة البيانات ---
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    path_on_disk = Column(String) # مسار المجلد (محلي أو على جوجل درايف)
    documents = relationship("Document", back_populates="folder")

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    file_path = Column(String)
    content_text = Column(Text)
    upload_date = Column(DateTime, default=datetime.datetime.now)
    folder_id = Column(Integer, ForeignKey('folders.id'))
    folder = relationship("Folder", back_populates="documents")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.now)

# إنشاء ملف القاعدة
engine = create_engine('sqlite:///ultimate_archive.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

# إنشاء مستخدم أدمن افتراضي
if not db.query(User).filter_by(username='admin').first():
    db.add(User(username='admin', password=hashlib.sha256('admin'.encode()).hexdigest()))
    db.commit()

# --- 2. محرك الـ OCR ---
@st.cache_resource
def load_ocr(langs):
    return easyocr.Reader(langs)

# --- 3. واجهة النظام والأمان ---
st.set_page_config(page_title="نظام الأرشفة السحابي 2026", layout="wide")

def check_login():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 نظام الأرشفة الذكي - تسجيل الدخول")
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            hp = hashlib.sha256(p.encode()).hexdigest()
            if db.query(User).filter_by(username=u, password=hp).first():
                st.session_state.authenticated = True
                st.session_state.username = u
                st.rerun()
            else: st.error("بيانات الدخول غير صحيحة")
        return False
    return True

if check_login():
    # تنسيق الواجهة (RTL)
    st.markdown("""<style>.main {text-align: right; direction: rtl;} div.stButton>button {background-color: #2E86C1; color: white; border-radius: 10px; font-weight: bold;}</style>""", unsafe_allow_html=True)
    
    st.sidebar.title(f"👤 المستخدم: {st.session_state.username}")
    menu = st.sidebar.radio("القائمة الرئيسية", ["🏠 لوحة التحكم", "📁 إدارة المجلدات (Cloud)", "📤 أرشفة وثيقة ذكية", "🔍 البحث والتصحيح اليدوي", "📜 سجل الرقابة والتقارير"])

    # --- إدارة المجلدات ---
    if menu == "📁 إدارة المجلدات (Cloud)":
        st.header("إعداد شجرة الأرشفة ومزامنة السحابة")
        st.info("نصيحة: إذا كنت تستخدم Google Drive، اختر مسار المجلد داخل قرص الـ G المخصص لجوجل درايف على جهازك.")
        
        with st.form("folder_form"):
            f_name = st.text_input("اسم المجلد (مثلاً: العقود الرسمية)")
            f_path = st.text_input("المسار الفعلي (اتركه فارغاً للافتراضي)", placeholder="C:/Users/Name/Google Drive/Archive")
            if st.form_submit_button("إضافة المجلد للأرشيف"):
                if f_name:
                    final_path = f_path if f_path else f"storage/{f_name}"
                    os.makedirs(final_path, exist_ok=True)
                    db.add(Folder(name=f_name, path_on_disk=final_path))
                    db.add(AuditLog(user=st.session_state.username, action=f"إنشاء مجلد: {f_name}"))
                    db.commit()
                    st.success(f"تم اعتماد المجلد في المسار: {final_path}")

    # --- أرشفة وثيقة ---
    elif menu == "📤 أرشفة وثيقة ذكية":
        st.header("أرشفة وثيقة مع تحسين القراءة")
        folders = db.query(Folder).all()
        if not folders:
            st.warning("يرجى إنشاء مجلد أولاً.")
        else:
            f_options = {f.name: f for f in folders}
            col1, col2 = st.columns(2)
            with col1:
                target_f = st.selectbox("اختر المجلد المستهدف", list(f_options.keys()))
                langs = st.multiselect("لغات الوثيقة (لزيادة الدقة)", ["ar", "en"], default=["ar", "en"])
            with col2:
                uploaded_file = st.file_uploader("اختر صورة الوثيقة", type=['png', 'jpg', 'jpeg'])

            if uploaded_file and st.button("بدء المسح والأرشفة السحابية"):
                folder_obj = f_options[target_f]
                full_path = os.path.join(folder_obj.path_on_disk, uploaded_file.name)
                
                # حفظ الملف (سيتم رفعه للدرايف تلقائياً إذا كان المسار يتبع له)
                with open(full_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                with st.spinner("جاري معالجة الصورة واستخراج النص..."):
                    # معالجة الصورة لتحسين الـ OCR
                    img = Image.open(uploaded_file)
                    opencv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
                    processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                    
                    reader = load_ocr(langs)
                    results = reader.readtext(processed, detail=0, paragraph=True)
                    final_text = " ".join(results)

                # حفظ في قاعدة البيانات
                new_doc = Document(title=uploaded_file.name, file_path=full_path, content_text=final_text, folder_id=folder_obj.id)
                db.add(new_doc)
                db.add(AuditLog(user=st.session_state.username, action=f"أرشفة وثيقة: {uploaded_file.name}"))
                db.commit()
                st.success("تم الحفظ والفهرسة بنجاح!")
                st.text_area("النص المكتشف (معاينة):", final_text)

    # --- البحث والتصحيح ---
    elif menu == "🔍 البحث والتصحيح اليدوي":
        st.header("البحث المتقدم وتصحيح نصوص الوثائق القديمة")
        search_q = st.text_input("أدخل كلمة للبحث (مثلاً: عبد اللطيف، بغداد، قرار)")
        if search_q:
            results = db.query(Document).filter(Document.content_text.contains(search_q)).all()
            if not results: st.info("لا توجد نتائج تطابق بحثك.")
            for doc in results:
                with st.expander(f"📄 {doc.title} - المجلد: {doc.folder.name}"):
                    c1, c2 = st.columns([1, 2])
                    with c1: st.image(doc.file_path, use_column_width=True)
                    with c2:
                        updated_txt = st.text_area("تعديل النص المستخرج يدوياً:", doc.content_text, key=f"edit_{doc.id}", height=300)
                        if st.button("حفظ النص المعدل", key=f"save_{doc.id}"):
                            doc.content_text = updated_txt
                            db.commit()
                            st.success("تم تحديث النص بنجاح في قاعدة البيانات.")

    # --- التقارير والسجلات ---
    elif menu == "📜 سجل الرقابة والتقارير":
        st.header("سجل العمليات والتقارير الإدارية")
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
        df = pd.DataFrame([{"المستخدم": l.user, "الإجراء": l.action, "الوقت": l.timestamp} for l in logs])
        st.dataframe(df, use_container_width=True)
        
        # تصدير Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("تحميل سجل العمليات (Excel)", data=output.getvalue(), file_name="audit_report.xlsx")

    # --- لوحة التحكم ---
    else:
        st.header("📊 إحصائيات الأرشيف")
        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي الوثائق", db.query(Document).count())
        col2.metric("عدد المجلدات", db.query(Folder).count())
        col3.metric("العمليات اليوم", db.query(AuditLog).filter(AuditLog.timestamp >= datetime.date.today()).count())
        
        st.write("---")
        if st.sidebar.button("تسجيل الخروج"):
            st.session_state.authenticated = False
            st.rerun()
