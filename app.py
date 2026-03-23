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
    documents = relationship("Document", back_populates="folder")

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    file_path = Column(String)
    content_text = Column(Text)
    language = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.now)
    folder_id = Column(Integer, ForeignKey('folders.id'))
    folder = relationship("Folder", back_populates="documents")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.now)

# إنشاء قاعدة البيانات (محلياً بصيغة SQLite)
engine = create_engine('sqlite:///smart_dms_final.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

# إنشاء مستخدم "مدير" افتراضي إذا لم يكن موجوداً
if not db.query(User).filter_by(username='admin').first():
    admin_pass = hashlib.sha256('admin'.encode()).hexdigest()
    db.add(User(username='admin', password=admin_pass))
    db.commit()

# --- 2. محرك الـ OCR (تحميل الموديل مرة واحدة لتوفير الذاكرة) ---
@st.cache_resource
def get_ocr_reader(langs):
    return easyocr.Reader(langs, gpu=False) # تعطيل GPU لأن سيرفرات Streamlit مجانية

# --- 3. نظام الحماية والواجهة ---
st.set_page_config(page_title="Seville Smart Archive 2026", layout="wide", initial_sidebar_state="expanded")

def login_system():
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        st.markdown("<h2 style='text-align: center;'>🔐 نظام الأرشفة الذكي - تسجيل الدخول</h2>", unsafe_allow_html=True)
        with st.container():
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                u = st.text_input("اسم المستخدم")
                p = st.text_input("كلمة المرور", type="password")
                if st.button("دخول", use_container_width=True):
                    hashed_p = hashlib.sha256(p.encode()).hexdigest()
                    user = db.query(User).filter_by(username=u, password=hashed_p).first()
                    if user:
                        st.session_state.auth = True
                        st.session_state.user = u
                        st.rerun()
                    else:
                        st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
        return False
    return True

if login_system():
    # الهيدر الجانبي
    st.sidebar.success(f"مرحباً بك: {st.session_state.user}")
    menu = st.sidebar.radio("المهام الرئيسية", ["🏠 لوحة التحكم", "📁 إدارة المجلدات", "📤 أرشفة وثيقة جديدة", "🔍 البحث في الأرشيف", "📜 سجل العمليات"])

    # --- القسم 1: لوحة التحكم ---
    if menu == "🏠 لوحة التحكم":
        st.title("📊 حالة الأرشيف العام")
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الوثائق", db.query(Document).count())
        c2.metric("المجلدات النشطة", db.query(Folder).count())
        c3.metric("عمليات اليوم", db.query(AuditLog).filter(AuditLog.timestamp >= datetime.date.today()).count())
        
        if st.sidebar.button("تسجيل الخروج"):
            st.session_state.auth = False
            st.rerun()

    # --- القسم 2: إدارة المجلدات ---
    elif menu == "📁 إدارة المجلدات":
        st.header("إدارة تصنيفات المجلدات")
        new_folder = st.text_input("اسم المجلد الجديد (مثلاً: أدوية الضغط، عقود 2026)")
        if st.button("إنشاء المجلد"):
            if new_folder:
                if not db.query(Folder).filter_by(name=new_folder).first():
                    db.add(Folder(name=new_folder))
                    db.commit()
                    st.success(f"تم إنشاء مجلد {new_folder}")
                else: st.warning("المجلد موجود مسبقاً")

    # --- القسم 3: أرشفة وثيقة ---
    elif menu == "📤 أرشفة وثيقة جديدة":
        st.header("رفع ومعالجة وثيقة ذكية")
        folders = db.query(Folder).all()
        f_map = {f.name: f.id for f in folders}
        
        if not f_map:
            st.info("يرجى إنشاء مجلد واحد على الأقل قبل البدء بالأرشفة.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                sel_f = st.selectbox("اختر المجلد", list(f_map.keys()))
                lang_choice = st.multiselect("لغة النص في الصورة", ['ar', 'en'], default=['ar'])
            with col2:
                file = st.file_uploader("اختر صورة الوثيقة", type=['png', 'jpg', 'jpeg'])

            if file and st.button("بدء التحليل والأرشفة"):
                with st.spinner("جاري قراءة النص وتحسين الصورة..."):
                    # 1. حفظ الملف في الذاكرة المؤقتة
                    os.makedirs(f"storage/{sel_f}", exist_ok=True)
                    f_path = os.path.join(f"storage/{sel_f}", file.name)
                    with open(f_path, "wb") as f: f.write(file.getbuffer())

                    # 2. معالجة الصورة بـ OpenCV
                    img = Image.open(file).convert('RGB')
                    opencv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
                    # تحسين التباين لزيادة دقة الـ OCR
                    processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

                    # 3. تشغيل OCR
                    reader = get_ocr_reader(lang_choice)
                    results = reader.readtext(processed, detail=0, paragraph=True)
                    final_text = " ".join(results)

                    # 4. الحفظ في قاعدة البيانات
                    new_doc = Document(title=file.name, file_path=f_path, content_text=final_text, 
                                       language=str(lang_choice), folder_id=f_map[sel_f])
                    db.add(new_doc)
                    db.add(AuditLog(user=st.session_state.user, action=f"أرشفة وثيقة: {file.name}"))
                    db.commit()
                    
                    st.success("تم الحفظ بنجاح!")
                    st.text_area("النص الذي تم استخراجه:", final_text, height=200)

    # --- القسم 4: البحث والتعديل ---
    elif menu == "🔍 البحث في الأرشيف":
        st.header("البحث الذكي في محتوى الوثائق")
        search_query = st.text_input("اكتب اسم الدواء، رقم الوثيقة، أو أي كلمة من المحتوى...")
        if search_query:
            results = db.query(Document).filter(Document.content_text.contains(search_query) | Document.title.contains(search_query)).all()
            st.write(f"تم العثور على ({len(results)}) وثيقة:")
            for d in results:
                with st.expander(f"📄 {d.title} - مجلد: {d.folder.name}"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        if os.path.exists(d.file_path):
                            st.image(d.file_path, use_container_width=True)
                    with c2:
                        st.info(f"تاريخ الرفع: {d.upload_date.strftime('%Y-%m-%d %H:%M')}")
                        new_content = st.text_area("المحتوى المكتوب (يمكنك تعديله):", d.content_text, key=f"edit_{d.id}", height=200)
                        if st.button("حفظ التغييرات", key=f"save_{d.id}"):
                            d.content_text = new_content
                            db.commit()
                            st.success("تم تحديث البيانات")

    # --- القسم 5: السجلات ---
    elif menu == "📜 سجل العمليات":
        st.header("سجل الرقابة (Audit Log)")
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
        log_data = [{"المستخدم": l.user, "الإجراء": l.action, "الوقت": l.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for l in logs]
        st.table(pd.DataFrame(log_data))
