"""
نظام الأرشفة والمراسلات الداخلية
نظام ويب متكامل لإدارة المستندات والمراسلات الداخلية
متعدد المستخدمين مع صلاحيات متدرجة
"""

import os
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template_string, request, redirect, url_for, flash, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# ======================
# إعدادات التطبيق
# ======================
app = Flask(__name__)

# إعدادات الأمان - يفضل تغيير المفتاح في الإنتاج
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'my-secret-key-change-in-production-2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///archiving.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'png', 'txt'}

# إنشاء مجلد الرفع إذا لم يكن موجوداً
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# تهيئة قاعدة البيانات
db = SQLAlchemy(app)

# ======================
# نماذج قاعدة البيانات
# ======================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='employee')  # admin, employee, viewer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    document_type = db.Column(db.String(50))
    department = db.Column(db.String(100))
    security_level = db.Column(db.String(20), default='normal')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_accessible_by(self, user_id, user_role):
        if user_role == 'admin':
            return True
        if self.security_level == 'normal':
            return True
        access = DocumentAccess.query.filter_by(document_id=self.id, user_id=user_id).first()
        return access is not None and access.can_view
    
    def can_edit_by(self, user_id, user_role):
        if user_role == 'admin':
            return True
        if self.created_by == user_id:
            return True
        access = DocumentAccess.query.filter_by(document_id=self.id, user_id=user_id).first()
        return access is not None and access.can_edit

class DocumentAccess(db.Model):
    __tablename__ = 'document_access'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    can_view = db.Column(db.Boolean, default=True)
    can_edit = db.Column(db.Boolean, default=False)

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(50))
    action = db.Column(db.String(100), nullable=False)
    document_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ======================
