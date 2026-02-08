# 📧 نظام تسجيل الدخول بالإيميل - التوثيق الكامل

## نظرة عامة

نظام يسمح للمستخدمين بتسجيل الدخول باستخدام بريدهم الإلكتروني بدلاً من Telegram.
يتم إرسال كود تحقق مكون من 6 أرقام إلى البريد الإلكتروني.

**التدفق:**
```
المستخدم يدخل الإيميل → النظام يبحث في Firebase → يولّد كود 6 أرقام 
→ يرسله للإيميل → المستخدم يدخل الكود → تسجيل دخول ناجح
```

---

## 🛠️ خطوات التركيب من الصفر

### الخطوة 1: إضافة إعدادات SMTP في config.py

**الملف:** `config.py`
**المكان:** أضف في نهاية الملف (بعد إعدادات Tabby)

```python
# === إعدادات البريد الإلكتروني (SMTP) ===
# يمكن تغييرها من Render Environment Variables
SMTP_SERVER = os.environ.get("SMTP_SERVER", "mail.privateemail.com")  # Namecheap افتراضي
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))  # منفذ SSL
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "")  # الإيميل
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")  # كلمة المرور
SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "TR Store")  # اسم المرسل
```

---

### الخطوة 2: إضافة imports في routes/auth_routes.py

**الملف:** `routes/auth_routes.py`
**المكان:** في أعلى الملف مع باقي الـ imports

```python
# أضف هذه في أعلى الملف
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD
```

---

### الخطوة 3: إضافة دالة إرسال الإيميل

**الملف:** `routes/auth_routes.py`
**المكان:** أضف قبل الـ routes (قبل @auth_bp.route)

```python
# ==================== نظام تسجيل الدخول بالإيميل ====================

def send_email_otp(to_email, code):
    """إرسال كود التحقق عبر الإيميل"""
    try:
        if not SMTP_EMAIL or not SMTP_PASSWORD:
            print("❌ إعدادات SMTP غير مكتملة")
            return False
            
        msg = MIMEMultipart('alternative')
        msg['From'] = f"TR Store <{SMTP_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = "🔐 كود الدخول - TR Store"

        # تصميم الرسالة HTML
        html_body = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head><meta charset="UTF-8"></head>
        <body style="margin: 0; padding: 0; background-color: #f0f2f5; font-family: 'Segoe UI', Tahoma, sans-serif;">
            <div style="max-width: 500px; margin: 30px auto; background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">🔐 TR Store</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">رمز التحقق الخاص بك</p>
                </div>
                <div style="padding: 40px 30px; text-align: center;">
                    <p style="color: #666; font-size: 16px; margin-bottom: 30px;">مرحباً! 👋<br>استخدم الرمز التالي لتسجيل الدخول:</p>
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; display: inline-block;">
                        <span style="font-size: 36px; font-weight: bold; color: white; letter-spacing: 8px;">{code}</span>
                    </div>
                    <p style="color: #999; font-size: 14px; margin-top: 30px;">⏰ هذا الرمز صالح لمدة <strong>10 دقائق</strong> فقط</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #aaa; font-size: 12px;">⚠️ إذا لم تطلب هذا الرمز، تجاهل هذا الإيميل</p>
                </div>
                <div style="background: #f8f9fa; padding: 20px; text-align: center;">
                    <p style="color: #888; font-size: 12px; margin: 0;">TR Store © 2024</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(f"رمز التحقق: {code}", 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        print(f"📧 محاولة إرسال إيميل إلى: {to_email} عبر {SMTP_SERVER}:{SMTP_PORT}")
        
        # محاولة SSL أولاً (port 465)
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)
                print(f"✅ تم إرسال الإيميل بنجاح إلى: {to_email}")
                return True
        except Exception as ssl_error:
            print(f"⚠️ فشل SSL: {ssl_error}, جاري تجربة TLS...")
            
        # محاولة TLS كخيار ثاني (port 587)
        try:
            with smtplib.SMTP(SMTP_SERVER, 587, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)
                print(f"✅ تم إرسال الإيميل بنجاح (TLS) إلى: {to_email}")
                return True
        except Exception as tls_error:
            print(f"❌ فشل TLS أيضاً: {tls_error}")
            return False
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ خطأ في المصادقة: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ في إرسال الإيميل: {e}")
        return False
```

---

### الخطوة 4: إضافة Endpoint إرسال الكود

**الملف:** `routes/auth_routes.py`
**المكان:** أضف بعد دالة send_email_otp

```python
@auth_bp.route('/api/auth/send-code', methods=['POST'])
def send_code_email():
    """إرسال كود التحقق للإيميل"""
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'بيانات غير صالحة'})
        
    email = data.get('email', '').strip().lower()
    
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'الرجاء إدخال بريد إلكتروني صحيح'})

    try:
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1)
        results = list(query.stream())

        if results:
            user_doc = results[0]
            user_id = user_doc.id
            user_ref = users_ref.document(user_id)
            print(f"✅ تم العثور على المستخدم: {user_id}")
        else:
            return jsonify({'success': False, 'message': 'لا يوجد حساب مرتبط بهذا البريد الإلكتروني'})

        # توليد وحفظ الكود
        new_code = generate_code()
        user_ref.update({
            'verification_code': new_code,
            'code_time': time.time()
        })
        
        # إرسال الإيميل
        if send_email_otp(email, new_code):
            return jsonify({'success': True, 'message': f'✅ تم إرسال الرمز إلى {email}', 'email': email})
        else:
            # إذا فشل الإيميل، نحاول إرسال عبر Telegram
            try:
                user_data = user_doc.to_dict()
                message_text = f"📧 كود التحقق للدخول:\n\n<code>{new_code}</code>\n\n⏰ صالح لمدة 10 دقائق"
                bot.send_message(int(user_id), message_text, parse_mode='HTML')
                return jsonify({'success': True, 'message': '✅ تم إرسال الرمز عبر Telegram', 'email': email})
            except:
                return jsonify({'success': False, 'message': 'فشل الإرسال!'})

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ في النظام'})
```

---

### الخطوة 5: إضافة Endpoint تسجيل الدخول

**الملف:** `routes/auth_routes.py`
**المكان:** أضف بعد send_code_email

```python
@auth_bp.route('/api/auth/login', methods=['POST'])
def login_email():
    """التحقق من الكود وتسجيل الدخول بالإيميل"""
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'بيانات غير صالحة'})
        
    email = data.get('email', '').strip().lower()
    code = data.get('code', '').strip()
    
    if not email or not code:
        return jsonify({'success': False, 'message': 'الرجاء إدخال البريد والكود'})
    
    try:
        query = db.collection('users').where('email', '==', email).limit(1)
        results = list(query.stream())
        
        if not results:
            return jsonify({'success': False, 'message': 'الحساب غير موجود'})
            
        user_doc = results[0]
        user_data = user_doc.to_dict()
        
        # التحقق من انتهاء صلاحية الكود (10 دقائق)
        code_time = user_data.get('code_time', 0)
        if time.time() - code_time > 600:
            return jsonify({'success': False, 'message': 'انتهت صلاحية الكود، اطلب كود جديد'})
        
        # التحقق من الكود
        saved_code = str(user_data.get('verification_code', ''))
        if saved_code == code:
            # تجديد الجلسة للأمان
            regenerate_session()
            
            # دخول ناجح
            session['user_id'] = user_doc.id
            session['user_name'] = user_data.get('username', user_data.get('first_name', 'مستخدم'))
            session['user_email'] = email
            session['logged_in'] = True
            session['login_time'] = time.time()  # ⚠️ مهم جداً لمنع انتهاء الجلسة فوراً!
            session.permanent = True
            session.modified = True
            
            # مسح الكود بعد الاستخدام
            db.collection('users').document(user_doc.id).update({
                'verification_code': None,
                'code_time': None
            })
            
            print(f"✅ تم تسجيل دخول المستخدم: {user_doc.id}")
            return jsonify({'success': True, 'message': 'تم تسجيل الدخول بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'الكود غير صحيح'})
            
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء الدخول'})
```

