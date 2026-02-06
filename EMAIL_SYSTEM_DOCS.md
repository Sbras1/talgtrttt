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

| المتغير | القيمة | مثال |
|---------|--------|------|
| `SMTP_SERVER` | سيرفر البريد | `mail.privateemail.com` |
| `SMTP_PORT` | المنفذ | `465` |
| `SMTP_EMAIL` | إيميل المرسل | `tr@gamerstr1.com` |
| `SMTP_PASSWORD` | كلمة المرور | `yourpassword123` |

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

## 📁 الملفات المتعلقة

```
├── config.py                    # إعدادات SMTP
├── routes/auth_routes.py        # API endpoints + إرسال الإيميل
└── templates/categories.html    # واجهة المستخدم
```

---

**تاريخ التحديث:** فبراير 2026