# دوال مساعدة
# ======================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def log_action(user_id, username, action, document_id=None, details=None):
    try:
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            document_id=document_id,
            details=details,
            ip_address=request.remote_addr if request else '0.0.0.0'
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"خطأ في تسجيل السجل: {e}")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('الرجاء تسجيل الدخول أولاً', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ======================
# قوالب HTML (مضمنة)
# ======================

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}نظام الأرشفة والمراسلات{% endblock %}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; direction: rtl; }
        .header { background: #2c3e50; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; position: fixed; top: 0; right: 0; left: 0; z-index: 100; }
        .header h1 { font-size: 1.5rem; }
        .user-info { display: flex; gap: 15px; align-items: center; }
        .logout, .back-link { color: white; text-decoration: none; background: #e74c3c; padding: 5px 10px; border-radius: 5px; }
        .back-link { background: #3498db; }
        .sidebar { width: 220px; background: #34495e; position: fixed; top: 70px; bottom: 0; padding: 20px 0; overflow-y: auto; }
        .sidebar ul { list-style: none; }
        .sidebar li a { display: block; padding: 12px 20px; color: white; text-decoration: none; transition: 0.3s; }
        .sidebar li a:hover { background: #2c3e50; }
        .content { margin-right: 220px; margin-top: 70px; padding: 20px; }
        .form-container, .search-form, .document-details { max-width: 600px; margin: 20px auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px; font-family: inherit; }
        button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; }
        button:hover { background: #2980b9; }
        .documents-table { width: 100%; background: white; border-collapse: collapse; margin-top: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .documents-table th, .documents-table td { padding: 12px; text-align: right; border-bottom: 1px solid #ddd; }
        .documents-table th { background: #34495e; color: white; }
        .documents-table tr:hover { background: #f5f5f5; }
        .level-normal { color: green; font-weight: bold; }
        .level-confidential { color: orange; font-weight: bold; }
        .level-top_secret { color: red; font-weight: bold; }
        .login-container { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.2); text-align: center; }
        .login-container input { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .flash-messages { position: fixed; top: 80px; right: 20px; left: 20px; z-index: 1000; }
        .flash { padding: 12px 20px; border-radius: 5px; margin-bottom: 10px; text-align: center; }
        .flash.success { background: #2ecc71; color: white; }
        .flash.error { background: #e74c3c; color: white; }
        .flash.info { background: #3498db; color: white; }
        .detail-row { padding: 10px 0; border-bottom: 1px solid #eee; }
        .detail-row strong { display: inline-block; width: 120px; color: #2c3e50; }
        @media (max-width: 768px) { .sidebar { display: none; } .content { margin-right: 0; } }
    </style>
</head>
<body>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-messages">
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
</body>
</html>
'''

LOGIN_TEMPLATE = '''
{% extends "base" %}
{% block title %}تسجيل الدخول{% endblock %}
{% block content %}
<div class="login-container">
    <h1>نظام الأرشفة والمراسلات الداخلية</h1>
    <form method="POST">
        <input type="text" name="username" placeholder="اسم المستخدم" required>
        <input type="password" name="password" placeholder="كلمة المرور" required>
        <button type="submit">دخول</button>
    </form>
    <div class="demo-info" style="margin-top:20px;padding-top:15px;border-top:1px solid #ddd;">
        <p>المستخدم الافتراضي: <strong>admin</strong> | كلمة المرور: <strong>admin123</strong></p>
    </div>
</div>
{% endblock %}
'''

INDEX_TEMPLATE = '''
{% extends "base" %}
{% block title %}لوحة التحكم{% endblock %}
{% block content %}
<div class="header">
    <h1>نظام الأرشفة والمراسلات الداخلية</h1>
    <div class="user-info">
        مرحباً، {{ session.full_name }}
        <a href="{{ url_for('logout') }}" class="logout">تسجيل خروج</a>
    </div>
</div>
<div class="sidebar">
    <ul>
        <li><a href="{{ url_for('index') }}">الرئيسية</a></li>
        <li><a href="{{ url_for('add_document') }}">إضافة مستند جديد</a></li>
        <li><a href="{{ url_for('search') }}">البحث المتقدم</a></li>
        {% if session.role == 'admin' %}
        <li><a href="{{ url_for('manage_users') }}">إدارة المستخدمين</a></li>
        <li><a href="{{ url_for('audit_log') }}">سجل العمليات</a></li>
        {% endif %}
    </ul>
</div>
<div class="content">
    <h2>المستندات والمراسلات</h2>
    <table class="documents-table">
        <thead>汽<br>汽<th>#</th><th>العنوان</th><th>النوع</th><th>القسم</th><th>درجة السرية</th><th>التاريخ</th><th>العمليات</th> </thead>
        <tbody>
            {% for doc in documents %}
            <tr>
                <td>{{ doc.id }}</td>
                <td>{{ doc.title }}</td>
                <td>{{ doc.document_type }}</td>
                <td>{{ doc.department }}</td>
                <td class="level-{{ doc.security_level }}">
                    {% if doc.security_level == 'normal' %}عادي{% elif doc.security_level == 'confidential' %}سري{% else %}شديد السرية{% endif %}
                </td>
                <td>{{ doc.created_at.strftime('%Y-%m-%d') }}</td>
                <td>
                    <a href="{{ url_for('view_document', doc_id=doc.id) }}">عرض</a>
                    {% if doc.created_by == session.user_id or session.role == 'admin' %}
                    | <a href="{{ url_for('edit_document', doc_id=doc.id) }}">تعديل</a>
                    {% endif %}
                </td>
            </tr>
            {% else %}
            <tr><td colspan="7">لا توجد مستندات حتى الآن</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
'''

ADD_DOCUMENT_TEMPLATE = '''
{% extends "base" %}
{% block title %}إضافة مستند جديد{% endblock %}
{% block content %}
<div class="header">
    <h1>إضافة مستند جديد</h1>
    <a href="{{ url_for('index') }}" class="back-link">← العودة للرئيسية</a>
</div>
<div class="form-container">
    <form method="POST" enctype="multipart/form-data">
        <div class="form-group"><label>عنوان المستند *</label><input type="text" name="title" required></div>
        <div class="form-group"><label>الوصف</label><textarea name="description" rows="4"></textarea></div>
        <div class="form-group">
            <label>نوع المستند</label>
            <select name="document_type">
                <option value="مراسلة">مراسلة</option><option value="تقرير">تقرير</option>
                <option value="عقد">عقد</option><option value="فواتير">فواتير</option><option value="أخرى">أخرى</option>
            </select>
        </div>
        <div class="form-group">
            <label>القسم</label>
            <select name="department">
                <option value="الإدارة">الإدارة</option><option value="المالية">المالية</option>
                <option value="الموارد البشرية">الموارد البشرية</option><option value="التقنية">التقنية</option>
                <option value="التسويق">التسويق</option>
            </select>
        </div>
        <div class="form-group">
            <label>درجة السرية</label>
            <select name="security_level" id="security_level">
                <option value="normal">عادي (يطلع عليه الجميع)</option>
                <option value="confidential">سري (يطلع عليه المصرح لهم فقط)</option>
                <option value="top_secret">شديد السرية (يطلع عليه المصرح لهم فقط)</option>
            </select>
        </div>
        <div class="form-group" id="access_users_group" style="display:none;">
            <label>المستخدمون المصرح لهم بالاطلاع</label>
            <select name="access_users" multiple size="5">
                {% for user in users %}
                <option value="{{ user.id }}">{{ user.full_name }}</option>
                {% endfor %}
            </select>
            <small>اضغط Ctrl لتحديد أكثر من مستخدم</small>
        </div>
        <div class="form-group"><label>رفع ملف (اختياري)</label><input type="file" name="file"></div>
        <button type="submit">حفظ المستند</button>
    </form>
</div>
<script>
    document.getElementById('security_level').addEventListener('change', function() {
        document.getElementById('access_users_group').style.display = (this.value != 'normal') ? 'block' : 'none';
    });
</script>
{% endblock %}
'''

VIEW_DOCUMENT_TEMPLATE = '''
{% extends "base" %}
{% block title %}{{ document.title }}{% endblock %}
{% block content %}
<div class="header">
    <h1>عرض المستند</h1>
    <a href="{{ url_for('index') }}" class="back-link">← العودة للرئيسية</a>
</div>
<div class="document-details">
    <div class="detail-row"><strong>رقم المستند:</strong> {{ document.id }}</div>
    <div class="detail-row"><strong>العنوان:</strong> {{ document.title }}</div>
    <div class="detail-row"><strong>الوصف:</strong> {{ document.description or 'لا يوجد' }}</div>
    <div class="detail-row"><strong>النوع:</strong> {{ document.document_type }}</div>
    <div class="detail-row"><strong>القسم:</strong> {{ document.department }}</div>
    <div class="detail-row"><strong>درجة السرية:</strong> 
        <span class="level-{{ document.security_level }}">
            {% if document.security_level == 'normal' %}عادي{% elif document.security_level == 'confidential' %}سري{% else %}شديد السرية{% endif %}
        </span>
    </div>
    <div class="detail-row"><strong>تاريخ الإضافة:</strong> {{ document.created_at.strftime('%Y-%m-%d %H:%M') }}</div>
    {% if document.file_path %}
    <div class="detail-row"><strong>الملف المرفق:</strong> <a href="{{ url_for('download_file', filename=document.file_path) }}" target="_blank">تحميل الملف</a></div>
    {% endif %}
</div>
{% endblock %}
'''

EDIT_DOCUMENT_TEMPLATE = '''
{% extends "base" %}
{% block title %}تعديل المستند{% endblock %}
{% block content %}
<div class="header">
    <h1>تعديل المستند</h1>
    <a href="{{ url_for('view_document', doc_id=document.id) }}" class="back-link">← العودة</a>
</div>
<div class="form-container">
    <form method="POST" enctype="multipart/form-data">
        <div class="form-group"><label>عنوان المستند *</label><input type="text" name="title" value="{{ document.title }}" required></div>
        <div class="form-group"><label>الوصف</label><textarea name="description" rows="4">{{ document.description or '' }}</textarea></div>
        <div class="form-group">
            <label>نوع المستند</label>
            <select name="document_type">
                <option value="مراسلة" {% if document.document_type == 'مراسلة' %}selected{% endif %}>مراسلة</option>
                <option value="تقرير" {% if document.document_type == 'تقرير' %}selected{% endif %}>تقرير</option>
                <option value="عقد" {% if document.document_type == 'عقد' %}selected{% endif %}>عقد</option>
                <option value="فواتير" {% if document.document_type == 'فواتير' %}selected{% endif %}>فواتير</option>
                <option value="أخرى" {% if document.document_type == 'أخرى' %}selected{% endif %}>أخرى</option>
            </select>
        </div>
        <div class="form-group">
            <label>القسم</label>
            <select name="department">
                <option value="الإدارة" {% if document.department == 'الإدارة' %}selected{% endif %}>الإدارة</option>
                <option value="المالية" {% if document.department == 'المالية' %}selected{% endif %}>المالية</option>
                <option value="الموارد البشرية" {% if document.department == 'الموارد البشرية' %}selected{% endif %}>الموارد البشرية</option>
                <option value="التقنية" {% if document.department == 'التقنية' %}selected{% endif %}>التقنية</option>
                <option value="التسويق" {% if document.department == 'التسويق' %}selected{% endif %}>التسويق</option>
            </select>
        </div>
        <div class="form-group"><label>رفع ملف جديد (اختياري)</label><input type="file" name="file"></div>
        <button type="submit">حفظ التغييرات</button>
    </form>
</div>
{% endblock %}
'''

SEARCH_TEMPLATE = '''
{% extends "base" %}
{% block title %}البحث المتقدم{% endblock %}
{% block content %}
<div class="header">
    <h1>البحث المتقدم</h1>
    <a href="{{ url_for('index') }}" class="back-link">← العودة للرئيسية</a>
</div>
<div class="search-form">
    <form method="GET">
        <div class="form-group"><input type="text" name="q" placeholder="كلمة البحث..." value="{{ query }}"></div>
        <div style="display:flex;gap:15px;">
            <div class="form-group" style="flex:1"><label>نوع المستند</label><select name="type"><option value="">الكل</option><option value="مراسلة">مراسلة</option><option value="تقرير">تقرير</option><option value="عقد">عقد</option></select></div>
            <div class="form-group" style="flex:1"><label>القسم</label><select name="department"><option value="">الكل</option><option value="الإدارة">الإدارة</option><option value="المالية">المالية</option><option value="الموارد البشرية">الموارد البشرية</option></select></div>
        </div>
        <div style="display:flex;gap:15px;">
            <div class="form-group" style="flex:1"><label>من تاريخ</label><input type="date" name="from_date" value="{{ from_date }}"></div>
            <div class="form-group" style="flex:1"><label>إلى تاريخ</label><input type="date" name="to_date" value="{{ to_date }}"></div>
        </div>
        <button type="submit">بحث</button>
    </form>
</div>
{% if results is not none %}
<div class="search-results">
    <h3>نتائج البحث ({{ results|length }} مستند)</h3>
    <table class="documents-table">
        <thead><tr><th>العنوان</th><th>النوع</th><th>القسم</th><th>التاريخ</th><th>العمليات</th></tr></thead>
        <tbody>
            {% for doc in results %}
            <tr>
                <td>{{ doc.title }}</td><td>{{ doc.document_type }}</td><td>{{ doc.department }}</td>
                <td>{{ doc.created_at.strftime('%Y-%m-%d') }}</td>
                <td><a href="{{ url_for('view_document', doc_id=doc.id) }}">عرض</a></td>
            </tr>
            {% else %}
            <tr><td colspan="5">لا توجد نتائج مطابقة</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endif %}
{% endblock %}
'''

MANAGE_USERS_TEMPLATE = '''
{% extends "base" %}
{% block title %}إدارة المستخدمين{% endblock %}
{% block content %}
<div class="header">
    <h1>إدارة المستخدمين</h1>
    <a href="{{ url_for('index') }}" class="back-link">← العودة للرئيسية</a>
</div>
<div class="form-container">
    <h3>إضافة مستخدم جديد</h3>
    <form method="POST" action="{{ url_for('add_user') }}">
        <div class="form-group"><input type="text" name="username" placeholder="اسم المستخدم" required></div>
        <div class="form-group"><input type="text" name="full_name" placeholder="الاسم الكامل" required></div>
        <div class="form-group"><input type="password" name="password" placeholder="كلمة المرور" required></div>
        <div class="form-group">
            <select name="role">
                <option value="employee">موظف</option><option value="viewer">قارئ</option><option value="admin">مدير</option>
            </select>
        </div>
        <button type="submit">إضافة مستخدم</button>
    </form>
</div>
<div class="content" style="margin-right:0;">
    <h3>قائمة المستخدمين</h3>
    <table class="documents-table">
        <thead><tr><th>#</th><th>اسم المستخدم</th><th>الاسم الكامل</th><th>الدور</th><th>تاريخ الإضافة</th><th>العمليات</th></tr></thead>
        <tbody>
            {% for user in users %}
            <tr>
                <td>{{ user.id }}</td><td>{{ user.username }}</td><td>{{ user.full_name }}</td>
                <td>{% if user.role == 'admin' %}مدير{% elif user.role == 'employee' %}موظف{% else %}قارئ{% endif %}</td>
                <td>{{ user.created_at.strftime('%Y-%m-%d') }}</td>
                <td>{% if user.id != session.user_id %}<a href="{{ url_for('delete_user', user_id=user.id) }}" onclick="return confirm('هل أنت متأكد؟')">حذف</a>{% endif %}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
'''

AUDIT_LOG_TEMPLATE = '''
{% extends "base" %}
{% block title %}سجل العمليات{% endblock %}
{% block content %}
<div class="header">
    <h1>سجل العمليات</h1>
    <a href="{{ url_for('index') }}" class="back-link">← العودة للرئيسية</a>
</div>
<div class="content" style="margin-right:0;">
    <table class="documents-table">
        <thead><tr><th>التاريخ</th><th>المستخدم</th><th>الإجراء</th><th>التفاصيل</th><th>IP</th></tr></thead>
        <tbody>
            {% for log in logs %}
            <tr>
                <td>{{ log.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                <td>{{ log.username }}</td><td>{{ log.action }}</td><td>{{ log.details or '' }}</td><td>{{ log.ip_address }}</td>
            </tr>
            {% else %}
            <tr><td colspan="5">لا توجد سجلات</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
'''

# ======================
# المسارات (Routes)
# ======================

def render_with_base(template_name, **context):
    templates = {
        'login': LOGIN_TEMPLATE,
        'index': INDEX_TEMPLATE,
        'add_document': ADD_DOCUMENT_TEMPLATE,
        'view_document': VIEW_DOCUMENT_TEMPLATE,
        'edit_document': EDIT_DOCUMENT_TEMPLATE,
        'search': SEARCH_TEMPLATE,
        'manage_users': MANAGE_USERS_TEMPLATE,
        'audit_log': AUDIT_LOG_TEMPLATE,
    }
    content = templates.get(template_name, '')
    full_template = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', 
                                           '{% block content %}' + content + '{% endblock %}')
    return render_template_string(full_template, **context)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') == 'admin':
        documents = Document.query.order_by(Document.created_at.desc()).all()
    else:
        documents = Document.query.filter(
            (Document.security_level == 'normal') |
            (Document.id.in_(
                db.session.query(DocumentAccess.document_id).filter_by(user_id=session['user_id'])
            ))
        ).order_by(Document.created_at.desc()).all()
    
    return render_with_base('index', documents=documents, session=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            session['role'] = user.role
            log_action(user.id, user.username, 'تسجيل دخول')
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_with_base('login')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_action(session['user_id'], session.get('username', ''), 'تسجيل خروج')
    session.clear()
    flash('تم تسجيل الخروج', 'info')
    return redirect(url_for('login'))

@app.route('/add_document', methods=['GET', 'POST'])
@login_required
def add_document():
    users = User.query.filter(User.role != 'admin').all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        document_type = request.form.get('document_type')
        department = request.form.get('department')
        security_level = request.form.get('security_level')
        access_users = request.form.getlist('access_users')
        
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
                file_path = unique_name
        
        doc = Document(
            title=title, description=description, file_path=file_path,
            document_type=document_type, department=department,
            security_level=security_level, created_by=session['user_id']
        )
        db.session.add(doc)
        db.session.flush()
        
        if security_level != 'normal' and access_users:
            for uid in access_users:
                access = DocumentAccess(document_id=doc.id, user_id=int(uid), can_view=True, can_edit=False)
                db.session.add(access)
        
        db.session.commit()
        log_action(session['user_id'], session['username'], 'إضافة مستند', doc.id, title)
        flash('تمت إضافة المستند بنجاح', 'success')
        return redirect(url_for('index'))
    
    return render_with_base('add_document', users=users, session=session)

@app.route('/view_document/<int:doc_id>')
@login_required
def view_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if not doc.is_accessible_by(session['user_id'], session['role']):
        flash('ليس لديك صلاحية لعرض هذا المستند', 'error')
        return redirect(url_for('index'))
    
    log_action(session['user_id'], session['username'], 'عرض مستند', doc.id, doc.title)
    return render_with_base('view_document', document=doc, session=session)

@app.route('/edit_document/<int:doc_id>', methods=['GET', 'POST'])
@login_required
def edit_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if not doc.can_edit_by(session['user_id'], session['role']):
        flash('ليس لديك صلاحية لتعديل هذا المستند', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        doc.title = request.form.get('title')
        doc.description = request.form.get('description')
        doc.document_type = request.form.get('document_type')
        doc.department = request.form.get('department')
        
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                if doc.file_path:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], doc.file_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(file.filename)
                unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
                doc.file_path = unique_name
        
        db.session.commit()
        log_action(session['user_id'], session['username'], 'تعديل مستند', doc.id, doc.title)
        flash('تم تعديل المستند بنجاح', 'success')
        return redirect(url_for('view_document', doc_id=doc.id))
    
    return render_with_base('edit_document', document=doc, session=session)

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    doc_type = request.args.get('type', '')
    department = request.args.get('department', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    results = []
    if query or doc_type or department or from_date or to_date:
        search_query = Document.query
        if query:
            search_query = search_query.filter(
                (Document.title.contains(query)) | (Document.description.contains(query))
            )
        if doc_type:
            search_query = search_query.filter_by(document_type=doc_type)
        if department:
            search_query = search_query.filter_by(department=department)
        if from_date:
            search_query = search_query.filter(Document.created_at >= datetime.strptime(from_date, '%Y-%m-%d'))
        if to_date:
            search_query = search_query.filter(Document.created_at <= datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1))
        
        if session['role'] != 'admin':
            search_query = search_query.filter(
                (Document.security_level == 'normal') |
                (Document.id.in_(db.session.query(DocumentAccess.document_id).filter_by(user_id=session['user_id'])))
            )
        results = search_query.order_by(Document.created_at.desc()).all()
    
    return render_with_base('search', results=results, query=query, doc_type=doc_type, 
                           department=department, from_date=from_date, to_date=to_date, session=session)

@app.route('/manage_users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_with_base('manage_users', users=users, session=session)

@app.route('/add_user', methods=['POST'])
@admin_required
def add_user():
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    password = request.form.get('password')
    role = request.form.get('role')
    
    if User.query.filter_by(username=username).first():
        flash('اسم المستخدم موجود بالفعل', 'error')
        return redirect(url_for('manage_users'))
    
    user = User(username=username, full_name=full_name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    log_action(session['user_id'], session['username'], 'إضافة مستخدم', details=f"المستخدم: {username}")
    flash('تمت إضافة المستخدم بنجاح', 'success')
    return redirect(url_for('manage_users'))

@app.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('لا يمكن حذف حسابك الحالي', 'error')
        return redirect(url_for('manage_users'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    log_action(session['user_id'], session['username'], 'حذف مستخدم', details=f"المستخدم: {user.username}")
    flash('تم حذف المستخدم', 'success')
    return redirect(url_for('manage_users'))

@app.route('/audit_log')
@admin_required
def audit_log():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return render_with_base('audit_log', logs=logs, session=session)

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ======================
# إنشاء قاعدة البيانات والمستخدم الافتراضي
# ======================
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', full_name='مدير النظام', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ تم إنشاء المستخدم admin بكلمة مرور admin123")

# ======================
# تشغيل التطبيق
# ======================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("=" * 50)
    print("🚀 نظام الأرشفة والمراسلات الداخلية")
    print(f"📍 يعمل على: http://localhost:{port}")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