---

### الخطوة 6: إضافة واجهة المستخدم (HTML + JavaScript)

**الملف:** `templates/categories.html` (أو أي صفحة تسجيل دخول)
**المكان:** داخل modal أو form تسجيل الدخول

#### HTML:
```html
<!-- نموذج إدخال الإيميل -->
<div id="step1" class="step active">
    <form id="emailForm">
        <input type="email" id="loginEmail" placeholder="example@gmail.com" required>
        <button type="submit">إرسال كود التحقق</button>
    </form>
    <div id="emailError" class="error-msg"></div>
</div>

<!-- نموذج إدخال الكود -->
<div id="step2" class="step">
    <form id="verifyForm">
        <input type="text" id="verifyCode" placeholder="أدخل الكود" maxlength="6" required>
        <button type="submit">تأكيد الدخول</button>
    </form>
    <div id="codeError" class="error-msg"></div>
</div>
```

#### JavaScript:
```javascript
// متغير لحفظ الإيميل
window.loginEmail = null;

// إرسال كود التحقق
document.getElementById('emailForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const errorDiv = document.getElementById('emailError');
    
    try {
        const response = await fetch('/api/auth/send-code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email })
        });
        const data = await response.json();
        
        if (data.success) {
            window.loginEmail = email;  // حفظ الإيميل للخطوة التالية
            document.getElementById('step1').classList.remove('active');
            document.getElementById('step2').classList.add('active');
            document.getElementById('verifyCode').focus();
        } else {
            errorDiv.textContent = data.message;
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'خطأ في الاتصال بالسيرفر';
        errorDiv.style.display = 'block';
    }
});

// التحقق من الكود
document.getElementById('verifyForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const code = document.getElementById('verifyCode').value.trim();
    const errorDiv = document.getElementById('codeError');
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                email: window.loginEmail,
                code: code 
            })
        });
        const data = await response.json();
        
        if (data.success) {
            window.loginEmail = null;
            location.reload();  // إعادة تحميل الصفحة
        } else {
            errorDiv.textContent = data.message;
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'خطأ في الاتصال بالسيرفر';
        errorDiv.style.display = 'block';
    }
});
```

---

### الخطوة 7: إعداد Render Environment Variables

اذهب إلى **Render Dashboard** → **Environment** وأضف:

| المتغير | الوصف | مثال |
|---------|-------|------|
| `SMTP_SERVER` | سيرفر البريد | `mail.privateemail.com` |
| `SMTP_PORT` | المنفذ (465 لـ SSL، 587 لـ TLS) | `465` |
| `SMTP_EMAIL` | إيميل المرسل | `tr@gamerstr1.com` |
| `SMTP_PASSWORD` | كلمة المرور | `yourpassword123` |
| `SMTP_FROM_NAME` | اسم المرسل (اختياري) | `TR Store` |

**ملاحظة:** `SMTP_FROM_NAME` اختياري، القيمة الافتراضية `TR Store`

---

### الخطوة 8: إعداد Firebase

1. اذهب إلى **Firebase Console** → **Firestore Database**
2. افتح collection **users**
3. لكل مستخدم، أضف حقل **email**:

```javascript
// Firebase > Firestore > users > {user_id}
{
    "username": "اسم_المستخدم",
    "email": "user@example.com",      // ← أضف هذا الحقل
    "balance": 0.0
}
```

---

## 📁 ملخص الملفات والأماكن

| الملف | ما يجب إضافته | المكان |
|-------|---------------|--------|
| `config.py` | إعدادات SMTP | نهاية الملف |
| `routes/auth_routes.py` | imports | أعلى الملف (سطر 1-15) |
| `routes/auth_routes.py` | دالة `send_email_otp` | قبل الـ routes |
| `routes/auth_routes.py` | `/api/auth/send-code` | بعد الدالة |
| `routes/auth_routes.py` | `/api/auth/login` | بعد send-code |
| `templates/*.html` | HTML + JavaScript | في modal تسجيل الدخول |

---

## � API Endpoints

### إرسال كود التحقق
```
POST /api/auth/send-code
Content-Type: application/json

Request:
{
    "email": "user@example.com"
}

Response (نجاح):
{
    "success": true,
    "message": "✅ تم إرسال الرمز إلى user@example.com",
    "email": "user@example.com"
}

Response (فشل):
{
    "success": false,
    "message": "لا يوجد حساب مرتبط بهذا البريد الإلكتروني"
}
```

### تسجيل الدخول بالكود
```
POST /api/auth/login
Content-Type: application/json

Request:
{
    "email": "user@example.com",
    "code": "123456"
}

Response (نجاح):
{
    "success": true,
    "message": "تم تسجيل الدخول بنجاح"
}

Response (فشل):
{
    "success": false,
    "message": "الكود غير صحيح"
}
```

### إرسال كود بالإيميل (البديل في app.py)

**الملف:** `app.py`
**الميزات الإضافية:**
- Rate Limiting: 3 طلبات/دقيقة
- حفظ الكود في الذاكرة + Firebase
- استخدام `email_service.py`
- Fallback تلقائي لـ Telegram

```
POST /api/send_code_by_email
Content-Type: application/json

Request:
{
    "email": "user@example.com"
}

Response (نجاح - إيميل):
{
    "success": true,
    "message": "✅ تم إرسال كود التحقق إلى user@example.com",
    "user_id": "123456789",
    "method": "email"
}

Response (نجاح - Telegram كبديل):
{
    "success": true,
    "message": "✅ تم إرسال الكود عبر Telegram (خدمة الإيميل غير متاحة)",
    "user_id": "123456789",
    "method": "telegram"
}

Response (فشل):
{
    "success": false,
    "message": "لا يوجد حساب مرتبط بهذا البريد الإلكتروني"
}
```

### مقارنة بين الـ Endpoints

| الميزة | `/api/auth/send-code` | `/api/send_code_by_email` |
|--------|----------------------|---------------------------|
| **الملف** | auth_routes.py | app.py |
| **Rate Limiting** | يدوي (5 محاولات) | `@limiter` (3/دقيقة) |
| **حفظ الكود** | Firebase فقط | ذاكرة + Firebase |
| **خدمة الإيميل** | `send_email_otp()` محلية | `email_service.py` |
| **تصميم الإيميل** | بنفسجي/أبيض | أسود/أخضر نيون |
| **صلاحية الكود** | 10 دقائق | 5 دقائق |
| **Fallback** | Telegram | Telegram |
| **يرجع user_id** | ❌ | ✅ |

**ملاحظة:** يمكنك استخدام أي منهما حسب احتياجك. الأول أبسط، والثاني فيه ميزات أكثر.

---

## 🗄️ بنية Firebase المطلوبة

```javascript
// Firebase > Firestore > users > {user_id}
{
    "username": "Sbras_1",
    "first_name": "سعد",
    "email": "user@example.com",      // ← مطلوب للدخول بالإيميل
    "verification_code": "123456",     // يتم توليده عند الطلب
    "code_time": 1707177600,           // وقت إنشاء الكود (timestamp)
    "balance": 0.0
}
```

---

## 🔒 الأمان

| الميزة | التفاصيل |
|--------|----------|
| صلاحية الكود | 10 دقائق فقط |
| مسح الكود | بعد الاستخدام الناجح |
| SSL/TLS | اتصال مشفر مع SMTP |
| Session Timeout | 30 دقيقة |
| Session Regeneration | تجديد الجلسة عند الدخول |
| Rate Limiting | حماية من المحاولات المتكررة |
| login_time | ⚠️ مهم لمنع انتهاء الجلسة فوراً |

---

## 🔧 استكشاف الأخطاء

