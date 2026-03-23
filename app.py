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

engine = create_engine('sqlite:///smart_dms_final.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

# إنشاء مستخدم افتراضي
if not db.query(User).filter_by(username='admin').first():
    db.add(User(username='admin', password=hashlib.sha256('admin'.encode()).hexdigest()))
    db.commit()

# --- 2. محرك الـ OCR الديناميكي ---
@st.cache_resource
def get_ocr_reader(langs):
    # langs: ['ar', 'en'] أو ['ar'] أو ['en']
    return easyocr.Reader(langs)

# --- 3. نظام الحماية والواجهة ---
st.set_page_config(page_title="نظام الأرشفة الذكي 2026", layout="wide")

def login_system():
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        st.title("🔐 الدخول للنظام")
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل الدخول"):
            if db.query(User).filter_by(username=u, password=hashlib.sha256(p.encode()).hexdigest()).first():
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else: st.error("بيانات خاطئة")
        return False
    return True

if login_system():
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = st.sidebar.radio("القائمة", ["🏠 الإحصائيات", "📁 المجلدات", "📤 أرشفة وثيقة", "🔍 البحث والتعديل", "📜 السجلات"])

    # --- أرشفة وثيقة (النسخة المحسنة) ---
    if menu == "📤 أرشفة وثيقة":
        st.header("أرشفة وثيقة جديدة")
        folders = db.query(Folder).all()
        f_map = {f.name: f.id for f in folders}
        
        if not f_map:
            st.warning("يرجى إنشاء مجلد أولاً من قسم المجلدات.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                sel_f = st.selectbox("المجلد المستهدف", list(f_map.keys()))
                lang_choice = st.multiselect("لغة الوثيقة (اختر واحدة لزيادة الدقة)", ['ar', 'en'], default=['ar', 'en'])
            with col2:
                file = st.file_uploader("ارفع الصورة", type=['png', 'jpg', 'jpeg'])

            if file and st.button("تحليل وأرشفة"):
                # حفظ الملف
                os.makedirs(f"storage/{sel_f}", exist_ok=True)
                f_path = os.path.join(f"storage/{sel_f}", file.name)
                with open(f_path, "wb") as f: f.write(file.getbuffer())

                with st.spinner("جاري المعالجة الصورية والـ OCR..."):
                    # 1. تحسين الصورة (Image Pre-processing)
                    img = Image.open(file)
                    opencv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
                    # تنظيف الصورة من "النمش" أو النقط السوداء
                    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
                    processed = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

                    # 2. القراءة اللغوية
                    reader = get_ocr_reader(lang_choice)
                    results = reader.readtext(processed, detail=0, paragraph=True)
                    final_text = " ".join(results)

                # 3. الحفظ في القاعدة
                new_doc = Document(title=file.name, file_path=f_path, content_text=final_text, 
                                   language=str(lang_choice), folder_id=f_map[sel_f])
                db.add(new_doc)
                db.add(AuditLog(user=st.session_state.user, action=f"أرشفة: {file.name}"))
                db.commit()
                st.success("تمت الأرشفة بنجاح!")
                st.text_area("النص المستخرج:", final_text, height=200)

    # --- البحث والتعديل اليدوي ---
    elif menu == "🔍 البحث والتعديل":
        st.header("البحث في الأرشيف")
        q = st.text_input("ابحث عن نص أو اسم ملف...")
        if q:
            docs = db.query(Document).filter(Document.content_text.contains(q) | Document.title.contains(q)).all()
            for d in docs:
                with st.expander(f"📄 {d.title} (بتاريخ {d.upload_date.date()})"):
                    c1, c2 = st.columns([1, 2])
                    with c1: st.image(d.file_path)
                    with c2:
                        corrected_text = st.text_area("تصحيح النص يدوياً:", d.content_text, key=f"edit_{d.id}", height=250)
                        if st.button("حفظ التعديل", key=f"btn_{d.id}"):
                            d.content_text = corrected_text
                            db.commit()
                            st.success("تم التحديث")

    # --- بقية الأقسام ---
    elif menu == "📁 المجلدات":
        st.header("إدارة المجلدات")
        name = st.text_input("اسم المجلد")
        if st.button("إنشاء"):
            if name:
                db.add(Folder(name=name)); db.commit()
                st.success("تم")

    elif menu == "📜 السجلات":
        st.header("سجل الرقابة")
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
        st.dataframe(pd.DataFrame([{"المستخدم": l.user, "العملية": l.action, "الوقت": l.timestamp} for l in logs]))

    else:
        st.header("لوحة التحكم")
        col1, col2 = st.columns(2)
        col1.metric("إجمالي الوثائق", db.query(Document).count())
        col2.metric("عدد المجلدات", db.query(Folder).count())
        if st.sidebar.button("تسجيل الخروج"):
            st.session_state.auth = False
            st.rerun()