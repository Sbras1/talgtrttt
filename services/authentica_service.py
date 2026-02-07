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


def is_authentica_configured():
    """التحقق من إعداد خدمة Authentica"""
    return bool(AUTHENTICA_API_KEY)


def format_phone_number(phone):
    """
    تنسيق رقم الجوال للصيغة الدولية
    
    Args:
        phone: رقم الجوال (05xxxxxxxx أو +966xxxxxxxx)
    
    Returns:
        str: الرقم بالصيغة الدولية (+966xxxxxxxxx)
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


def send_otp_whatsapp(phone, otp_code=None, method=None):
    """
    إرسال كود OTP عبر WhatsApp أو SMS
    
    Args:
        phone: رقم الجوال
        otp_code: كود OTP مخصص (اختياري - سيولد تلقائياً إذا لم يحدد)
        method: طريقة الإرسال (whatsapp, sms) - افتراضي من الإعدادات
    
    Returns:
        dict: {'success': bool, 'message': str, 'otp': str}
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


def verify_otp_authentica(phone, otp_code):
    """
    التحقق من كود OTP عبر Authentica API
    
    Args:
        phone: رقم الجوال
        otp_code: الكود المدخل من المستخدم
    
    Returns:
        dict: {'success': bool, 'message': str}
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


def get_authentica_balance():
    """
    الاستعلام عن رصيد Authentica
    
    Returns:
        dict: {'success': bool, 'balance': int, 'message': str}
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