### الخطأ: "Username and Password not accepted"
- **السبب**: كلمة مرور SMTP خاطئة
- **الحل**: تحقق من `SMTP_PASSWORD` في Render

### الخطأ: "لا يوجد حساب مرتبط بهذا البريد"
- **السبب**: الإيميل غير موجود في Firebase
- **الحل**: أضف حقل `email` للمستخدم في Firestore

### الخطأ: "انتهت صلاحية الكود"
- **السبب**: مر أكثر من 10 دقائق
- **الحل**: اطلب كود جديد

### الجلسة تنتهي فوراً بعد الدخول
- **السبب**: `login_time` غير موجود في الجلسة
- **الحل**: تأكد من إضافة `session['login_time'] = time.time()`

### الإيميل لا يصل
- **السبب**: إعدادات DNS غير مكتملة (للدومين الخاص)
- **الحل**: تحقق من إضافة MX و SPF records

---

## 📝 ملاحظات مهمة

1. **الكود يدعم** Namecheap Private Email و Gmail
2. **يمكن تغيير مزود SMTP** من Environment Variables فقط
3. **Fallback للتلغرام** إذا فشل إرسال الإيميل
4. **قالب HTML جميل** للإيميل مع تدرج لوني

---

## � الدوال المساعدة المطلوبة

### دالة توليد الكود العشوائي

**الملف:** `utils.py`
**الوظيفة:** توليد كود مكون من 6 أرقام

```python
import random

def generate_code():
    """توليد كود تحقق عشوائي من 6 أرقام"""
    return str(random.randint(100000, 999999))
```

---

### دالة تجديد الجلسة

**الملف:** `utils.py`
**الوظيفة:** تجديد الجلسة للأمان عند تسجيل الدخول (منع Session Fixation Attack)

```python
from flask import session

def regenerate_session():
    """تجديد ID الجلسة لمنع Session Fixation"""
    # حفظ كل البيانات الحالية
    old_data = dict(session)
    
    # مسح الجلسة القديمة (يولّد session ID جديد)
    session.clear()
    
    # إعادة كل البيانات للجلسة الجديدة
    session.update(old_data)
    
    # إجبار حفظ التغييرات
    session.modified = True
```

**ملاحظة أمنية:** هذه الدالة تُستدعى عند تسجيل الدخول الناجح لمنع هجمات Session Fixation حيث يحاول المهاجم تثبيت session ID معين قبل تسجيل الدخول.

---

## ⚙️ إعدادات Session في config.py

**الملف:** `config.py`
**المكان:** أضف مع الإعدادات الأخرى

```python
from datetime import timedelta

# === إعدادات الجلسة ===
SESSION_CONFIG = {
    'SESSION_COOKIE_SECURE': True,  # HTTPS فقط
    'SESSION_COOKIE_HTTPONLY': True,  # منع JavaScript من الوصول
    'SESSION_COOKIE_SAMESITE': 'Lax',  # حماية CSRF
    'PERMANENT_SESSION_LIFETIME': timedelta(minutes=30),  # 30 دقيقة
    'SESSION_COOKIE_NAME': 'tr_session',
}
```

**ثم في `app.py`:**
```python
from config import SESSION_CONFIG

app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key")
app.config.update(SESSION_CONFIG)
```

---

## 🔗 تسجيل Blueprint في app.py

**الملف:** `app.py`
**المكان:** مع باقي الـ blueprints

```python
# في أعلى الملف - Import
from routes.auth_routes import auth_bp

# بعد إنشاء app - Registration
app.register_blueprint(auth_bp)
```

**ملاحظة:** تأكد أن ملف `routes/auth_routes.py` يحتوي على:
```python
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
```

---

## 🎨 CSS للواجهة

**الملف:** `templates/categories.html` أو `static/css/style.css`

```css
/* === نموذج تسجيل الدخول === */
.login-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.login-container {
    background: white;
    border-radius: 20px;
    padding: 30px;
    width: 90%;
    max-width: 400px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

/* الخطوات */
.step {
    display: none;
}

.step.active {
    display: block;
}

/* حقول الإدخال */
.login-container input {
    width: 100%;
    padding: 15px;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    font-size: 16px;
    margin-bottom: 15px;
    transition: border-color 0.3s;
}

.login-container input:focus {
    border-color: #667eea;
    outline: none;
}

/* حقل الكود */
.code-input {
    text-align: center;
    font-size: 24px !important;
    letter-spacing: 8px;
    font-weight: bold;
}

/* الأزرار */
.login-container button {
    width: 100%;
    padding: 15px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

.login-container button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.login-container button:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
}

/* رسائل الخطأ */
.error-msg {
    background: #fee;
    color: #c00;
    padding: 10px 15px;
    border-radius: 8px;
    margin-top: 10px;
    display: none;
    font-size: 14px;
}

/* رسائل النجاح */
.success-msg {
    background: #efe;
    color: #080;
    padding: 10px 15px;
    border-radius: 8px;
    margin-top: 10px;
    display: none;
    font-size: 14px;
}

/* العد التنازلي */
.countdown {
    text-align: center;
    color: #666;
    font-size: 14px;
    margin-top: 15px;
}

.countdown span {
    color: #667eea;
    font-weight: bold;
}
```

---

## 🛡️ نظام الحماية من المحاولات المتكررة (Rate Limiting)

**الملف:** `routes/auth_routes.py`
**الوظيفة:** حماية من هجمات Brute Force على تسجيل الدخول

### كيف يعمل؟

1. **تتبع المحاولات الفاشلة** بناءً على IP
2. **5 محاولات فاشلة** → حظر 15 دقيقة
3. **إعادة تعيين** العداد بعد 15 دقيقة من آخر محاولة
4. **مسح العداد** عند تسجيل دخول ناجح

### الكود:

```python
# تخزين مؤقت لمحاولات الدخول الفاشلة
login_failed_attempts = {}  # {ip: {'count': 0, 'blocked_until': 0, 'last_attempt': 0}}

def check_login_rate_limit():
    """التحقق من rate limit لتسجيل الدخول"""
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    current_time = time.time()
    
    if client_ip in login_failed_attempts:
        attempt_data = login_failed_attempts[client_ip]
        
        # التحقق من الحظر
        if attempt_data.get('blocked_until', 0) > current_time:
            remaining = int(attempt_data['blocked_until'] - current_time)
            return False, f'⛔ تم حظرك مؤقتاً. حاول بعد {remaining} ثانية'
        
        # إعادة تعيين العداد بعد 15 دقيقة من آخر محاولة
        if current_time - attempt_data.get('last_attempt', 0) > 900:
            login_failed_attempts[client_ip] = {'count': 0, 'blocked_until': 0, 'last_attempt': current_time}
    
    return True, None

def record_failed_login():
    """تسجيل محاولة دخول فاشلة"""
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    current_time = time.time()
    
    if client_ip not in login_failed_attempts:
        login_failed_attempts[client_ip] = {'count': 0, 'blocked_until': 0, 'last_attempt': current_time}
    
    login_failed_attempts[client_ip]['count'] += 1
    login_failed_attempts[client_ip]['last_attempt'] = current_time
    
    attempts = login_failed_attempts[client_ip]['count']
    
    # حظر بعد 5 محاولات فاشلة لمدة 15 دقيقة
    if attempts >= 5:
        login_failed_attempts[client_ip]['blocked_until'] = current_time + 900  # 15 دقيقة
        return 0
    
    return 5 - attempts  # عدد المحاولات المتبقية

def reset_login_attempts():
    """إعادة تعيين عداد المحاولات بعد دخول ناجح"""
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    if client_ip in login_failed_attempts:
        del login_failed_attempts[client_ip]
```

### استخدام في الـ Endpoint:

```python
@auth_bp.route('/login', methods=['POST'])
def login():
    # 🔒 التحقق من Rate Limit أولاً
    allowed, error_msg = check_login_rate_limit()
    if not allowed:
        return jsonify({'success': False, 'message': error_msg})
    
    # ... باقي الكود ...
    
    if login_failed:
        remaining = record_failed_login()
        return jsonify({'success': False, 'message': f'كود خاطئ. متبقي {remaining} محاولات'})
    
    # عند النجاح
    reset_login_attempts()
```

