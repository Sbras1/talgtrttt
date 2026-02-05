#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة إرسال البريد الإلكتروني
=============================
إرسال كود التحقق والإشعارات عبر Gmail SMTP
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, SMTP_FROM_NAME

logger = logging.getLogger(__name__)


def is_email_configured():
    """التحقق من إعداد خدمة البريد الإلكتروني"""
    return bool(SMTP_EMAIL and SMTP_PASSWORD)


def send_otp_email(to_email, otp_code, user_name="عميلنا العزيز"):
    """
    إرسال كود التحقق عبر البريد الإلكتروني
    
    Args:
        to_email: بريد المستلم
        otp_code: كود التحقق (6 أرقام)
        user_name: اسم المستخدم
    
    Returns:
        bool: True إذا نجح الإرسال
    """
    if not is_email_configured():
        logger.error("❌ إعدادات البريد الإلكتروني غير مكتملة")
        return False
    
    if not to_email:
        logger.error("❌ لم يتم تحديد بريد المستلم")
        return False

    try:
        # إعداد الرسالة
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = "🔐 كود تسجيل الدخول - TR Store"

        # نص عادي (للعملاء الذين لا يدعمون HTML)
        text_body = f"""
مرحباً {user_name}!

كود التحقق الخاص بك هو: {otp_code}

هذا الكود صالح لمدة 5 دقائق فقط.
لا تشارك هذا الكود مع أي شخص.

إذا لم تطلب هذا الكود، تجاهل هذه الرسالة.

مع تحيات،
فريق TR Store
"""

        # تصميم HTML احترافي
        html_body = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #0a0a0f;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0a0a0f; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 500px; background: linear-gradient(145deg, #12121a 0%, #0d0d12 100%); border-radius: 20px; border: 1px solid rgba(0, 255, 136, 0.15); box-shadow: 0 0 60px rgba(0, 255, 136, 0.08);">
                    
                    <!-- الشعار -->
                    <tr>
                        <td align="center" style="padding: 40px 30px 20px;">
                            <div style="width: 70px; height: 70px; background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%); border-radius: 20px; display: inline-block; text-align: center; line-height: 70px; font-size: 32px; box-shadow: 0 10px 30px rgba(0, 255, 136, 0.3);">
                                🔐
                            </div>
                        </td>
                    </tr>
                    
                    <!-- العنوان -->
                    <tr>
                        <td align="center" style="padding: 0 30px;">
                            <h1 style="color: #ffffff; font-size: 24px; font-weight: 700; margin: 0 0 10px; letter-spacing: 1px;">
                                كود التحقق
                            </h1>
                            <p style="color: #6b7280; font-size: 14px; margin: 0;">
                                مرحباً {user_name} 👋
                            </p>
                        </td>
                    </tr>
                    
                    <!-- الكود -->
                    <tr>
                        <td align="center" style="padding: 30px;">
                            <div style="background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 255, 136, 0.05) 100%); border: 2px solid rgba(0, 255, 136, 0.3); border-radius: 16px; padding: 25px 40px;">
                                <span style="font-size: 42px; font-weight: 800; letter-spacing: 10px; color: #00ff88; text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);">
                                    {otp_code}
                                </span>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- التعليمات -->
                    <tr>
                        <td align="center" style="padding: 0 30px 30px;">
                            <p style="color: #9ca3af; font-size: 13px; line-height: 1.8; margin: 0;">
                                ⏰ هذا الكود صالح لمدة <span style="color: #00ff88; font-weight: 600;">5 دقائق</span> فقط<br>
                                🔒 لا تشارك هذا الكود مع أي شخص
                            </p>
                        </td>
                    </tr>
                    
                    <!-- تحذير -->
                    <tr>
                        <td align="center" style="padding: 0 30px 30px;">
                            <div style="background: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); border-radius: 10px; padding: 15px;">
                                <p style="color: #ffc107; font-size: 12px; margin: 0;">
                                    ⚠️ إذا لم تطلب هذا الكود، تجاهل هذه الرسالة
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- الفوتر -->
                    <tr>
                        <td align="center" style="padding: 20px 30px; border-top: 1px solid rgba(255,255,255,0.05);">
                            <p style="color: #4b5563; font-size: 11px; margin: 0;">
                                TR Store Digital Services<br>
                                <span style="color: #00ff88;">www.tr-store22.com</span>
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

        # إضافة النصين للرسالة
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # الاتصال بسيرفر Gmail وإرسال الرسالة
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # تفعيل التشفير
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"✅ تم إرسال كود التحقق بنجاح إلى {to_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ خطأ في المصادقة - تأكد من App Password: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ خطأ SMTP: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع في إرسال الإيميل: {e}")
        return False


def send_notification_email(to_email, subject, message, user_name=""):
    """
    إرسال إشعار عام عبر البريد الإلكتروني
    
    Args:
        to_email: بريد المستلم
        subject: موضوع الرسالة
        message: نص الرسالة
        user_name: اسم المستخدم (اختياري)
    
    Returns:
        bool: True إذا نجح الإرسال
    """
    if not is_email_configured():
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject

        html_body = f"""
<!DOCTYPE html>
<html dir="rtl">
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
    <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h2 style="color: #333; text-align: center;">🏪 TR Store</h2>
        {f'<p style="color: #666;">مرحباً {user_name}،</p>' if user_name else ''}
        <div style="color: #333; line-height: 1.8;">
            {message}
        </div>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="text-align: center; color: #999; font-size: 12px;">
            TR Store Digital Services
        </p>
    </div>
</body>
</html>
"""
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        return True

    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الإشعار: {e}")
        return False
