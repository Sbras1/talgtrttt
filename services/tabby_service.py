#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة تابي (Tabby) للدفع بالتقسيط
================================
اشتري الآن وادفع لاحقاً
يدعم: السعودية (SAR) والإمارات (AED)
"""

import requests
import time
import hashlib
from config import (
    TABBY_SA_PK, TABBY_SA_SK, TABBY_SA_MERCHANT_CODE,
    TABBY_AE_PK, TABBY_AE_SK, TABBY_AE_MERCHANT_CODE,
    TABBY_PK, TABBY_SK, TABBY_MERCHANT_CODE,
    TABBY_API_URL, SITE_URL
)

# الحد الأدنى والأقصى لتابي
TABBY_MIN_AMOUNT = 100  # ريال/درهم
TABBY_MAX_AMOUNT = 5000  # ريال/درهم

# إعدادات البلدان
TABBY_COUNTRIES = {
    'SA': {
        'pk': TABBY_SA_PK,
        'sk': TABBY_SA_SK,
        'merchant_code': TABBY_SA_MERCHANT_CODE,
        'currency': 'SAR',
        'phone_code': '+966',
        'name': 'السعودية'
    },
    'AE': {
        'pk': TABBY_AE_PK,
        'sk': TABBY_AE_SK,
        'merchant_code': TABBY_AE_MERCHANT_CODE,
        'currency': 'AED',
        'phone_code': '+971',
        'name': 'الإمارات'
    }
}


def is_tabby_configured(country='SA'):
    """التحقق من إعداد مفاتيح تابي لبلد معين"""
    if country in TABBY_COUNTRIES:
        config = TABBY_COUNTRIES[country]
        return bool(config['sk'] and config['merchant_code'])
    # للتوافق القديم
    return bool(TABBY_SK and TABBY_MERCHANT_CODE)


def get_available_countries():
    """الحصول على البلدان المتاحة لتابي"""
    available = []
    for code, config in TABBY_COUNTRIES.items():
        if config['sk'] and config['merchant_code']:
            available.append({
                'code': code,
                'name': config['name'],
                'currency': config['currency']
            })
    return available


def is_amount_eligible(amount):
    """التحقق من أن المبلغ مؤهل لتابي"""
    return TABBY_MIN_AMOUNT <= float(amount) <= TABBY_MAX_AMOUNT


def create_tabby_session(order_id, amount, customer_phone, customer_name="عميل", customer_email=None, description="شحن رصيد", country='SA'):
    """
    إنشاء جلسة دفع تابي
    
    Args:
        order_id: معرف الطلب
        amount: المبلغ (يجب أن يكون بين 100-5000)
        customer_phone: رقم الجوال
        customer_name: اسم العميل
        customer_email: البريد الإلكتروني (اختياري)
        description: وصف الطلب
        country: البلد ('SA' للسعودية أو 'AE' للإمارات)
        
    Returns:
        dict: نتيجة الإنشاء تحتوي على redirect_url أو خطأ
    """
    
    # الحصول على إعدادات البلد
    if country in TABBY_COUNTRIES:
        config = TABBY_COUNTRIES[country]
        sk = config['sk']
        merchant_code = config['merchant_code']
        currency = config['currency']
        phone_code = config['phone_code']
    else:
        # افتراضي: السعودية
        sk = TABBY_SK
        merchant_code = TABBY_MERCHANT_CODE
        currency = 'SAR'
        phone_code = '+966'
    
    if not sk or not merchant_code:
        return {
            'success': False,
            'error': f'تابي {TABBY_COUNTRIES.get(country, {}).get("name", country)} غير مُعد. يرجى إضافة المفاتيح.'
        }
    
    if not is_amount_eligible(amount):
        currency_name = 'ريال' if currency == 'SAR' else 'درهم'
        return {
            'success': False,
            'error': f'المبلغ يجب أن يكون بين {TABBY_MIN_AMOUNT} و {TABBY_MAX_AMOUNT} {currency_name}'
        }
    
    # تنسيق رقم الجوال
    phone = str(customer_phone).strip()
    if phone.startswith('0'):
        phone = phone_code + phone[1:]
    elif phone.startswith('5') and len(phone) == 9:
        phone = phone_code + phone
    elif not phone.startswith('+'):
        phone = phone_code + phone
    
    # تنسيق البريد الإلكتروني - يجب أن يكون صحيحاً لتابي
    if not customer_email or '@temp' in str(customer_email):
        # استخدام بريد افتراضي بناءً على رقم الجوال
        phone_digits = ''.join(filter(str.isdigit, phone))[-9:]  # آخر 9 أرقام
        customer_email = f"customer{phone_digits}@gmail.com"
    
    headers = {
        "Authorization": f"Bearer {sk}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "payment": {
            "amount": str(amount),
            "currency": currency,
            "description": description,
            "buyer": {
                "phone": phone,
                "name": customer_name,
                "email": customer_email
            },
            "buyer_history": {
                "registered_since": "2024-01-01T00:00:00Z",
                "loyalty_level": 0
            },
            "order": {
                "reference_id": order_id,
                "items": [{
                    "title": description,
                    "description": f"طلب رقم {order_id}",
                    "quantity": 1,
                    "unit_price": str(amount),
                    "category": "Digital Services"
                }]
            },
            "order_history": []
        },
        "lang": "ar",
        "merchant_code": merchant_code,
        "merchant_urls": {
            "success": f"{SITE_URL}/tabby/success?order_id={order_id}",
            "cancel": f"{SITE_URL}/tabby/cancel?order_id={order_id}",
            "failure": f"{SITE_URL}/tabby/failure?order_id={order_id}"
        }
    }
    
    try:
        print(f"📤 Tabby Request: order_id={order_id}, amount={amount}")
        response = requests.post(TABBY_API_URL, json=payload, headers=headers, timeout=30)
        result = response.json()
        print(f"📥 Tabby Response: {response.status_code} - {result}")
        
        if response.status_code == 200:
            # جلسة ناجحة
            checkout_url = None
            
            # البحث عن رابط الدفع
            if 'configuration' in result and 'available_products' in result['configuration']:
                products = result['configuration']['available_products']
                if 'installments' in products and len(products['installments']) > 0:
                    checkout_url = products['installments'][0].get('web_url')
            
            if not checkout_url and 'payment' in result:
                checkout_url = result.get('payment', {}).get('checkout_url')
            
            if checkout_url:
                return {
                    'success': True,
                    'checkout_url': checkout_url,
                    'session_id': result.get('id'),
                    'payment_id': result.get('payment', {}).get('id'),
                    'expires_at': time.time() + 1800  # 30 دقيقة
                }
            else:
                # تابي رفضت العميل
                rejection_reason = "غير مؤهل للدفع بالتقسيط"
                if 'rejection_reason' in result:
                    rejection_reason = result['rejection_reason']
                
                return {
                    'success': False,
                    'error': rejection_reason,
                    'rejected': True
                }
        else:
            error_msg = result.get('error', {}).get('message', 'خطأ غير معروف')
            return {
                'success': False,
                'error': error_msg
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'انتهت مهلة الاتصال بتابي'
        }
    except Exception as e:
        print(f"❌ Tabby Error: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def verify_tabby_webhook(data, signature=None):
    """
    التحقق من صحة webhook من تابي
    
    Args:
        data: بيانات الـ webhook
        signature: التوقيع (اختياري)
        
    Returns:
        bool: صحة البيانات
    """
    # تابي ترسل payment_id و status
    if not data:
        return False
    
    required_fields = ['id', 'status']
    return all(field in data for field in required_fields)


def get_payment_status(payment_id):
    """
    جلب حالة دفعة من تابي
    
    Args:
        payment_id: معرف الدفعة
        
    Returns:
        dict: حالة الدفعة
    """
    if not is_tabby_configured():
        return None
    
    headers = {
        "Authorization": f"Bearer {TABBY_SK}",
        "Accept": "application/json"
    }
    
    url = f"https://api.tabby.ai/api/v2/payments/{payment_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"❌ Tabby Status Error: {e}")
        return None


def capture_payment(payment_id, amount):
    """
    تأكيد (Capture) الدفعة بعد نجاحها
    
    Args:
        payment_id: معرف الدفعة
        amount: المبلغ
        
    Returns:
        dict: نتيجة التأكيد
    """
    if not is_tabby_configured():
        return {'success': False, 'error': 'تابي غير مُعد'}
    
    headers = {
        "Authorization": f"Bearer {TABBY_SK}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.tabby.ai/api/v2/payments/{payment_id}/captures"
    
    payload = {
        "amount": str(amount)
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        result = response.json()
        
        if response.status_code in [200, 201]:
            return {'success': True, 'data': result}
        else:
            return {'success': False, 'error': result.get('error', {}).get('message', 'فشل التأكيد')}
    except Exception as e:
        print(f"❌ Tabby Capture Error: {e}")
        return {'success': False, 'error': str(e)}


def refund_payment(payment_id, amount):
    """
    استرداد دفعة
    
    Args:
        payment_id: معرف الدفعة
        amount: المبلغ المراد استرداده
        
    Returns:
        dict: نتيجة الاسترداد
    """
    if not is_tabby_configured():
        return {'success': False, 'error': 'تابي غير مُعد'}
    
    headers = {
        "Authorization": f"Bearer {TABBY_SK}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.tabby.ai/api/v2/payments/{payment_id}/refunds"
    
    payload = {
        "amount": str(amount)
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        result = response.json()
        
        if response.status_code in [200, 201]:
            return {'success': True, 'data': result}
        else:
            return {'success': False, 'error': result.get('error', {}).get('message', 'فشل الاسترداد')}
    except Exception as e:
        print(f"❌ Tabby Refund Error: {e}")
        return {'success': False, 'error': str(e)}