---

## 📧 خدمة البريد الإلكتروني المنفصلة (اختياري)

**الملف:** `services/email_service.py`
**الوظيفة:** خدمة إيميل متقدمة مع تصميم مختلف (أسود/أخضر)

### ملاحظة:
هذا الملف موجود كبديل/إضافة لـ `send_email_otp()` في `auth_routes.py`. يمكنك استخدام أي منهما.

### الدوال المتوفرة:

| الدالة | الوظيفة |
|--------|--------|
| `is_email_configured()` | التحقق من إعداد SMTP |
| `send_otp_email(to, code, name)` | إرسال كود التحقق |
| `send_notification_email(to, subject, msg)` | إرسال إشعار عام |

### الاختلاف عن auth_routes:

| البند | `auth_routes.py` | `email_service.py` |
|-------|------------------|--------------------|
| التصميم | بنفسجي/أبيض | أسود/أخضر نيون |
| صلاحية الكود | 10 دقائق | 5 دقائق (في النص) |
| الاتصال | SSL ثم TLS | TLS فقط |

### كود مختصر:

```python
# services/email_service.py
from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, SMTP_FROM_NAME

def is_email_configured():
    """التحقق من إعداد خدمة البريد الإلكتروني"""
    return bool(SMTP_EMAIL and SMTP_PASSWORD)

def send_otp_email(to_email, otp_code, user_name="عميلنا العزيز"):
    """إرسال كود التحقق عبر البريد الإلكتروني"""
    if not is_email_configured():
        return False
    
    # ... إعداد الرسالة مع تصميم HTML ...
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
    
    return True
```

---

## 🌐 إعداد DNS لـ Namecheap Private Email

إذا كنت تستخدم دومين خاص (مثل `gamerstr1.com`)، يجب إضافة سجلات DNS:

### الخطوات:

1. اذهب إلى **Namecheap** → **Dashboard**
2. اضغط على **Domain List**
3. بجانب الدومين اضغط **Manage**
4. اضغط على **Advanced DNS**
5. أضف السجلات التالية:

### سجلات MX (للاستقبال):

| Type | Host | Value | Priority |
|------|------|-------|----------|
| MX | @ | mx1.privateemail.com | 10 |
| MX | @ | mx2.privateemail.com | 10 |

### سجل SPF (للإرسال):

| Type | Host | Value |
|------|------|-------|
| TXT | @ | v=spf1 include:spf.privateemail.com ~all |

### سجل DKIM (اختياري - لتحسين التسليم):

| Type | Host | Value |
|------|------|-------|
| TXT | default._domainkey | (احصل عليه من Namecheap Email Settings) |

### ملاحظات:
- انتظر **1-4 ساعات** حتى تنتشر الإعدادات
- يمكنك التحقق من https://mxtoolbox.com/

---

## 📁 الملفات المتعلقة

```
├── config.py                    # إعدادات SMTP + Session + SMTP_FROM_NAME
├── utils.py                     # generate_code() + regenerate_session()
├── app.py                       # تسجيل Blueprint + Session config
├── routes/auth_routes.py        # API endpoints + إرسال الإيميل + Rate Limiting
├── services/email_service.py    # خدمة إيميل بديلة (تصميم أسود/أخضر)
├── templates/categories.html    # واجهة المستخدم
└── static/css/style.css         # التنسيقات (اختياري)
```

---

## ✅ قائمة التحقق قبل التشغيل

### الإعدادات:
- [ ] إضافة إعدادات SMTP في `config.py`
- [ ] إضافة `SMTP_FROM_NAME` في `config.py`
- [ ] إضافة إعدادات Session في `config.py`

### الدوال المساعدة:
- [ ] إضافة `generate_code()` في `utils.py`
- [ ] إضافة `regenerate_session()` في `utils.py`

### نظام المصادقة:
- [ ] إضافة imports في `routes/auth_routes.py`
- [ ] إضافة Rate Limiting (check, record, reset)
- [ ] إضافة دالة `send_email_otp()` في `routes/auth_routes.py`
- [ ] إضافة endpoint `/api/auth/send-code`
- [ ] إضافة endpoint `/api/auth/login`

### التكامل:
- [ ] تسجيل Blueprint في `app.py`
- [ ] تطبيق Session config في `app.py`

### الواجهة:
- [ ] إضافة HTML + JavaScript في الواجهة
- [ ] إضافة CSS للتنسيق

### البيئة:
- [ ] إعداد Environment Variables في Render (5 متغيرات)
- [ ] إضافة حقل `email` للمستخدمين في Firebase
- [ ] إعداد DNS (إذا كان دومين خاص)

---

---

# 📱 نظام تسجيل الدخول بالجوال (WhatsApp/SMS) - Authentica API

## نظرة عامة

نظام يسمح للمستخدمين بتسجيل الدخول باستخدام رقم الجوال بدلاً من Telegram.
يتم إرسال كود تحقق مكون من 6 أرقام عبر **WhatsApp** أو **SMS** باستخدام خدمة **Authentica API**.

**التدفق:**
```
المستخدم يدخل رقم الجوال → النظام يبحث في Firebase → يولّد كود 6 أرقام 
→ يرسله عبر WhatsApp (Authentica) → المستخدم يدخل الكود 
→ التحقق عبر Authentica API → تسجيل دخول ناجح
```

**ميزات الخدمة:**
- ✅ إرسال OTP عبر WhatsApp (أسرع وأوفر)
- ✅ إرسال OTP عبر SMS كبديل
- ✅ التحقق من الكود عبر API (يظهر "Verified" في لوحة التحكم)
- ✅ الاستعلام عن الرصيد
- ✅ دعم الأرقام السعودية (05, +966, 966)

---

## 🛠️ خطوات التركيب من الصفر

### الخطوة 1: إضافة إعدادات Authentica في config.py

**الملف:** `config.py`
**المكان:** أضف في نهاية الملف (بعد إعدادات SMTP)

```python
# === إعدادات Authentica API (WhatsApp/SMS OTP) ===
# احصل على API Key من: https://portal.authentica.sa/settings/apikeys/
AUTHENTICA_API_KEY = os.environ.get("AUTHENTICA_API_KEY", "")
AUTHENTICA_API_URL = "https://api.authentica.sa/api/v2"
AUTHENTICA_DEFAULT_METHOD = os.environ.get("AUTHENTICA_METHOD", "whatsapp")  # whatsapp أو sms
AUTHENTICA_TEMPLATE_ID = os.environ.get("AUTHENTICA_TEMPLATE_ID", "1")  # رقم القالب
```

**شرح المتغيرات:**

| المتغير | الوصف | القيمة الافتراضية |
|---------|-------|-------------------|
| `AUTHENTICA_API_KEY` | مفتاح API من Authentica Portal | (فارغ) |
| `AUTHENTICA_API_URL` | رابط API الثابت | `https://api.authentica.sa/api/v2` |
| `AUTHENTICA_DEFAULT_METHOD` | طريقة الإرسال الافتراضية | `whatsapp` |
| `AUTHENTICA_TEMPLATE_ID` | رقم قالب الرسالة | `1` |

---

### الخطوة 2: إنشاء خدمة Authentica

**الملف:** `services/authentica_service.py` ← **ملف جديد**
**المكان:** أنشئ مجلد `services` إذا لم يكن موجوداً

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة Authentica للتحقق عبر WhatsApp/SMS
========================================
إرسال والتحقق من OTP عبر Authentica API
"""

import requests
import logging
from config import (
    AUTHENTICA_API_KEY,
    AUTHENTICA_API_URL,
    AUTHENTICA_DEFAULT_METHOD,
    AUTHENTICA_TEMPLATE_ID
)

logger = logging.getLogger(__name__)
```

---

### الخطوة 3: دالة التحقق من الإعداد

**الملف:** `services/authentica_service.py`
**المكان:** بعد الـ imports

```python
def is_authentica_configured():
    """
    التحقق من إعداد خدمة Authentica
    
    Returns:
        bool: True إذا كان API Key موجود
    
    الاستخدام:
        if is_authentica_configured():
            # الخدمة جاهزة
        else:
            # استخدم طريقة بديلة (Telegram)
    """
    return bool(AUTHENTICA_API_KEY)
```

---

### الخطوة 4: دالة تنسيق رقم الجوال

**الملف:** `services/authentica_service.py`
**المكان:** بعد `is_authentica_configured()`

```python
def format_phone_number(phone):
    """
    تنسيق رقم الجوال للصيغة الدولية المطلوبة من Authentica
    
    Args:
        phone (str): رقم الجوال بأي صيغة
            - 05xxxxxxxx (صيغة محلية)
            - 5xxxxxxxx (بدون صفر)
            - 966xxxxxxx (بدون +)
            - +966xxxxxxx (صيغة دولية)
    
    Returns:
        str: الرقم بالصيغة الدولية (+966xxxxxxxxx)
        None: إذا كان الرقم فارغ
    
    أمثلة:
        >>> format_phone_number("0501234567")
        '+966501234567'
        
        >>> format_phone_number("501234567")
        '+966501234567'
        
        >>> format_phone_number("+966501234567")
        '+966501234567'
    """
    if not phone:
        return None
    
    # إزالة المسافات والرموز
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    # إذا بدأ بـ 05 → تحويل لـ +966
    if phone.startswith("05"):
        phone = "+966" + phone[1:]
    # إذا بدأ بـ 5 فقط → إضافة +966
    elif phone.startswith("5") and len(phone) == 9:
        phone = "+966" + phone
    # إذا بدأ بـ 966 بدون + → إضافة +
    elif phone.startswith("966"):
        phone = "+" + phone
    # إذا لم يبدأ بـ + → إضافتها
    elif not phone.startswith("+"):
        phone = "+" + phone
    
    return phone
```

---

### الخطوة 5: دالة إرسال OTP

**الملف:** `services/authentica_service.py`
**المكان:** بعد `format_phone_number()`

```python
def send_otp_whatsapp(phone, otp_code=None, method=None):
    """
    إرسال كود OTP عبر WhatsApp أو SMS
    
    Args:
        phone (str): رقم الجوال (أي صيغة)
        otp_code (str, optional): كود OTP مخصص
            - إذا لم يُحدد: Authentica يولد كود تلقائياً
            - إذا حُدد: يُرسل الكود المحدد
        method (str, optional): طريقة الإرسال
            - 'whatsapp': إرسال عبر واتساب (افتراضي)
            - 'sms': إرسال رسالة نصية
    
    Returns:
        dict: {
            'success': bool,      # هل نجح الإرسال
            'message': str,       # رسالة للمستخدم
            'otp': str or None,   # الكود إذا كان مخصص
            'phone': str          # الرقم بالصيغة الدولية
        }
    
    الاستخدام:
        # إرسال بكود مخصص
        result = send_otp_whatsapp("0501234567", otp_code="123456")
        
        # إرسال بدون كود (Authentica يولد)
        result = send_otp_whatsapp("0501234567")
        
        # إرسال عبر SMS
        result = send_otp_whatsapp("0501234567", method="sms")
    
    ملاحظة:
        - يتطلب إعداد AUTHENTICA_API_KEY
        - القالب يجب أن يكون مفعّل في لوحة تحكم Authentica
    """
    if not is_authentica_configured():
        logger.error("❌ Authentica API Key غير مُعد")
        return {'success': False, 'message': 'خدمة الرسائل غير مُعدة', 'otp': None}
    
    # تنسيق رقم الجوال
    formatted_phone = format_phone_number(phone)
    if not formatted_phone:
        return {'success': False, 'message': 'رقم الجوال غير صحيح', 'otp': None}
    
    # تحديد طريقة الإرسال
    send_method = method or AUTHENTICA_DEFAULT_METHOD
    
    try:
        # إعداد الطلب
        headers = {
            'X-Authorization': AUTHENTICA_API_KEY,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'method': send_method,
            'phone': formatted_phone,
            'template_id': AUTHENTICA_TEMPLATE_ID
        }
        
        # إضافة OTP مخصص إذا تم تحديده
        if otp_code:
            payload['otp'] = str(otp_code)
        
        logger.info(f"📤 إرسال OTP عبر {send_method} إلى {formatted_phone}")
        
        # إرسال الطلب
        response = requests.post(
            f"{AUTHENTICA_API_URL}/send-otp",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            logger.info(f"✅ تم إرسال OTP بنجاح عبر {send_method}")
            return {
                'success': True,
                'message': f'تم إرسال الكود عبر {"واتساب" if send_method == "whatsapp" else "رسالة نصية"}',
                'otp': otp_code,  # نرجع الكود إذا كان مخصص
                'phone': formatted_phone
            }
        else:
            error_msg = result.get('message', 'فشل إرسال الكود')
            logger.error(f"❌ فشل إرسال OTP: {error_msg}")
            return {'success': False, 'message': error_msg, 'otp': None}
            
    except requests.exceptions.Timeout:
        logger.error("❌ انتهت مهلة الاتصال بـ Authentica")
        return {'success': False, 'message': 'انتهت مهلة الاتصال، حاول مرة أخرى', 'otp': None}
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ خطأ في الاتصال: {e}")
        return {'success': False, 'message': 'خطأ في الاتصال بالخدمة', 'otp': None}
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع: {e}")
        return {'success': False, 'message': 'حدث خطأ غير متوقع', 'otp': None}
```

---

### الخطوة 6: دالة التحقق من OTP

**الملف:** `services/authentica_service.py`
**المكان:** بعد `send_otp_whatsapp()`

```python
def verify_otp_authentica(phone, otp_code):
    """
    التحقق من كود OTP عبر Authentica API
    
    ⚠️ مهم: هذه الدالة ترسل طلب التحقق إلى Authentica
    حتى يظهر "Verified" في لوحة التحكم بدلاً من "Not Verified"
    
    Args:
        phone (str): رقم الجوال (أي صيغة)
        otp_code (str): الكود المدخل من المستخدم
    
    Returns:
        dict: {
            'success': bool,   # هل الكود صحيح
            'message': str     # رسالة للمستخدم
        }
    
    الاستخدام:
        result = verify_otp_authentica("0501234567", "123456")
        if result['success']:
            # الكود صحيح - أكمل تسجيل الدخول
        else:
            # الكود خاطئ
    
    ملاحظة:
        - يجب استدعاء هذه الدالة عند التحقق من الكود
        - بدونها سيظهر "Not Verified" في لوحة تحكم Authentica
    """
    if not is_authentica_configured():
        return {'success': False, 'message': 'خدمة التحقق غير مُعدة'}
    
    formatted_phone = format_phone_number(phone)
    if not formatted_phone:
        return {'success': False, 'message': 'رقم الجوال غير صحيح'}
    
    try:
        headers = {
            'X-Authorization': AUTHENTICA_API_KEY,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'phone': formatted_phone,
            'otp': str(otp_code)
        }
        
        logger.info(f"🔍 التحقق من OTP للرقم {formatted_phone}")
        
        response = requests.post(
            f"{AUTHENTICA_API_URL}/verify-otp",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        result = response.json()
        
        # ملاحظة: Authentica ترجع 'status' وليس 'success'
        if response.status_code == 200 and result.get('status'):
            logger.info("✅ تم التحقق من OTP بنجاح")
            return {'success': True, 'message': 'تم التحقق بنجاح'}
        else:
            error_msg = result.get('message', 'الكود غير صحيح')
            logger.warning(f"⚠️ فشل التحقق: {error_msg}")
            return {'success': False, 'message': error_msg}
            
    except Exception as e:
        logger.error(f"❌ خطأ في التحقق: {e}")
        return {'success': False, 'message': 'حدث خطأ أثناء التحقق'}
```

---

### الخطوة 7: دالة الاستعلام عن الرصيد

**الملف:** `services/authentica_service.py`
**المكان:** في نهاية الملف

```python
def get_authentica_balance():
    """
    الاستعلام عن رصيد حساب Authentica
    
    Returns:
        dict: {
            'success': bool,    # هل نجح الاستعلام
            'balance': int,     # الرصيد (عدد الرسائل المتبقية)
            'message': str      # رسالة
        }
    
    الاستخدام:
        result = get_authentica_balance()
        if result['success']:
            print(f"الرصيد: {result['balance']} رسالة")
    """
    if not is_authentica_configured():
        return {'success': False, 'balance': 0, 'message': 'الخدمة غير مُعدة'}
    
    try:
        headers = {
            'X-Authorization': AUTHENTICA_API_KEY,
            'Accept': 'application/json'
        }
        
        response = requests.get(
            f"{AUTHENTICA_API_URL}/balance",
            headers=headers,
            timeout=15
        )
        
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            balance = result.get('data', {}).get('balance', 0)
            return {'success': True, 'balance': balance, 'message': 'تم جلب الرصيد'}
        else:
            return {'success': False, 'balance': 0, 'message': 'فشل جلب الرصيد'}
            
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الرصيد: {e}")
        return {'success': False, 'balance': 0, 'message': 'خطأ في الاتصال'}
```

---

### الخطوة 8: إضافة imports في auth_routes.py

**الملف:** `routes/auth_routes.py`
**المكان:** في أعلى الملف مع باقي الـ imports

```python
# === Authentica API (WhatsApp/SMS OTP) ===
try:
    from services.authentica_service import (
        is_authentica_configured,
        send_otp_whatsapp,
        verify_otp_authentica,
        format_phone_number
    )
    AUTHENTICA_AVAILABLE = is_authentica_configured()
    print(f"📱 Authentica Service: {'✅ متاح' if AUTHENTICA_AVAILABLE else '❌ غير مُعد'}")
except ImportError as e:
    print(f"⚠️ Authentica service not available: {e}")
    AUTHENTICA_AVAILABLE = False
```

**شرح:**
- `try/except` للتعامل مع حالة عدم وجود الملف
- `AUTHENTICA_AVAILABLE` متغير عام للتحقق من توفر الخدمة
- طباعة حالة الخدمة عند بدء التشغيل

---

### الخطوة 9: Endpoint إرسال كود الجوال

**الملف:** `routes/auth_routes.py`
**المكان:** أضف بعد endpoints الإيميل

```python
@auth_bp.route('/api/auth/send-code-phone', methods=['POST'])
def send_code_phone():
    """
    إرسال كود التحقق للجوال عبر WhatsApp
    
    Request Body:
        {
            "phone": "0501234567"  // رقم الجوال
        }
    
    Response (نجاح):
        {
            "success": true,
            "message": "تم إرسال الكود عبر واتساب",
            "user_id": "123456789"
        }
    
    Response (فشل):
        {
            "success": false,
            "message": "سبب الفشل"
        }
    
    التدفق:
        1. التحقق من توفر Authentica
        2. البحث عن المستخدم بالجوال
        3. توليد كود 6 أرقام
        4. حفظ الكود في Firebase
        5. إرسال عبر Authentica
        6. Fallback لـ Telegram إذا فشل
    """
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'بيانات غير صالحة'})
    
    # === معالجة البيانات ===
    phone = data.get('phone', '')
    if isinstance(phone, dict):
        phone = phone.get('phone', '') or ''
    phone = str(phone).strip()
    
    if not phone:
        return jsonify({'success': False, 'message': 'الرجاء إدخال رقم الجوال'})
    
    # === التحقق من توفر Authentica ===
    if not AUTHENTICA_AVAILABLE:
        return jsonify({'success': False, 'message': 'خدمة الرسائل غير متاحة حالياً'})
    
    try:
        # === البحث عن المستخدم ===
        users_ref = db.collection('users')
        user_id = None
        user_doc = None
        
        # تجربة صيغ مختلفة للرقم
        search_phones = [phone]
        if phone.startswith('05'):
            search_phones.append('+966' + phone[1:])
        elif phone.startswith('+966'):
            search_phones.append('0' + phone[4:])
        elif phone.startswith('966'):
            search_phones.append('+' + phone)
            search_phones.append('0' + phone[3:])
        
        for search_phone in search_phones:
            query = users_ref.where('phone', '==', search_phone).limit(1)
            results = list(query.stream())
            if results:
                user_doc = results[0]
                user_id = user_doc.id
                print(f"✅ تم العثور على المستخدم: {user_id} بالرقم {search_phone}")
                break
        
        if not user_id:
            return jsonify({'success': False, 'message': 'لا يوجد حساب مرتبط بهذا الرقم'})
        
        # === توليد وحفظ الكود ===
        new_code = generate_code()
        users_ref.document(user_id).update({
            'verification_code': new_code,
            'code_time': time.time()
        })
        
        # === إرسال عبر Authentica ===
        result = send_otp_whatsapp(phone, otp_code=new_code)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', 'تم إرسال الكود'),
                'user_id': user_id
            })
        
        # === Fallback لـ Telegram ===
        try:
            message_text = f"📱 كود التحقق:\n\n<code>{new_code}</code>\n\n⏰ صالح 10 دقائق"
            bot.send_message(int(user_id), message_text, parse_mode='HTML')
            return jsonify({
                'success': True,
                'message': '✅ تم إرسال الكود عبر Telegram',
                'user_id': user_id
            })
        except Exception as tg_error:
            print(f"❌ فشل Telegram أيضاً: {tg_error}")
            return jsonify({'success': False, 'message': 'فشل إرسال الكود'})
        
    except Exception as e:
        print(f"❌ Phone Send Code Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'حدث خطأ في النظام'})
```

---

### الخطوة 10: Endpoint تسجيل الدخول بالجوال

**الملف:** `routes/auth_routes.py`
**المكان:** بعد `send_code_phone`

```python
@auth_bp.route('/api/auth/login-phone', methods=['POST'])
def login_phone():
    """
    التحقق من الكود وتسجيل الدخول بالجوال
    
    Request Body:
        {
            "phone": "0501234567",   // رقم الجوال
            "code": "123456",        // الكود المدخل
            "user_id": "123456789"   // (اختياري) معرف المستخدم
        }
    
    Response (نجاح):
        {
            "success": true,
            "message": "تم تسجيل الدخول بنجاح"
        }
    
    التدفق:
        1. معالجة البيانات المدخلة
        2. البحث عن المستخدم (بـ user_id أو الجوال)
        3. التحقق من صلاحية الكود (10 دقائق)
        4. التحقق عبر Authentica API ← مهم!
        5. إنشاء الجلسة
        6. مسح الكود
    """
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'بيانات غير صالحة'})
    
    # === معالجة البيانات ===
    phone = data.get('phone', '')
    code = data.get('code', '')
    user_id = data.get('user_id', '')
    
    # التأكد من أن البيانات strings (حماية من dict)
    if isinstance(phone, dict):
        phone = phone.get('phone', '') or ''
    if isinstance(code, dict):
        code = code.get('code', '') or ''
    if isinstance(user_id, dict):
        user_id = user_id.get('user_id', '') or ''
    
    phone = str(phone).strip()
    code = str(code).strip()
    user_id = str(user_id).strip()
    
    if not code:
        return jsonify({'success': False, 'message': 'الرجاء إدخال الكود'})
    
    try:
        # === البحث عن المستخدم ===
        if not user_id and phone:
            users_ref = db.collection('users')
            search_phones = [phone]
            if phone.startswith('05'):
                search_phones.append('+966' + phone[1:])
            elif phone.startswith('+966'):
                search_phones.append('0' + phone[4:])
            
            for search_phone in search_phones:
                query = users_ref.where('phone', '==', search_phone).limit(1)
                results = list(query.stream())
                if results:
                    user_id = results[0].id
                    break
        
        if not user_id:
            return jsonify({'success': False, 'message': 'الحساب غير موجود'})
        
        # === جلب بيانات المستخدم ===
        user_doc = db.collection('users').document(str(user_id)).get()
        if not user_doc.exists:
            return jsonify({'success': False, 'message': 'الحساب غير موجود'})
        
        user_data = user_doc.to_dict()
        
        # === التحقق من الصلاحية ===
        code_time = user_data.get('code_time', 0)
        if time.time() - code_time > 600:  # 10 دقائق
            return jsonify({'success': False, 'message': 'انتهت صلاحية الكود، اطلب كود جديد'})
        
        # === ⚠️ التحقق عبر Authentica API ===
        # مهم جداً: بدون هذا سيظهر "Not Verified" في لوحة التحكم
        if AUTHENTICA_AVAILABLE:
            verify_result = verify_otp_authentica(phone, code)
            if not verify_result.get('success'):
                # Fallback للتحقق المحلي
                saved_code = str(user_data.get('verification_code', ''))
                if saved_code != code:
                    return jsonify({'success': False, 'message': 'الكود غير صحيح'})
                print(f"⚠️ Authentica verify failed, used local verification")
            else:
                print(f"✅ Authentica verified OTP successfully")
        else:
            # التحقق المحلي فقط
            saved_code = str(user_data.get('verification_code', ''))
            if saved_code != code:
                return jsonify({'success': False, 'message': 'الكود غير صحيح'})
        
        # === ✅ تسجيل دخول ناجح ===
        regenerate_session()
        
        session['user_id'] = user_id
        session['user_name'] = user_data.get('username', user_data.get('first_name', 'مستخدم'))
        session['user_phone'] = phone
        session['logged_in'] = True
        session['login_time'] = time.time()
        session.permanent = True
        session.modified = True
        
        # === مسح الكود ===
        db.collection('users').document(str(user_id)).update({
            'verification_code': None,
            'code_time': None
        })
        
        print(f"✅ تم تسجيل دخول المستخدم بالجوال: {user_id}")
        return jsonify({'success': True, 'message': 'تم تسجيل الدخول بنجاح'})
        
    except Exception as e:
        print(f"❌ Phone Login Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء الدخول'})
```

---

### الخطوة 11: تحسين Endpoint تسجيل الدخول العام

**الملف:** `routes/auth_routes.py`
**الدالة:** `/api/auth/login`
**التحسين:** دعم البحث بالجوال بالإضافة للإيميل

```python
@auth_bp.route('/api/auth/login', methods=['POST'])
def login_email():
    """
    التحقق من الكود وتسجيل الدخول (يدعم الإيميل والجوال)
    
    Request Body:
        {
            "email": "user@example.com",  // الإيميل (اختياري)
            "phone": "0501234567",        // الجوال (اختياري)
            "user_id": "123456789",       // معرف المستخدم (اختياري)
            "code": "123456"              // الكود (مطلوب)
        }
    
    ملاحظة: يجب تمرير واحد على الأقل: email أو phone أو user_id
    
    طريقة البحث:
        1. إذا وُجد email → بحث بالإيميل
        2. إذا وُجد user_id → بحث مباشر
        3. إذا وُجد phone → بحث بالجوال (صيغ متعددة)
    """
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'بيانات غير صالحة'})
    
    # معالجة البيانات
    if isinstance(data, dict):
        email = data.get('email', '').strip().lower() if isinstance(data.get('email'), str) else ''
        code = data.get('code', '').strip() if isinstance(data.get('code'), str) else ''
        phone = data.get('phone', '').strip() if isinstance(data.get('phone'), str) else ''
        user_id = data.get('user_id', '').strip() if isinstance(data.get('user_id'), str) else ''
    else:
        return jsonify({'success': False, 'message': 'بيانات غير صالحة'})
    
    if not code:
        return jsonify({'success': False, 'message': 'الرجاء إدخال الكود'})
    
    try:
        user_doc = None
        
        # البحث بالإيميل
        if email:
            query = db.collection('users').where('email', '==', email).limit(1)
            results = list(query.stream())
            if results:
                user_doc = results[0]
        
        # البحث بـ user_id
        if not user_doc and user_id:
            doc = db.collection('users').document(str(user_id)).get()
            if doc.exists:
                user_doc = doc
        
        # البحث بالجوال (صيغ متعددة)
        if not user_doc and phone:
            search_phones = [phone]
            if phone.startswith('05'):
                search_phones.append('+966' + phone[1:])
            elif phone.startswith('+966'):
                search_phones.append('0' + phone[4:])
            elif phone.startswith('966'):
                search_phones.append('+' + phone)
                search_phones.append('0' + phone[3:])
            
            for search_phone in search_phones:
                query = db.collection('users').where('phone', '==', search_phone).limit(1)
                results = list(query.stream())
                if results:
                    user_doc = results[0]
                    break
        
        if not user_doc:
            return jsonify({'success': False, 'message': 'الحساب غير موجود'})
        
        # ... باقي الكود (التحقق من الكود والجلسة) ...
```

---

### الخطوة 12: الواجهة - HTML

**الملف:** `templates/categories.html`
**المكان:** داخل modal تسجيل الدخول

```html
<!-- ==================== قسم الجوال ==================== -->
<div id="phoneSection" class="auth-section">
    <h4 class="section-title">📱 تسجيل الدخول بالجوال</h4>
    
    <!-- الخطوة 1: إدخال رقم الجوال -->
    <div id="phoneStep1" class="step active">
        <form id="phoneForm">
            <div class="input-group">
                <input type="tel" 
                       id="loginPhone" 
                       placeholder="05xxxxxxxx" 
                       required
                       pattern="[0-9]{10}"
                       dir="ltr">
                <span class="input-icon">📱</span>
            </div>
            <button type="submit" class="submit-btn">
                إرسال كود التحقق
            </button>
        </form>
        <div id="phoneError" class="error-msg"></div>
        
        <!-- رابط للتلغرام -->
        <p class="switch-method">
            <a href="#" onclick="switchToTelegram()">
                الدخول بالتلغرام ←
            </a>
        </p>
    </div>
    
    <!-- الخطوة 2: إدخال الكود -->
    <div id="phoneStep2" class="step">
        <p class="info-msg">تم إرسال الكود إلى <span id="sentPhoneDisplay"></span></p>
        <form id="phoneVerifyForm">
            <input type="text" 
                   id="phoneVerifyCode" 
                   class="code-input"
                   placeholder="000000" 
                   maxlength="6" 
                   pattern="[0-9]{6}"
                   inputmode="numeric"
                   autocomplete="one-time-code"
                   required>
            <button type="submit" class="submit-btn">تأكيد الدخول</button>
        </form>
        <div id="phoneCodeError" class="error-msg"></div>
        
        <!-- زر العودة -->
        <button onclick="goBackPhoneStep()" class="back-btn">
            ← تغيير الرقم
        </button>
    </div>
</div>
```

---

### الخطوة 13: الواجهة - JavaScript

**الملف:** `templates/categories.html`
**المكان:** داخل `<script>` في نهاية الصفحة

```javascript
// ==================== متغيرات الجوال ====================
window.loginPhone = null;
window.currentUserId = null;

// ==================== إرسال كود الجوال ====================
document.getElementById('phoneForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const phone = document.getElementById('loginPhone').value.trim();
    const errorDiv = document.getElementById('phoneError');
    const submitBtn = this.querySelector('button[type="submit"]');
    
    // إخفاء الخطأ السابق
    errorDiv.style.display = 'none';
    
    // التحقق من الرقم
    if (!phone || phone.length < 10) {
        errorDiv.textContent = 'الرجاء إدخال رقم جوال صحيح';
        errorDiv.style.display = 'block';
        return;
    }
    
    // تعطيل الزر
    submitBtn.disabled = true;
    submitBtn.textContent = 'جاري الإرسال...';
    
    try {
        const response = await fetch('/api/auth/send-code-phone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // حفظ البيانات
            window.loginPhone = phone;
            window.currentUserId = data.user_id;
            
            // حفظ في sessionStorage (للحماية من إعادة التحميل)
            sessionStorage.setItem('loginPhone', phone);
            sessionStorage.setItem('currentUserId', data.user_id);
            
            // الانتقال للخطوة 2
            document.getElementById('phoneStep1').classList.remove('active');
            document.getElementById('phoneStep2').classList.add('active');
            document.getElementById('sentPhoneDisplay').textContent = phone;
            document.getElementById('phoneVerifyCode').focus();
        } else {
            errorDiv.textContent = data.message;
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Error:', error);
        errorDiv.textContent = 'خطأ في الاتصال بالسيرفر';
        errorDiv.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'إرسال كود التحقق';
    }
});

// ==================== التحقق من الكود ====================
document.getElementById('phoneVerifyForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const code = document.getElementById('phoneVerifyCode').value.trim();
    const errorDiv = document.getElementById('phoneCodeError');
    const submitBtn = this.querySelector('button[type="submit"]');
    
    errorDiv.style.display = 'none';
    
    if (!code || code.length !== 6) {
        errorDiv.textContent = 'الرجاء إدخال الكود المكون من 6 أرقام';
        errorDiv.style.display = 'block';
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'جاري التحقق...';
    
    try {
        const response = await fetch('/api/auth/login-phone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                phone: window.loginPhone || sessionStorage.getItem('loginPhone'),
                code: code,
                user_id: window.currentUserId || sessionStorage.getItem('currentUserId')
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // مسح البيانات المحفوظة
            window.loginPhone = null;
            window.currentUserId = null;
            sessionStorage.removeItem('loginPhone');
            sessionStorage.removeItem('currentUserId');
            
            // إعادة تحميل الصفحة
            location.reload();
        } else {
            errorDiv.textContent = data.message;
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Error:', error);
        errorDiv.textContent = 'خطأ في الاتصال بالسيرفر';
        errorDiv.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'تأكيد الدخول';
    }
});

// ==================== العودة للخطوة الأولى ====================
function goBackPhoneStep() {
    document.getElementById('phoneStep2').classList.remove('active');
    document.getElementById('phoneStep1').classList.add('active');
    document.getElementById('phoneVerifyCode').value = '';
    document.getElementById('phoneCodeError').style.display = 'none';
}

// ==================== استعادة البيانات عند التحميل ====================
document.addEventListener('DOMContentLoaded', function() {
    // استعادة من sessionStorage إذا وُجدت
    const savedPhone = sessionStorage.getItem('loginPhone');
    const savedUserId = sessionStorage.getItem('currentUserId');
    
    if (savedPhone) {
        window.loginPhone = savedPhone;
        window.currentUserId = savedUserId;
    }
});
```

---

## 🔧 إعداد Render Environment Variables

اذهب إلى **Render Dashboard** → **Environment** وأضف:

| المتغير | الوصف | مثال |
|---------|-------|------|
| `AUTHENTICA_API_KEY` | مفتاح API من Authentica | `$2y$10$XXXX...` |
| `AUTHENTICA_METHOD` | طريقة الإرسال | `whatsapp` أو `sms` |
| `AUTHENTICA_TEMPLATE_ID` | رقم القالب | `1` |

**الحصول على API Key:**
1. اذهب إلى https://portal.authentica.sa
2. سجل دخول أو أنشئ حساب
3. اذهب إلى **Settings** → **API Keys**
4. انسخ المفتاح

---

## 📊 API Endpoints - ملخص

### إرسال كود للجوال
```
POST /api/auth/send-code-phone
Content-Type: application/json

Request:
{
    "phone": "0501234567"
}

Response (نجاح):
{
    "success": true,
    "message": "تم إرسال الكود عبر واتساب",
    "user_id": "123456789"
}
```

### تسجيل الدخول بالجوال
```
POST /api/auth/login-phone
Content-Type: application/json

Request:
{
    "phone": "0501234567",
    "code": "123456",
    "user_id": "123456789"
}

Response (نجاح):
{
    "success": true,
    "message": "تم تسجيل الدخول بنجاح"
}
```

---

## 🗄️ بنية Firebase المطلوبة

```javascript
// Firebase > Firestore > users > {user_id}
{
    "username": "اسم_المستخدم",
    "first_name": "الاسم",
    "phone": "+966501234567",           // ← مطلوب للدخول بالجوال
    "email": "user@example.com",        // للدخول بالإيميل
    "verification_code": "123456",      // الكود (مؤقت)
    "code_time": 1707177600,            // وقت الكود (timestamp)
    "balance": 0.0
}
```

---

## 📁 ملخص الملفات

```
├── config.py                           # إعدادات Authentica
│   └── AUTHENTICA_API_KEY, URL, METHOD, TEMPLATE_ID
│
├── services/
│   └── authentica_service.py           # ← ملف جديد
│       ├── is_authentica_configured()
│       ├── format_phone_number()
│       ├── send_otp_whatsapp()
│       ├── verify_otp_authentica()     # ← مهم للتحقق
│       └── get_authentica_balance()
│
├── routes/auth_routes.py
│   ├── imports Authentica
│   ├── /api/auth/send-code-phone       # ← جديد
│   ├── /api/auth/login-phone           # ← جديد
│   └── /api/auth/login (محسّن)         # ← يدعم الجوال
│
└── templates/categories.html
    ├── phoneSection HTML
    └── JavaScript (send-code, login, sessionStorage)
```

---

## 🔒 الأمان

| الميزة | التفاصيل |
|--------|----------|
| صلاحية الكود | 10 دقائق فقط |
| مسح الكود | بعد الاستخدام الناجح |
| التحقق المزدوج | Authentica API + محلي (fallback) |
| sessionStorage | حماية البيانات من الضياع |
| تنسيق الأرقام | دعم صيغ متعددة (05, +966, 966) |

---

## 🔧 استكشاف الأخطاء

### "Not Verified" في لوحة تحكم Authentica
- **السبب**: لم يتم استدعاء `verify_otp_authentica()`
- **الحل**: تأكد من استخدام `/api/auth/login-phone` وليس التحقق المحلي فقط

### "خدمة الرسائل غير متاحة"
- **السبب**: `AUTHENTICA_API_KEY` غير موجود
- **الحل**: أضفه في Render Environment Variables

### "لا يوجد حساب مرتبط بهذا الرقم"
- **السبب**: الرقم غير موجود في Firebase
- **الحل**: أضف حقل `phone` للمستخدم بالصيغة الصحيحة

### الكود لا يصل عبر WhatsApp
- **السبب**: القالب غير مفعّل أو الرصيد منتهي
- **الحل**: تحقق من لوحة تحكم Authentica

---

## ✅ قائمة التحقق

### الإعدادات:
- [ ] إضافة إعدادات Authentica في `config.py`
- [ ] إنشاء `services/authentica_service.py`

### الـ Routes:
- [ ] إضافة imports Authentica في `auth_routes.py`
- [ ] إضافة `/api/auth/send-code-phone`
- [ ] إضافة `/api/auth/login-phone`
- [ ] تحسين `/api/auth/login`

### الواجهة:
- [ ] إضافة HTML قسم الجوال
- [ ] إضافة JavaScript

### البيئة:
- [ ] إعداد `AUTHENTICA_API_KEY` في Render
- [ ] إضافة حقل `phone` للمستخدمين في Firebase

---

**تاريخ التحديث:** فبراير 2026
